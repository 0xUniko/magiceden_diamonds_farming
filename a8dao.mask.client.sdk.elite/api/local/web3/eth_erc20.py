import time
from typing import Any, List, Optional, TypedDict

import requests

from api import _get_chain_name, headers
from api.local.web3 import FailedRes, SuccessRes, base_url, web3_config
from model import ChainId

eth_erc20_config = web3_config["eth_erc20"]


class CallDataItem(TypedDict):
    value: Any
    type: str


class CallData(TypedDict):
    function_name: str
    function_args: List[CallDataItem]


class ContractData(TypedDict):
    function_name: str
    function_args: list


class Balance(TypedDict):
    balance: int
    decimals: int


def get_wallet_assets_statistics(
    chain_name: ChainId, address: str
) -> FailedRes | SuccessRes[dict]:
    retry_count = 0
    while True:
        res = requests.get(
            url=f'{base_url}{eth_erc20_config["get_wallet_assets_statistics"]}',
            params={"chain_name": _get_chain_name(
                chain_name), "address": address},
            headers=headers,
        )
        if res.status_code != 200:
            if retry_count < 3:
                continue
            return {"code": 1, "message": res.reason}
        return res.json()


def get_transaction_by_hash(
    chain_name: ChainId, hash: str
) -> FailedRes | SuccessRes[dict]:
    res = requests.get(
        url=f'{base_url}{eth_erc20_config["get_transaction_by_hash"]}',
        params={"chain_name": _get_chain_name(chain_name), "hash": hash},
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def get_internal_transactions_by_hash(
    chain_name: ChainId, hash: str
) -> FailedRes | SuccessRes[list]:
    res = requests.get(
        url=f'{base_url}{eth_erc20_config["get_internal_transactions_by_hash"]}',
        params={"chain_name": _get_chain_name(chain_name), "hash": hash},
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def get_transactions(
    chain_name: ChainId, address: str, offset: int = 100
) -> FailedRes | SuccessRes[list]:
    res = requests.get(
        url=f'{base_url}{eth_erc20_config["get_transactions"]}',
        params={
            "chain_name": _get_chain_name(chain_name),
            "address": address,
            "offset": offset,
        },
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def get_latest_transaction(
    chain_name: ChainId, address: str
) -> FailedRes | SuccessRes[dict]:
    retry_count = 0
    while True:
        res = requests.get(
            url=f'{base_url}{eth_erc20_config["get_latest_transaction"]}',
            params={"chain_name": _get_chain_name(
                chain_name), "address": address},
            headers=headers,
        )
        if res.status_code != 200:
            if retry_count < 3:
                continue
            return {"code": 1, "message": res.reason}
        return res.json()


def get_nonce(chain_name: ChainId, address: str) -> FailedRes | SuccessRes[int]:
    res = requests.get(
        url=f'{base_url}{eth_erc20_config["get_nonce"]}',
        params={"chain_name": _get_chain_name(chain_name), "address": address},
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def get_gas_price(chain_name: ChainId):
    res = requests.get(
        url=f'{base_url}{eth_erc20_config["get_gas_price"]}',
        params={"chain_name": _get_chain_name(chain_name)},
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def send_raw_transaction(
    chain_name: ChainId,
    private_key: str,
    to: str,
    function_signature: str,
    function_args: list,
    value: int = 0,
) -> FailedRes | SuccessRes[dict]:
    params = {
        "chain_name": _get_chain_name(chain_name),
        "private_key": private_key,
        "to": to,
        "function_signature": function_signature,
        "function_args": function_args,
        "value": value,
    }
    res = requests.post(
        f'{base_url}{eth_erc20_config["send_raw_transaction"]}',
        json=params,
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def send_raw_transaction_with_data(
    chain_name: ChainId,
    private_key: str,
    to: str,
    data: str,
    value: int = 0,
) -> FailedRes | SuccessRes[dict]:
    params = {
        "chain_name": _get_chain_name(chain_name),
        "private_key": private_key,
        "to": to,
        "data": data,
        "value": value,
    }
    res = requests.post(
        f'{base_url}{eth_erc20_config["send_raw_transaction_with_data"]}',
        json=params,
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def balance_of(
    chain_name: ChainId, address: str, contract_address: Optional[str] = None
) -> FailedRes | SuccessRes[int]:
    params = {"chain_name": _get_chain_name(chain_name), "address": address}
    if contract_address:
        params["contract_address"] = contract_address
    res = requests.get(
        url=f'{base_url}{eth_erc20_config["balance_of"]}',
        params=params,
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def transfer(
    chain_name: ChainId, private_key: str, to: str, value: int
) -> FailedRes | SuccessRes[dict]:
    params = {
        "chain_name": _get_chain_name(chain_name),
        "private_key": private_key,
        "to": to,
        "value": value,
    }
    res = requests.post(
        f'{base_url}{eth_erc20_config["transfer"]}',
        json=params,
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def send_transaction(
    chain_name: ChainId,
    private_key: str,
    to: str,
    abi_address: Optional[str] = None,
    abi: Optional[str] = None,
    value: int = 0,
    contract_data: ContractData | None = None,
) -> FailedRes | SuccessRes[dict]:
    params = {
        "chain_name": _get_chain_name(chain_name),
        "private_key": private_key,
        "to": to,
        "abi_address": abi_address,
        "abi": abi,
        "value": value,
    }
    if contract_data:
        params["contract_data"] = contract_data
    res = requests.post(
        f'{base_url}{eth_erc20_config["send_transaction"]}',
        json=params,
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def build_transaction(
    chain_name: ChainId,
    private_key: str,
    to: str,
    abi_address: Optional[str] = None,
    abi: Optional[str] = None,
    value: int = 0,
    contract_data: ContractData | None = None,
) -> FailedRes | SuccessRes[dict]:
    params = {
        "chain_name": _get_chain_name(chain_name),
        "private_key": private_key,
        "to": to,
        "abi_address": abi_address,
        "abi": abi,
        "value": value,
    }
    if contract_data:
        params["contract_data"] = contract_data
    res = requests.post(
        f'{base_url}{eth_erc20_config["build_transaction"]}',
        json=params,
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def signature(
    chain_name: ChainId, private_key: str, message: dict
) -> FailedRes | SuccessRes[str]:
    params = {
        "chain_name": _get_chain_name(chain_name),
        "private_key": private_key,
        "message": message,
    }
    res = requests.post(
        f'{base_url}{eth_erc20_config["signature"]}',
        json=params,
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def signature_text(
    chain_name: ChainId, private_key: str, message: str
) -> FailedRes | SuccessRes[str]:
    params = {
        "chain_name": _get_chain_name(chain_name),
        "private_key": private_key,
        "message": message,
    }
    res = requests.post(
        f'{base_url}{eth_erc20_config["signature_text"]}',
        json=params,
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def to_checksum_address(address: str):
    res = requests.get(
        url=f'{base_url}{eth_erc20_config["to_checksum_address"]}',
        params={"address": address},
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def raw_call(
    chain_name: ChainId,
    to: str,
    function_signature: str,
    function_args: list,
    value: int = 0,
) -> FailedRes | SuccessRes[str]:
    params = {
        "chain_name": _get_chain_name(chain_name),
        "to": to,
        "function_signature": function_signature,
        "function_args": function_args,
        "value": value,
    }
    res = requests.post(
        f'{base_url}{eth_erc20_config["raw_call"]}',
        json=params,
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def call_function(chain_name: ChainId,
                  to: str,
                  call_data: CallData,
                  abi_address: Optional[str] = None,
                  abi: Optional[str] = None) -> FailedRes | SuccessRes[Any]:
    params = {
        "chain_name": _get_chain_name(chain_name),
        "to": to,
        "abi_address": abi_address,
        "abi": abi,
        "call_data": call_data,
    }
    res = requests.post(
        f'{base_url}{eth_erc20_config["call_function"]}',
        json=params,
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()
