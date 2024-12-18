from typing import Literal, NotRequired, TypedDict

import requests

from api import headers
from api.local.web3 import FailedRes, SuccessRes, base_url, web3_config
from config import config

starkconfig = web3_config["starknet"]
eth_contract = config["contract"]["starknet"]["eth"]


def wallet_generate(mnemonic: str) -> FailedRes | SuccessRes[dict]:
    return requests.get(
        f'{base_url}{starkconfig["wallet_generate"]}',
        params={"mnemonic": mnemonic},
        headers=headers,
    ).json()
    # if res.status_code != 200:
    #     return {"code": 1, "message": res.reason}
    # res = res.json()
    # data = {
    #     "address": res["address"],
    #     "mnemonic": mnemonic,
    #     "private_key": res["privateKey"],
    # }
    # return {"code": 0, "message": "OK", "data": data}


def wallet_deploy(wallet: dict) -> FailedRes | SuccessRes[dict]:
    return requests.post(
        f'{base_url}{starkconfig["wallet_deploy"]}',
        json={
            "address": wallet["address"],
            "private_key": wallet["private_key"],
            "mnemonic": wallet["mnemonic"],
        },
        headers=headers,
    ).json()


def get_nonce(address: str) -> FailedRes | SuccessRes[int]:
    return requests.get(
        f'{base_url}{starkconfig["get_nonce"]}',
        params={"address": address},
        headers=headers,
    ).json()


class Balance(TypedDict):
    balance: int
    decimals: int


def get_token_balance(
    address: str, contract_address: str = eth_contract
) -> FailedRes | SuccessRes[Balance]:
    res = requests.get(
        f'{base_url}{starkconfig["get_token_balance"]}',
        params={"address": address, "contract_address": contract_address},
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def invoke(
    contract_address: str,
    function_name: str,
    function_args: dict,
    address: str,
    private_key: str,
) -> FailedRes | SuccessRes[str]:
    return requests.post(
        f'{base_url}{starkconfig["invoke"]}',
        json={
            "contract_address": contract_address,
            "function_name": function_name,
            "function_args": function_args,
            "address": address,
            "private_key": private_key,
        },
        headers=headers,
    ).json()


def call(
    contract_address: str,
    function_name: str,
    function_args: dict,
) -> FailedRes | SuccessRes[dict]:
    return requests.post(
        f'{base_url}{starkconfig["call"]}',
        json={
            "contract_address": contract_address,
            "function_name": function_name,
            "function_args": function_args,
        },
        headers=headers,
    ).json()


class CallRequest(TypedDict):
    contract_address: str
    function_name: str
    cairo_version: NotRequired[int]  # default is 0
    function_args: NotRequired[dict]  # default is {}


def multicall(
    address: str,
    private_key: str,
    calls: list[CallRequest],
) -> FailedRes | SuccessRes[dict]:
    return requests.post(
        f'{base_url}{starkconfig["multicall"]}',
        json={
            "address": address,
            "private_key": private_key,
            "calls": calls,
        },
        headers=headers,
    ).json()


class RawCallRequest(TypedDict):
    contract_address: str
    function_name: str
    call_data: list[str]


def multi_raw_call(
    address: str,
    private_key: str,
    raw_calls: list[RawCallRequest],
) -> FailedRes | SuccessRes[dict]:
    return requests.post(
        f'{base_url}{starkconfig["multi_raw_call"]}',
        json={
            "address": address,
            "private_key": private_key,
            "raw_calls": raw_calls,
        },
        headers=headers,
    ).json()


class Tx(TypedDict):
    actual_fee: str
    hash: str
    status: Literal["Accepted on L1"] | Literal["Accepted on L2"] | Literal["Failed"]


def get_latest_transaction(address: str) -> FailedRes | SuccessRes[Tx]:
    res = requests.get(
        f'{base_url}{starkconfig["get_latest_transaction"]}',
        params={"address": address},
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return {"code": 0, "message": "OK", "data": res.json()}
