from typing import TypedDict
import json
import requests

from api import headers
from api.remote import *
from api.remote.resource import *
from model import ChainId
from model import ResourceType

wallet_config = resource_config["wallet"]


class WalletAddressChain(TypedDict):
    id: str
    tx_id: str
    block: str


def save_wallet_address_chain(wallet_address_chain: WalletAddressChain) -> dict:
    response = requests.post(
        f'{host}{wallet_config["save_wallet_address_chain"]}',
        json=wallet_address_chain,
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


class WalletAddressDTO(TypedDict):
    id: int
    address: str
    label: str
    status: int
    chain_id: ChainId
    wallet_api_id: str


def batch_import(wallet_address_dto_list: list[WalletAddressDTO]) -> dict:
    w_list = []
    for w in wallet_address_dto_list:
        w_list.append(
            {
                "id": w["id"],
                "address": w["address"],
                "label": w["label"],
                "status": w["status"],
                "chain_id": w["chain_id"].value,
                "wallet_api_id": w["wallet_api_id"],
                "account_org_id": headers["account_org_id"],
            }
        )
    post_data = {
        "account_org_id": headers["account_org_id"],
        "wallet_address_list": w_list,
    }
    response = requests.post(
        f'{host}{wallet_config["batch_import"]}',
        json=post_data,
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": response.status_code, "message": response.reason}
    return response.json()


def wallet_append_wallet_address(wallet_id: str, wallet_address_id: str) -> dict:
    response = requests.post(
        f'{host}{wallet_config["wallet_append_wallet_address"]}',
        headers=headers,
        json={"wallet_id": wallet_id, "wallet_address_id": wallet_address_id},
    )
    if response.status_code != 200:
        return {"code": response.status_code, "message": response.reason}
    return response.json()


class ExtendInformation(TypedDict):
    resource_id: int
    extend_information: dict

def save_extend_information(extend_information: ExtendInformation) -> dict:
    print(
        {
            "id": extend_information["resource_id"],
            "extend_information": json.dumps(extend_information["extend_information"]),
        }
    )
    response = requests.post(
        f'{host}{resource_config["wallet"]["save_extend_information"]}',
        json={
            "id": extend_information["resource_id"],
            "extend_information": json.dumps(extend_information["extend_information"]),
        },
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()
