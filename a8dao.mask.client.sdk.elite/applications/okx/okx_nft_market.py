from typing import Literal, TypedDict
from api.local.web3.eth_erc20 import signature
from api.local.web3.eth_erc721 import set_approval_for_all
from applications.okx.okx_api import OkxAPI
from model import ChainId, chain_id_to_chain_name, wallet_data
from tools.logger import task_log


class ListingItem(TypedDict):
    collectionAddress: str
    tokenId: str
    price: str
    currencyAddress: str
    count: int
    validTime: int
    platform: Literal["okx"] | Literal["opensea"]


class ListingData(TypedDict):
    chain: str  # https://www.okx.com/cn/web3/build/docs/build-dapp/marketplace-supported-blockchains
    walletAddress: str
    items: list[ListingItem]


class Order(TypedDict):
    orderId: str
    takeCount: int


"""
 {
    "chain": "arbitrum",
    "walletAddress": wallet_address,
    "items": [
        {
            "collectionAddress": "0x175edb154ed7a0e54410a7f547aaa7e3fbf21a34",
            "tokenId": "3518",
            "price": "100000000000000",
            "currencyAddress": "0x0000000000000000000000000000000000000000",
            "count": 1,
            "validTime": 1701915719,
            "platform": "okx",
        }
    ],
}
"""

chain_name_to_okx_nft_market_chain = {
    "eth-erc20": "eth", "eth-arb": "arbitrum"}


class OkxNftMarket(OkxAPI):
    def list_nft(self, wallet: wallet_data, listing_data: ListingData):
        """
        list nft, only support list one item now
        return orderId
        """
        task_log(
            self.task_id,
            f'list nft: {listing_data["items"][0]["collectionAddress"]} token_id: {listing_data["items"][0]["tokenId"]}',
        )
        task_log(self.task_id, "get listing info...")
        steps = self.send_request(
            "/api/v5/mktplace/nft/markets/create-listing", listing_data)["steps"]  # type: ignore
        if steps[0]["items"][0]["status"] == "incomplete":
            task_log(self.task_id, "approve nft...")
            item = steps[0]["items"][0]
            res = set_approval_for_all(
                ChainId(chain_id_to_chain_name[item["chain"]]),
                item["collectionAddress"],
                wallet["private_key"],
                item["approvalAddress"],
            )
            assert res["code"] == 0, "approve nft failed"
            task_log(self.task_id, "approve nft succeeded")
        else:
            task_log(self.task_id, "nft already approved")

        item = steps[1]["items"][0]
        contract_message_raw = item["data"]
        contract_message = {
            "conduitKey": bytes.fromhex(contract_message_raw["conduitKey"][2:]),
            "consideration": [
                {
                    "endAmount": int(con["endAmount"]),
                    "identifierOrCriteria": int(con["identifierOrCriteria"]),
                    "itemType": con["itemType"],
                    "recipient": con["recipient"],
                    "startAmount": int(con["startAmount"]),
                    "token": con["token"],
                }
                for con in contract_message_raw["consideration"]
            ],
            "counter": int(contract_message_raw["counter"]),
            "endTime": contract_message_raw["endTime"],
            "offer": [
                {
                    "endAmount": int(offer["endAmount"]),
                    "identifierOrCriteria": int(offer["identifierOrCriteria"]),
                    "itemType": offer["itemType"],
                    "startAmount": int(offer["startAmount"]),
                    "token": offer["token"],
                }
                for offer in contract_message_raw["offer"]
            ],
            "offerer": contract_message_raw["offerer"],
            "orderType": contract_message_raw["orderType"],
            # "salt": bytes.fromhex(contract_message_raw["salt"][2:]),
            "salt": int(contract_message_raw["salt"], 16),
            "startTime": contract_message_raw["startTime"],
            "totalOriginalConsiderationItems": contract_message_raw[
                "totalOriginalConsiderationItems"
            ],
            "zone": contract_message_raw["zone"],
            "zoneHash": bytes.fromhex(contract_message_raw["zoneHash"][2:]),
        }
        json_message = {
            "domain": item["domain"],
            "message": contract_message,
            "primaryType": item["primaryType"],
            "types": item["types"],
        }
        signature_result = signature(
            wallet["chain_id"], wallet["private_key"], json_message)

        submit_listing_body = {
            "chain": listing_data["chain"],
            "walletAddress": wallet["address"],
            "items": [
                {
                    "platform": listing_data["items"][0]["platform"],
                    "signature": signature_result,
                    "order": contract_message_raw,
                }
            ],
        }
        task_log(self.task_id, "submiting listing body...")
        res = self.send_request(
            "/api/v5/mktplace/nft/markets/submit-listing", submit_listing_body
        )["results"][0]
        assert res["success"], f'failed to submit listing: {res["message"]}'
        return item["orderIds"][0]

    def get_listing(
        self,
        chain: str,
        collection_address: str | None,
        token_id: int | None,
        maker: str | None,
    ):
        return self.send_request(
            "/api/v5/mktplace/nft/markets/listings",
            {
                "chain": chain,
                "collectionAddress": collection_address,
                "tokenId": str(token_id) if token_id is None else None,
                "maker": maker,
            },
            "get",
        )

    def buy_nft(self, wallet: wallet_data, items: list[Order]):
        return self.send_request(
            "/api/v5/mktplace/nft/markets/buy",
            {
                "chain": chain_name_to_okx_nft_market_chain[wallet["chain_id"]],
                "walletAddress": wallet["address"],
                "items": items,
            },
        )
