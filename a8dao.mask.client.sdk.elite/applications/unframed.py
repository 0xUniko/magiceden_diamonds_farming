from enum import Enum
from typing import Literal, TypedDict

import requests

from api.local.web3.starknet import call, invoke, multi_raw_call
from config import config
from extensions.argentx import ArgentX
from fingerprint.browser import Browser
from model import wallet_data
from tools.logger import task_log
from tools.web3_tools import TxRecorder

unframed_contract = "0x051734077ba7baf5765896c56ce10b389d80cdcee8622e23c0556fb49e82df1b"
eth_contract = config["contract"]["starknet"]["eth"]
unframed_operator_contract = (
    "0x3a2fc8b0db9a9ef748227ef61ed254897cb40ad39575a9bde734dc78073f779"
)


class CollectionType(Enum):
    erc721 = "0x01"


class Calldata(TypedDict):
    additional_params: list[str]
    amount: str
    collection: str
    collection_type: str
    currency: str
    end_time: int
    global_nonce: str
    limit_price: str
    maker: str
    max_fee: str
    order_nonce: str
    side: Literal["sell"] | Literal["buy"]
    signature: list[str]
    start_time: int
    strategy: str
    token_id: str


class Nft(TypedDict):
    tokenId: str
    name: str
    bestListPrice: str
    spec: Literal["erc721"]


