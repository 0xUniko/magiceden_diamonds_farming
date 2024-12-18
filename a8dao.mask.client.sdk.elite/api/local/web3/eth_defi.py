import time
from typing import Optional, TypedDict

import requests

from api import headers
from api.local.web3 import FailedRes, SuccessRes, base_url, web3_config
from model import ChainId
from api import _get_chain_name

eth_defi_config = web3_config["eth_defi"]


def get_token_list(chain_name: ChainId) -> FailedRes | SuccessRes[dict]:
    res = requests.get(
        url=f'{base_url}{eth_defi_config["get_token_list"]}',
        params={"chain_name": _get_chain_name(chain_name)},
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def swap(
    chain_name: ChainId,
    private_key: str,
    from_token_contract_address: str,
    to_token_contract_address: str,
    amount: int,
    slippage: float,
    full_allowance: bool = False,
) -> FailedRes | SuccessRes[dict]:
    params = {
        "chain_name": _get_chain_name(chain_name),
        "private_key": private_key,
        "from_token_contract_address": from_token_contract_address,
        "to_token_contract_address": to_token_contract_address,
        "amount": amount,
        "full_allowance": full_allowance,
        "slippage": slippage,
    }
    res = requests.post(
        f'{base_url}{eth_defi_config["swap"]}',
        json=params,
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()
