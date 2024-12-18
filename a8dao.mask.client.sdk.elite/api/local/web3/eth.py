from typing import Any, List, Optional, TypedDict

import requests

from api import headers
from api.local.web3 import FailedRes, SuccessRes, base_url, web3_config
from model import ChainId

ethconfig = web3_config["eth"]


class CallDataItem(TypedDict):
    value: Any
    type: str


class CallData(TypedDict):
    function_name: str
    function_args: List[CallDataItem]


class ContractData(TypedDict):
    function_name: str
    function_args: tuple


class Balance(TypedDict):
    balance: int
    decimals: int


def get_token_balance(
    chain_name: ChainId, address: str, contract_address: Optional[str] = None
) -> FailedRes | SuccessRes[Balance]:
    params = {"chain_name": _get_chain_name(chain_name), "address": address}
    if contract_address:
        params["contract_address"] = contract_address
    res = requests.get(
        url=f'{base_url}{ethconfig["get_token_balance"]}',
        params=params,
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def get_transactions(chain_name: ChainId, address: str, offset: int = 100):
    res = requests.get(
        url=f'{base_url}{ethconfig["get_transactions"]}',
        params={"chain_name": _get_chain_name(
            chain_name), "address": address, "offset": offset},
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def get_latest_transaction(chain_name: ChainId, address: str):
    res = requests.get(
        url=f'{base_url}{ethconfig["get_latest_transaction"]}',
        params={"chain_name": _get_chain_name(chain_name), "address": address},
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def get_nonce(chain_name: ChainId, address: str):
    res = requests.get(
        url=f'{base_url}{ethconfig["get_nonce"]}',
        params={"chain_name": _get_chain_name(chain_name), "address": address},
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def get_gas_price(chain_name: ChainId):
    res = requests.get(
        url=f'{base_url}{ethconfig["get_gas_price"]}',
        params={"chain_name": _get_chain_name(chain_name)},
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def get_erc721_transfer_events(
    chain_name: ChainId, contract_address: str, address: str, offset: int = 100
) -> FailedRes | SuccessRes[dict]:
    res = requests.get(
        f'{base_url}{ethconfig["get_erc721_transfer_events"]}',
        params={
            "chain_name": _get_chain_name(chain_name),
            "contract_address": contract_address,
            "address": address,
            "offset": offset,
        },
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
        f'{base_url}{ethconfig["send_raw_transaction"]}',
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
    value: int = 0,
    contract_data: ContractData | None = None,
) -> FailedRes | SuccessRes[dict]:
    params = {
        "chain_name": _get_chain_name(chain_name),
        "private_key": private_key,
        "to": to,
        "value": value,
    }
    if contract_data:
        params["contract_data"] = contract_data
    res = requests.post(
        f'{base_url}{ethconfig["send_transaction"]}',
        json=params,
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def _get_chain_name(chain_id: ChainId) -> str:
    chain_name = chain_id.value
    if chain_id == ChainId.ETH_ZKS_ERA:
        chain_name = "eth-zksync"
    return chain_name
