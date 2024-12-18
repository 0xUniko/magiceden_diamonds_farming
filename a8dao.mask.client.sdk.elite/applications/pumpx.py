import json
from decimal import Decimal
from math import ceil
from typing import Literal, TypedDict

import httpx

from api.local.web3.eth_erc20 import (
    send_raw_transaction,
    send_transaction,
    signature,
    signature_text,
    to_checksum_address,
)
from model import ChainId
from tools.logger import task_log


class Offer(TypedDict):
    id: int
    hash: str
    nonce: int
    loan_amount: int
    owner: str
    collateral_contract: str
    currency: str
    supply_cap: str
    supply_used: str
    single_cap: str
    max_collateral_factor: int
    max_tenor: int
    max_interest_rate: int
    tenor_multiplier: int
    collateral_factor_multiplier: int
    created_at: int
    updated_at: int


class Offer2(Offer):
    owner_weth_allowance: str
    owner_weth_balance: str
    loan_count: int


class AcceptOfferRequest(TypedDict):
    orderID: int
    nonce: int
    loanAmount: int
    downPayment: int
    collateralFactor: int
    tokenID: int
    eachPayment: int
    offerIR: int
    tenor: int
    offerHash: str
    currency: str
    borrower: str
    lender: str
    collateralContract: str
    numberOfInstallments: int
    offerSide: int
    isCreditSale: bool
    protocolFeeRate: int


