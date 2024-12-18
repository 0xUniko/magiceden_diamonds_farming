from typing import TypedDict

import requests

from api import headers
from api.local.web3 import FailedRes, SuccessRes, base_url, web3_config

solana_config = web3_config["solana"]


class SplBalance(TypedDict):
    amount: int
    decimals: int
    uiAmountString: str


def get_spl_balance(
    mint_address: str, owner: str
) -> FailedRes | SuccessRes[SplBalance]:
    retry_count = 0
    while True:
        res = requests.get(
            url=f'{base_url}{solana_config["get_spl_balance"]}',
            params={"mint_address": mint_address, "owner": owner},
            headers=headers,
        )
        if res.status_code != 200:
            if retry_count < 3:
                continue
            return {"code": 1, "message": res.reason}
        return res.json()


def get_pub_key_from_mnemonic(mnemonic: str) -> FailedRes | SuccessRes[str]:
    retry_count = 0
    while True:
        res = requests.get(
            url=f'{base_url}{solana_config["get_pub_key_from_mnemonic"]}',
            params={"mnemonic": mnemonic},
            headers=headers,
        )
        if res.status_code != 200:
            if retry_count < 3:
                continue
            return {"code": 1, "message": res.reason}
        return res.json()


def get_balance(pubkey: str) -> FailedRes | SuccessRes[int]:
    retry_count = 0
    while True:
        res = requests.get(
            url=f'{base_url}{solana_config["get_balance"]}',
            params={"pubkey": pubkey},
            headers=headers,
        )
        if res.status_code != 200:
            if retry_count < 3:
                continue
            return {"code": 1, "message": res.reason}
        return res.json()