class Unframed:
    def __init__(
        self,
        task_id: str,
        browser: Browser | None = None,
        argentx: ArgentX | None = None,
    ) -> None:
        self.task_id = task_id
        self.browser = browser
        self.argentx = argentx
        pass

    def home_and_connect_wallet(self):
        task_log(self.task_id, "go to unframed and connect wallet")
        assert self.browser is not None, "browser instance is required"
        assert self.argentx is not None, "argentx instance is required"
        self.browser.initialized_get("https://unframed.co/")
        log_in = self.browser.find_element_and_wait(
            "span.overflow-hidden.flex.flex-col.items-center.justify-center"
        )
        if log_in.text == "Log in":
            task_log(self.task_id, "connecting argentx...")
            self.browser.click(log_in)
            wallet_btn = self.browser.find_element_and_wait("p.font-semibold.text-base")
            assert (
                wallet_btn.text == "Argent X"
            ), "you are not clicking the argentx button"
            self.browser.click(wallet_btn)
            self.argentx.confirm()
        profile = self.browser.find_element_and_wait(
            "span.overflow-hidden.flex.flex-col.items-center.justify-center"
        )
        assert profile.text.endswith("ETH"), "fail in connecting to wallet"
        task_log(self.task_id, "already connected to wallet")

    def scan_nft_collection(self, nft_contract: str):
        assert self.browser is not None, "browser instance is required"
        self.browser.initialized_get(f"https://unframed.co/collection/{nft_contract}")
        return [
            item
            for item in self.browser.find_elements_and_wait("a")
            if item.get_attribute("href").startswith("https://unframed.co/item/")
        ]

    def get_collection(self, collection_contract: str) -> list[Nft]:
        task_log(self.task_id, f"get collection: {collection_contract}")
        content = requests.get(
            f"https://cloud.argent-api.com/v1/pandora/starknet/mainnet/collection/{collection_contract}/nfts?page=0&size=60"
        ).json()["content"]
        return [
            {
                "tokenId": nft["tokenId"],
                "name": nft["name"],
                "bestListPrice": nft["bestListPrice"],
                "spec": nft["spec"],
            }
            for nft in content
        ]

    @staticmethod
    def get_user_owned_collection(task_id, address: str):
        task_log(task_id, f"get collection of user: {address}")
        address = "0x" + "0" * (66 - len(address)) + address[2:]
        return requests.get(
            f"https://cloud.argent-api.com/v1/pandora/starknet/mainnet/profile/{address.lower()}/nfts?page=0&size=60"
        ).json()["content"]

    def buy_nft(self, item_address: str, wallet: wallet_data):
        assert self.browser is not None, "browser instance is required"
        assert self.argentx is not None, "argentx instance is required"
        task_log(self.task_id, f"go to {item_address}")
        self.browser.initialized_get(item_address)
        buy_now = self.browser.find_element_and_wait(
            "span.h-11.flex.items-center.justify-center.w-full"
        )
        self.browser.click(buy_now)
        with TxRecorder(self.task_id, wallet):
            self.argentx.confirm()
        task_log(self.task_id, "buy nft succeeded")

    def sell_nft(self, item_url: str, wallet: wallet_data, amount: float):
        assert self.browser is not None, "browser instance is required"
        assert self.argentx is not None, "argentx instance is required"
        task_log(self.task_id, f"go to {item_url}")
        self.browser.initialized_get(item_url)
        list_btn = self.browser.find_element_and_wait(
            "span.h-11.flex.items-center.justify-center.w-full"
        )
        assert list_btn.text != "Cancel listing", "already listing"
        self.browser.click(list_btn)
        price = self.browser.find_element_and_wait(
            "input[inputmode=numeric][type=text]"
        )
        self.browser.click(price)
        self.browser.send_keys(price, amount)
        list_now_btn = self.browser.find_element_and_wait(
            "span.h-11.flex.items-center.justify-center.w-full"
        )
        isApprovedAll_res = call(
            item_url.split("/")[4],
            "isApprovedForAll",
            {"owner": wallet["address"], "operator": unframed_operator_contract},
        )
        assert (
            isApprovedAll_res["code"] == 0
        ), f'check isApprovedForAll failed: {isApprovedAll_res["message"]}'
        if not isApprovedAll_res["data"]["isApproved"]:
            task_log(self.task_id, "not isApprovedForAll, setApprovedForAll ing...")
            setApprovalForAll_res = invoke(
                item_url.split("/")[4],
                "setApprovalForAll",
                {"operator": unframed_operator_contract, "approved": 1},
                wallet["address"],
                wallet["private_key"],
            )
            assert (
                setApprovalForAll_res["code"] == 0
            ), f'setApprovalForAll failed: {setApprovalForAll_res["message"]}'
            task_log(self.task_id, "setApprovalForAll succeeded")
        else:
            task_log(self.task_id, "already isApprovedForAll")
        self.browser.click(list_now_btn)
        self.argentx.confirm()
        self.browser.wait(5, 8)
        cancel_listing = self.browser.find_element_and_wait(
            "span.h-11.flex.items-center.justify-center.w-full"
        )
        assert cancel_listing.text == "Cancel listing", "listing failed"
        task_log(self.task_id, "listing succeeded")

    def find_available_nfts(self, collection: str):
        task_log(self.task_id, f"find available nft in collection: {collection}")
        nft_list = self.get_collection(collection)
        return [
            nft
            for nft in nft_list
            if len(
                requests.get(
                    f"https://cloud.argent-api.com/v1/pandora/starknet/mainnet/nft/{collection}/{nft['tokenId']}/order?side=sell&page=0&size=32"
                ).json()["content"]
            )
            == 1
        ]

    def buy_nft_onchain(
        self, collection: str, nft_id: str, buyer_address: str, private_key: str
    ):
        task_log(self.task_id, f"buy collection: {collection}, id: {nft_id}")
        content = requests.get(
            f"https://cloud.argent-api.com/v1/pandora/starknet/mainnet/nft/{collection}/{nft_id}/order?side=sell&page=0&size=32"
        ).json()["content"]
        assert len(content) == 1, "no maker"
        calldata: Calldata = content[0]
        token_id = hex(int(calldata["token_id"]))
        token_id1 = token_id[-32:]
        token_id2 = "0x00" if len(token_id) <= 34 else token_id[: len(token_id) - 32]

        res = multi_raw_call(
            buyer_address,
            private_key,
            [
                {
                    "contract_address": eth_contract,
                    "function_name": "increaseAllowance",
                    "call_data": [
                        unframed_contract,
                        hex(int(calldata["limit_price"])),
                        "0x00",
                    ],
                },
                {
                    "contract_address": unframed_contract,
                    "function_name": "execute_taker_buy",
                    "call_data": [
                        hex(int(calldata["limit_price"])),
                        "0x00",
                        hex(int(calldata["max_fee"])),
                        "0x00"
                        if len(calldata["additional_params"]) == 0
                        else "0x00",  # TODO:additional_params
                        "0x01",
                        calldata["maker"],
                        calldata["collection"],
                        CollectionType[calldata["collection_type"]].value,
                        hex(int(calldata["limit_price"])),
                        "0x00",
                        token_id1,
                        token_id2,
                        hex(int(calldata["amount"])),
                        "0x00",
                        calldata["strategy"],
                        calldata["currency"],
                        hex(int(calldata["global_nonce"])),
                        hex(int(calldata["order_nonce"])),
                        hex(int(calldata["start_time"])),
                        hex(int(calldata["end_time"])),
                        hex(int(calldata["max_fee"])),
                        "0x00"
                        if len(calldata["additional_params"]) == 0
                        else "0x00",  # TODO:additional_params
                        hex(len(calldata["signature"])),
                        *calldata["signature"],
                    ],
                },
            ],
        )
        assert res["code"] == 0, f'buy transaction failed: {res["message"]}'
        task_log(self.task_id, "buy successfully")
