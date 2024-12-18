import time
from typing import Optional, TypedDict

import requests

from api import _get_chain_name, headers
from api.local.web3 import FailedRes, SuccessRes, base_url, web3_config
from model import ChainId

eth_erc721_config = web3_config["eth_erc721"]


class ContractData(TypedDict):
    function_name: str
    function_args: list


def balance_of(
    chain_name: ChainId, contract_address: str, address: str
) -> FailedRes | SuccessRes[int]:
    params = {
        "chain_name": _get_chain_name(chain_name),
        "contract_address": contract_address,
        "address": address,
    }
    response = requests.get(
        url=f'{base_url}{eth_erc721_config["balance_of"]}',
        params=params,
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": response.status_code, "message": response.reason}
    return response.json()


def token_of_owner_by_index(
    chain_name: ChainId, contract_address: str, address: str, index: int
) -> FailedRes | SuccessRes[int]:
    params = {
        "chain_name": _get_chain_name(chain_name),
        "contract_address": contract_address,
        "address": address,
        "index": index,
    }
    response = requests.get(
        url=f'{base_url}{eth_erc721_config["token_of_owner_by_index"]}',
        params=params,
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": response.status_code, "message": response.reason}
    return response.json()


def owner_of(
    chain_name: ChainId, contract_address: str, token_id: int
) -> FailedRes | SuccessRes[str]:
    retry_count = 0
    while True:
        try:
            params = {
                "chain_name": _get_chain_name(chain_name),
                "contract_address": contract_address,
                "token_id": token_id,
            }
            response = requests.get(
                url=f'{base_url}{eth_erc721_config["owner_of"]}',
                params=params,
                headers=headers,
            )
            if response.status_code != 200:
                if retry_count < 3:
                    retry_count += 1
                    continue
                return {"code": response.status_code, "message": response.reason}
            return response.json()
        except Exception as e:
            print(e)


def get_transfer_events(
    chain_name: ChainId, contract_address: str, address: str, offset: int = 100
) -> FailedRes | SuccessRes[list]:
    retry_count = 0
    while True:
        try:
            response = requests.get(
                f'{base_url}{eth_erc721_config["get_transfer_events"]}',
                params={
                    "chain_name": _get_chain_name(chain_name),
                    "contract_address": contract_address,
                    "address": address,
                    "offset": offset,
                },
                headers=headers,
            )
            if response.status_code != 200:
                if retry_count < 3:
                    retry_count += 1
                    continue
                else:
                    return {"code": response.status_code, "message": response.reason}
            return response.json()
        except Exception as e:
            print(e)


def safe_transfer_from(
    chain_name: ChainId,
    contract_address: str,
    private_key: str,
    source_address: str,
    target_address: str,
    token_id: int,
) -> FailedRes | SuccessRes[dict]:
    response = requests.post(
        f'{base_url}{eth_erc721_config["safe_transfer_from"]}',
        json={
            "chain_name": _get_chain_name(chain_name),
            "contract_address": contract_address,
            "private_key": private_key,
            "source_address": source_address,
            "target_address": target_address,
            "token_id": token_id,
        },
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": response.status_code, "message": response.reason}
    return response.json()


def set_approval_for_all(
    chain_name: ChainId,
    contract_address: str,
    private_key: str,
    operator_address: str,
    approved: bool = True,
) -> FailedRes | SuccessRes[dict]:
    print(
        {
            "chain_name": _get_chain_name(chain_name),
            "contract_address": contract_address,
            "private_key": private_key,
            "operator_address": operator_address,
            "approved": approved,
        }
    )
    response = requests.post(
        f'{base_url}{eth_erc721_config["set_approval_for_all"]}',
        json={
            "chain_name": _get_chain_name(chain_name),
            "contract_address": contract_address,
            "private_key": private_key,
            "operator_address": operator_address,
            "approved": approved,
        },
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": response.status_code, "message": response.reason}
    return response.json()


def safe_mint(
    chain_name: ChainId,
    contract_address: str,
    private_key: str,
    mint_to_address: str,
) -> FailedRes | SuccessRes[dict]:
    response = requests.post(
        f'{base_url}{eth_erc721_config["safe_mint"]}',
        json={
            "chain_name": _get_chain_name(chain_name),
            "contract_address": contract_address,
            "private_key": private_key,
            "mint_to_address": mint_to_address,
        },
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": response.status_code, "message": response.reason}
    return response.json()
