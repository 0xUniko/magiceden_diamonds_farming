from typing import Literal, TypedDict

import requests

from api.local.web3.starknet import call, invoke
from tools.logger import task_log


class Eligibility(TypedDict):
    eligible: bool
    sig_r: str
    sig_s: str
    sig_v: Literal[""]


class StarknetTurkiyeNft:
    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        self.defi_adventure_nft_contract = (
            "0x0106c94dc954944b3893e2102d9ad5065d04a0ec9b08910891d8eedb75965334"
        )
        self.defi_adventure_api = "https://api.starknetturkiye.org/eligibility"

    def mint(self, campaign_id: int, address: str, private_key: str):
        task_log(self.task_id, f"mint campaign {campaign_id} nft to address: {address}")
        eligibility = self.eligibility(address, campaign_id)
        if eligibility["eligible"]:
            task_log(self.task_id, "has eligibility, minting...")
            res = invoke(
                self.defi_adventure_nft_contract,
                "mint",
                {
                    "campaign_id": campaign_id,
                    "order": {
                        "wallet_address": address,
                        "signer": "0x26128e6c0821347d2eea17548431dee2c66d9654cd3b9637447e2a91505d1df",
                        "campaign_id": campaign_id,
                        "amount": 1,
                        "expiry": 1691596800,
                        "strategy": "0x4f7e61fa8adab9e958f8c832868f77b149803834daa00491a1f2fbcd5dc5fb4",
                        "collection": "0x106c94dc954944b3893e2102d9ad5065d04a0ec9b08910891d8eedb75965334",
                    },
                    "hashDomain": "0x16ed14bf62427f6a87189a1855df2c6a467b93bf94cb8cf405482e4a670e982",
                    "orderSignature": [
                        hex(int(eligibility["sig_r"])),
                        hex(int(eligibility["sig_s"])),
                    ],
                },
                address,
                private_key,
            )
            assert res["code"] == 0, f'mint failed: {res["message"]}'
            task_log(self.task_id, "mint succeeded")
        else:
            task_log(self.task_id, "does not have eligibility")

    def eligibility(self, address: str, campaign_id: int) -> Eligibility:
        task_log(self.task_id, f"get eligibility of address: {address}")
        res = requests.get(
            self.defi_adventure_api,
            params={"address": address, "campaign_id": campaign_id},
        )
        if res.status_code != 200:
            raise Exception(res.reason)
        return res.json()

    def get_user_campaign_balance(self, address: str, campaign_id: int):
        task_log(
            self.task_id,
            f"get user campaign balance of address: {address} and campaign_id: {campaign_id}",
        )
        res = call(
            self.defi_adventure_nft_contract,
            "getUserCampaignBalance",
            {"user": address, "campaign_id": campaign_id},
        )
        assert res["code"] == 0, f'get user campaign balance failed: {res["message"]}'
        return res["data"]["balance"]