class Pumpx:
    auth_token = None
    address = None
    private_key = None

    def __init__(self, task_id: str):
        self.task_id = task_id

    def auth(self, address: str, private_key: str):
        login_message = httpx.post(
            "https://lending.pumpx.io/lending/api/v1/auth/challenge",
            json={"address": address},
        ).json()["login_message"]
        sig_res = signature_text(ChainId.ETH_ETHEREUM, private_key, login_message)
        assert sig_res["code"] == 0, f'sig failed: {sig_res["message"]}'
        auth_token = httpx.post(
            "https://lending.pumpx.io/lending/api/v1/auth/login",
            json={
                "address": address,
                "message": login_message,
                "signature": sig_res["data"],  # type: ignore
            },
        ).json()["token"]
        self.auth_token = auth_token
        task_log(self.task_id, "login success")
        self.address = address
        self.private_key = private_key

    def offer(
        self,
        collateral_contract: str,
        supply_cap: int,
        single_cap: int,
        max_collateral_factor: int,
        max_tenor: int,
        max_interest_rate: int,
        tenor_multiplier: int,
        collateral_factor_multiplier: int,
        offer_type: Literal["create"] | Literal["update"] = "create",
    ) -> Offer:
        task_log(self.task_id, "give offer")
        assert self.auth_token is not None, "must login before creating a new offer"
        assert self.address is not None
        assert self.private_key is not None

        typed_data = httpx.get(
            "https://lending.pumpx.io/lending/api/v1/pools/typed-data",
            headers={"authorization": f"Bearer {self.auth_token}"},
            params={
                "owner": self.address,
                "currency": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "collateral_contract": collateral_contract,
                "supply_cap": supply_cap,
                "single_cap": single_cap,
                "max_collateral_factor": max_collateral_factor,
                "max_tenor": max_tenor,
                "max_interest_rate": max_interest_rate,
                "tenor_multiplier": tenor_multiplier,
                "collateral_factor_multiplier": collateral_factor_multiplier,
            },
        ).json()
        task_log(self.task_id, f"get typed_data: {str(typed_data)}")

        sig_res = signature(
            ChainId.ETH_ETHEREUM,
            self.private_key,
            {
                "types": typed_data["types"],
                "primaryType": typed_data["primaryType"],
                "domain": {
                    **typed_data["domain"],
                    "chainId": int(typed_data["domain"]["chainId"], 16),
                },
                "message": {
                    "collateralContract": typed_data["message"]["collateralContract"],
                    "collateralFactorMultiplier": int(
                        typed_data["message"]["collateralFactorMultiplier"]
                    ),
                    "currency": typed_data["message"]["currency"],
                    "maxCollateralFactor": int(
                        typed_data["message"]["maxCollateralFactor"]
                    ),
                    "maxInterestRate": int(typed_data["message"]["maxInterestRate"]),
                    "maxTenor": int(typed_data["message"]["maxTenor"]),
                    "nonce": int(typed_data["message"]["nonce"]),
                    "owner": typed_data["message"]["owner"],
                    "singleCap": int(typed_data["message"]["singleCap"]),
                    "supplyCap": int(typed_data["message"]["supplyCap"]),
                    "tenorMultiplier": int(typed_data["message"]["tenorMultiplier"]),
                },
            },
        )
        assert sig_res["code"] == 0, f'failed to get signature: {sig_res["message"]}'
        task_log(self.task_id, "sign typed_data successfully")

        data = {
            "signature": sig_res["data"],
            "typed_data": json.dumps(typed_data),
        }

        if offer_type == "create":
            task_log(self.task_id, "creating offer...")
            res = httpx.post(
                "https://lending.pumpx.io/lending/api/v1/pools",
                headers={"authorization": f"Bearer {self.auth_token}"},
                json=data,
            ).json()
        else:
            task_log(self.task_id, "puting offer...")
            res = httpx.put(
                "https://lending.pumpx.io/lending/api/v1/pools",
                headers={"authorization": f"Bearer {self.auth_token}"},
                json=data,
            ).json()
        assert (
            "error" not in res
        ), f"failed to {offer_type} offer: {res['error']['message']}"
        task_log(self.task_id, f"{offer_type} offer successfully: {str(res)}")
        return res

    def set_weth_allowance(self, private_key: str, allowance: int = int("f" * 64, 16)):
        res = send_raw_transaction(
            ChainId.ETH_ETHEREUM,
            private_key,
            "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "approve(address,uint256)",
            ["0x9267CFF7720439457D16679C839F62984017672E", allowance],
        )
        assert res["code"] == 0, f"failed to set weth allowance: {res['message']}"
        task_log(self.task_id, "set weth successfully")
        return res["data"]

    def query_collection_info_list(self, collection_list: list[str]):
        return httpx.post(
            "https://pumpx.io/lending/query",
            json={
                "operationName": "NftCollectionsByContractAddresses",
                "variables": {"assetContractAddresses": collection_list},
                "query": "query NftCollectionsByContractAddresses($assetContractAddresses: [String!]!) {\n  nftCollectionsByContractAddresses(\n    assetContractAddresses: $assetContractAddresses\n  ) {\n    contractAddress\n    nftCollection {\n      assetsCount\n      description\n      featuredImageUrl\n      fees {\n        address\n        name\n        value\n        __typename\n      }\n      id\n      instagramUsername\n      mediumUsername\n      discordUrl\n      externalUrl\n      twitterUsername\n      telegramUrl\n      imagePreviewUrl\n      imageThumbnailUrl\n      imageUrl\n      largeImageUrl\n      name\n      nftCollectionStat {\n        averagePrice\n        count\n        createdAt\n        floorPrice\n        floorPriceRate\n        id\n        oneDayAveragePrice\n        oneDayChange\n        totalSales\n        totalSupply\n        totalVolume\n        volumeOneWeekAmount\n        volumeOneWeekUnit\n        floorPriceOneWeekAmount\n        floorPriceOneWeekUnit\n        numberOwners\n        __typename\n      }\n      safelistRequestStatus\n      shortDescription\n      slug\n      isCreatorFeesEnforced\n      totalListed\n      __typename\n    }\n    __typename\n  }\n}",
            },
        ).json()["data"]["nftCollectionsByContractAddresses"]

    def get_floor_price(self, slug: str) -> str:
        return str(
            httpx.get(
                f"https://pumpx.io/api/v1/xbn/marketFloorPrice?slug={slug}"
            ).json()["floor_price"]
        )

    def get_offer_list(self, collateral_contract: str) -> list[Offer2]:
        return httpx.get(
            f"https://lending.pumpx.io/lending/api/v1/pools?collateral_contract={collateral_contract}"
        ).json()

    def get_valid_offer_list(
        self,
        collateral_contract: str,
        collateral_factor: (
            Literal["1000"]
            | Literal["2000"]
            | Literal["3000"]
            | Literal["4000"]
            | Literal["5000"]
            | Literal["6000"]
            | Literal["7000"]
            | Literal["8000"]
            | Literal["9000"]
        ),
        order_price: int,
    ):
        offer_list = self.get_offer_list(collateral_contract)
        return [
            offer
            for offer in offer_list
            if min(
                int(offer["owner_weth_allowance"]),
                int(offer["owner_weth_balance"]),
                int(offer["single_cap"]),
                int(offer["supply_cap"]) - int(offer["supply_used"]),
            )
            >= order_price * int(collateral_factor) / 10000
            and offer["owner"].lower()
            != (self.address.lower() if self.address is not None else "")
        ]

    def get_asset_info(self, asset_contract: str, token_id: int):
        task_log(self.task_id, "get asset info")
        return httpx.post(
            "https://pumpx.io/lending/query",
            json={
                "operationName": "Asset",
                "variables": {
                    "assetContractAddress": asset_contract,
                    "assetTokenId": str(token_id),
                },
                "query": "query Asset($assetId: ID, $assetContractAddress: String, $assetTokenId: String) {\n  asset(\n    id: $assetId\n    assetContractAddress: $assetContractAddress\n    assetTokenID: $assetTokenId\n  ) {\n    id\n    assetContractAddress\n    tokenID\n       name\n    owner\n    orderChain\n    orderCoin\n    orderPrice\n    orderPriceMarket\n    __typename\n  }\n}",
            },
        ).json()["data"]["asset"]

    def get_nft_collection_assets(self, nft_address: str):
        task_log(self.task_id, "get nft collection assets")
        collection_id = httpx.post(
            "https://pumpx.io/lending/query",
            json={
                "operationName": "NftCollectionsByContractAddresses",
                "variables": {"assetContractAddresses": [nft_address.lower()]},
                "query": "query NftCollectionsByContractAddresses($assetContractAddresses: [String!]!) {\n  nftCollectionsByContractAddresses(\n    assetContractAddresses: $assetContractAddresses\n  ) {\n    contractAddress\n    nftCollection {\n      assetsCount\n      description\n      featuredImageUrl\n      fees {\n        address\n        name\n        value\n        __typename\n      }\n      id\n      instagramUsername\n      mediumUsername\n      discordUrl\n      externalUrl\n      twitterUsername\n      telegramUrl\n      imagePreviewUrl\n      imageThumbnailUrl\n      imageUrl\n      largeImageUrl\n      name\n      nftCollectionStat {\n        averagePrice\n        count\n        createdAt\n        floorPrice\n        floorPriceRate\n        id\n        oneDayAveragePrice\n        oneDayChange\n        totalSales\n        totalSupply\n        totalVolume\n        volumeOneWeekAmount\n        volumeOneWeekUnit\n        floorPriceOneWeekAmount\n        floorPriceOneWeekUnit\n        numberOwners\n        __typename\n      }\n      safelistRequestStatus\n      shortDescription\n      slug\n      isCreatorFeesEnforced\n      totalListed\n      __typename\n    }\n    __typename\n  }\n}",
            },
        ).json()["data"]["nftCollectionsByContractAddresses"][0]["nftCollection"]["id"]
        return httpx.post(
            "https://pumpx.io/lending/query",
            json={
                "operationName": "NftCollectionAssets",
                "variables": {
                    "collectionId": collection_id,
                    "orderBy": {"direction": "ASC", "field": "PRICE"},
                    "where": {"status": ["BUY_NOW"]},
                    "first": 24,
                },
                "query": "query NftCollectionAssets($collectionId: ID!, $orderBy: NFTAssetOrderBy!, $first: Int, $after: Cursor, $where: NFTAssetWhere) {\n  nftCollectionAssets(\n    collectionID: $collectionId\n    orderBy: $orderBy\n    first: $first\n    after: $after\n    where: $where\n  ) {\n    edges {\n      node {\n        id\n        assetContractAddress\n        tokenID\n        imageUrl\n        imagePreviewUrl\n        imageThumbnailUrl\n        imageOriginalUrl\n        animationUrl\n        animationOriginalUrl\n        backgroundColor\n        name\n        owner\n        orderPrice\n        nftAssetContract {\n          id\n          address\n          name\n          totalSupply\n          imageUrl\n          __typename\n        }\n        orderPriceMarket\n        __typename\n      }\n      cursor\n      __typename\n    }\n    pageInfo {\n      hasNextPage\n      endCursor\n      __typename\n    }\n    totalCount\n    __typename\n  }\n}",
            },
        ).json()["data"]["nftCollectionAssets"]["edges"]

    def get_loans(self):
        task_log(self.task_id, "get loans")
        assert self.auth_token is not None, "must login"
        assert self.address is not None
        assert self.private_key is not None
        # status: 1 is open
        return httpx.get(
            f"https://lending.pumpx.io/lending/api/v1/loans?borrower={self.address}&includes_collection=true&includes_nft=true",
            headers={"authorization": f"Bearer {self.auth_token}"},
        ).json()

    def get_repaymentplans(self):
        task_log(self.task_id, "get repaymentplans")
        assert self.auth_token is not None, "must login"
        assert self.address is not None
        assert self.private_key is not None
        return httpx.get(
            "https://lending.pumpx.io/lending/api/v1/loan/70/repaymentplans",
            headers={"authorization": f"Bearer {self.auth_token}"},
        ).json()

    def get_accept_offer_request(
        self,
        collateral_contract: str,
        token_id: int,
        collateral_factor: (
            Literal["1000"]
            | Literal["2000"]
            | Literal["3000"]
            | Literal["4000"]
            | Literal["5000"]
            | Literal["6000"]
            | Literal["7000"]
            | Literal["8000"]
            | Literal["9000"]
        ),
        tenor: (
            Literal["1"]
            | Literal["3"]
            | Literal["7"]
            | Literal["14"]
            | Literal["30"]
            | Literal["60"]
            | Literal["90"]
        ),
        offer_hash: str,
        borrower: str,
        lender: str,
        number_of_installments: int,
        tenor_multiplier: int,
        max_tenor: int,
        collateral_factor_multiplier: int,
        max_interest_rate: int,
        max_collateral_factor: int,
    ) -> AcceptOfferRequest:
        asset = self.get_asset_info(collateral_contract, token_id)
        order_price = Decimal(asset["orderPrice"])

        tenor_list = [
            "1",
            "3",
            "7",
            "14",
            "30",
            "60",
            "90",
        ]

        offer_ir: int = ceil(
            max_interest_rate
            * (tenor_multiplier / 10000)
            ** (
                tenor_list.index(str(int(max_tenor / 3600 / 24)))
                - tenor_list.index(tenor)
            )
            * (collateral_factor_multiplier / 10000)
            ** ((max_collateral_factor - int(collateral_factor)) / 1000)
        )

        loan_amount = order_price * int(collateral_factor) / 10000

        if offer_ir == 0:
            each_payment = loan_amount / number_of_installments
        else:
            installment = Decimal(tenor) / number_of_installments
            i = Decimal(offer_ir) / 10000 / 365 * installment
            n = int(Decimal(tenor) / installment)
            iPlus1powN = (i + 1) ** n
            each_payment = iPlus1powN * i / (iPlus1powN - 1) * loan_amount

        return {
            "orderID": 0,
            "nonce": 0,
            "loanAmount": int(loan_amount * 10**18),
            "downPayment": int(order_price * 10**18 - loan_amount * 10**18),
            "collateralFactor": int(collateral_factor),
            "tokenID": token_id,
            "eachPayment": ceil(each_payment * 10**18),
            "offerIR": offer_ir,
            "tenor": int(tenor) * 3600 * 24,
            "offerHash": offer_hash,
            "currency": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
            "borrower": borrower,
            "lender": lender,
            "collateralContract": collateral_contract,
            "numberOfInstallments": number_of_installments,
            "offerSide": 2,
            "isCreditSale": False,
            "protocolFeeRate": 50,
        }

    def buy(self, accept_offer_request: AcceptOfferRequest):
        task_log(self.task_id, "buy")
        assert self.auth_token is not None, "must login before creating a new offer"
        assert self.address is not None
        assert self.private_key is not None

        slug: str = self.query_collection_info_list(
            [accept_offer_request["collateralContract"]]
        )[0]["nftCollection"]["slug"]
        floor_price = self.get_floor_price(slug)
        task_log(self.task_id, f"floor_price: {floor_price}")

        # marketplace = self.get_asset_info(
        #     accept_offer_request["collateralContract"],
        #     int(accept_offer_request["tokenID"]),
        # )["orderPriceMarket"].lower()
        markets = httpx.get(
            "https://pumpx.io/api/v1/nft/price",
            params={
                "contract_address": accept_offer_request["collateralContract"],
                "token_id": accept_offer_request["tokenID"],
            },
        ).json()["data"]
        market_prices = [
            market[market["marketplace"].lower() + "_price"] for market in markets
        ]
        assert all(
            p["unit"] == "ETH" for p in market_prices
        ), "all nft should be priced in ETH"
        price_amounts = [p["amount"] for p in market_prices]
        marketplace = markets[price_amounts.index(min(price_amounts))][
            "marketplace"
        ].lower()
        task_log(self.task_id, f"marketplace: {marketplace}")

        typed_data: dict = {
            "types": {
                "EIP712Domain": [
                    {"name": "name", "type": "string"},
                    {"name": "version", "type": "string"},
                    {"name": "chainId", "type": "uint256"},
                    {"name": "verifyingContract", "type": "address"},
                ],
                "AcceptOfferRequest": [
                    {"name": "orderID", "type": "uint256"},
                    {"name": "loanAmount", "type": "uint256"},
                    {"name": "nonce", "type": "uint256"},
                    {"name": "downPayment", "type": "uint256"},
                    {"name": "collateralFactor", "type": "uint256"},
                    {"name": "tokenID", "type": "uint256"},
                    {"name": "eachPayment", "type": "uint256"},
                    {"name": "currency", "type": "address"},
                    {"name": "borrower", "type": "address"},
                    {"name": "lender", "type": "address"},
                    {"name": "collateralContract", "type": "address"},
                    {"name": "offerIR", "type": "uint32"},
                    {"name": "tenor", "type": "uint32"},
                    {"name": "offerHash", "type": "bytes32"},
                    {"name": "protocolFeeRate", "type": "uint16"},
                    {"name": "numberOfInstallments", "type": "uint8"},
                    {"name": "offerSide", "type": "uint8"},
                    {"name": "isCreditSale", "type": "bool"},
                ],
            },
            "primaryType": "AcceptOfferRequest",
            "domain": {
                "name": "xBank",
                "version": "1.0",
                "chainId": 1,
                "verifyingContract": "0x9267Cff7720439457D16679C839f62984017672e",
            },
            "message": accept_offer_request,
        }

        sig_res = signature(ChainId.ETH_ETHEREUM, self.private_key, typed_data)
        assert sig_res["code"] == 0, f"get signature failed: {sig_res['message']}"
        task_log(self.task_id, f"signature: {sig_res['data']}")

        typed_data["message"] = {**accept_offer_request}
        typed_data["message"]["orderID"] = str(accept_offer_request["orderID"])
        typed_data["message"]["nonce"] = str(accept_offer_request["nonce"])
        typed_data["message"]["loanAmount"] = str(accept_offer_request["loanAmount"])
        typed_data["message"]["downPayment"] = str(accept_offer_request["downPayment"])
        typed_data["message"]["collateralFactor"] = str(
            accept_offer_request["collateralFactor"]
        )
        typed_data["message"]["tokenID"] = str(accept_offer_request["tokenID"])
        typed_data["message"]["eachPayment"] = str(accept_offer_request["eachPayment"])

        offer_res = httpx.post(
            "https://lending.pumpx.io/lending/api/v1/offers",
            headers={"authorization": f"Bearer {self.auth_token}"},
            json={
                "collateral_price": str(
                    accept_offer_request["loanAmount"]
                    + accept_offer_request["downPayment"]
                ),
                "floor_price": str(int(Decimal(floor_price) * 10**18)),
                "marketplace": marketplace,
                "signature": sig_res["data"],
                "typed_data": json.dumps(typed_data),
            },
        ).json()
        assert "error" not in offer_res, offer_res["error"]["message"]
        accept_offer_request_res = offer_res["accept_offer_request"]

        with open("./src/applications/abi/xbank.json", "r") as f:
            abi = json.load(f)

        checksum_collateral_contract_address_res = to_checksum_address(
            accept_offer_request_res["collateralContract"]
        )
        assert (
            checksum_collateral_contract_address_res["code"] == 0
        ), f"failed to  get checksum address: {checksum_collateral_contract_address_res['message']}"
        checksum_currency_address_res = to_checksum_address(
            accept_offer_request_res["currency"]
        )
        assert (
            checksum_currency_address_res["code"] == 0
        ), f"failed to  get checksum address: {checksum_currency_address_res['message']}"
        checksum_borrower_address_res = to_checksum_address(
            accept_offer_request_res["borrower"]
        )
        assert (
            checksum_borrower_address_res["code"] == 0
        ), f"failed to  get checksum address: {checksum_borrower_address_res['message']}"
        checksum_lender_address_res = to_checksum_address(
            accept_offer_request_res["lender"]
        )
        assert (
            checksum_lender_address_res["code"] == 0
        ), f"failed to  get checksum address: {checksum_lender_address_res['message']}"

        res = send_transaction(
            ChainId.ETH_ETHEREUM,
            self.private_key,
            "0x9267Cff7720439457D16679C839f62984017672e",
            abi=abi,
            value=int(accept_offer_request_res["downPayment"])
            + int(accept_offer_request_res["loanAmount"])
            * accept_offer_request_res["protocolFeeRate"]
            / 10000,
            contract_data={
                "function_name": "prepareLoan",
                "function_args": [
                    (
                        int(accept_offer_request_res["orderID"]),
                        int(accept_offer_request_res["nonce"]),
                        int(accept_offer_request_res["loanAmount"]),
                        int(accept_offer_request_res["downPayment"]),
                        int(accept_offer_request_res["collateralFactor"]),
                        int(accept_offer_request_res["tokenID"]),
                        int(accept_offer_request_res["eachPayment"]),
                        checksum_currency_address_res["data"],
                        checksum_borrower_address_res["data"],
                        checksum_lender_address_res["data"],
                        checksum_collateral_contract_address_res["data"],
                        accept_offer_request_res["offerIR"],
                        accept_offer_request_res["tenor"],
                        accept_offer_request_res["offerHash"],
                        accept_offer_request_res["protocolFeeRate"],
                        accept_offer_request_res["numberOfInstallments"],
                        accept_offer_request_res["offerSide"],
                        accept_offer_request_res["isCreditSale"],
                    ),
                    offer_res["server_sig"],
                ],
            },
        )

        assert res["code"] == 0, f"failed to buy: {res['message']}"
        task_log(self.task_id, f"buy successfully, tx hash: {res['data']['tx_hash']}")
        task_log(
            self.task_id,
            f'token id: {accept_offer_request["tokenID"]}, order id: {accept_offer_request_res["orderID"]}',
        )
        return res["data"]

    def pay_loan(
        self,
        collateral_contract: str,
        token_id: int,
        pay_type: Literal["repay"] | Literal["payoff"] = "repay",
    ):
        task_log(self.task_id, "pay loan")
        assert self.auth_token is not None, "must login before repay loan"
        assert self.address is not None
        assert self.private_key is not None

        loan_res = httpx.get(
            "https://lending.pumpx.io/lending/api/v1/loans",
            headers={"authorization": f"Bearer {self.auth_token}"},
            params={"borrower": self.address},
        ).json()
        loans = [
            l
            for l in loan_res
            if l["collateral_contract"].lower() == collateral_contract.lower()
            and int(l["token_id"]) == token_id
            and l["status"] == 1
        ]
        assert len(loans) == 1, "failed to find the load"
        loan = loans[0]

        if pay_type == "repay":
            func_sig = "repayLoan(uint256)"
            value = loan["each_payment"]
        else:
            func_sig = "payoffLoan(uint256)"
            value = loan["outstanding_principal"]

        res = send_raw_transaction(
            ChainId.ETH_ETHEREUM,
            self.private_key,
            "0x9267Cff7720439457D16679C839f62984017672e",
            func_sig,
            [loan["loan_id"]],
            value,
        )
        assert res["code"] == 0, f"failed to pay: {res['message']}"
        task_log(self.task_id, f"pay successfully: {res['data']}")
        return res["data"]

    def collateral_listing(
        self,
        contract_address: str,
        token_id: int,
        platform: Literal["blur"] | Literal["opensea"],
        expiration_time: int,
        price: int,
    ):
        assert self.auth_token is not None, "must login"
        assert self.address is not None
        assert self.private_key is not None

        if contract_address.lower() == "0x63856ab8c1406f48621da28a7f0e501231c57bbb":
            platform = "opensea"
        slug: str = self.query_collection_info_list([contract_address])[0][
            "nftCollection"
        ]["slug"]
        fees: int = httpx.get(
            f"https://pumpx.io/api/v1/xbn/collectionFees?slug={slug}"
        ).json()["fees"][platform.upper()]["minimumRoyaltyBips"]

        res = httpx.post(
            "https://lending.pumpx.io/lending/api/v1/listings",
            headers={"authorization": f"Bearer {self.auth_token}"},
            json={
                "borrower_address": self.address,
                "contract_address": contract_address,
                "currency": "eth",
                "expiration_time": expiration_time,
                "network": "eth",
                "platform": platform,
                "qty": 1,
                "royalty": fees,
                "token_id": str(token_id),
                "type": 1,
                "price": str(Decimal(price) / 10**18),
            },
        ).json()
        assert (
            "error" not in res
        ), f"failed to collateral listing: {res['error']['message']}"
        task_log(self.task_id, "collateral listing success")
        task_log(
            self.task_id,
            f"contract address: {contract_address}, token id: {token_id}, platform: {platform}, expiration time: {expiration_time}, price: {price}",
        )
        return res
