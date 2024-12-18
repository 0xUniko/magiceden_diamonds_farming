import requests

from api import headers
from api.local.web3 import FailedRes, SuccessRes
from api.network import *
from model import ChainId

wallet_config = network_config["wallet"]


def get_by_id(id: str) -> FailedRes | SuccessRes[dict]:
    response = requests.get(
        url=f'{host}{wallet_config["get_by_id"]}?id={id}',
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def create(
    address: str,
    private_key: str,
    mnemonic: str,
    metamask_password: str,
    chain_id: ChainId,
) -> FailedRes | SuccessRes[dict]:
    post_data = {
        "account_org_id": headers["account_org_id"],
        "address": address,
        "private_key": private_key,
        "mnemonic": mnemonic,
        "metamask_password": metamask_password,
        "chain_id": chain_id.value,
    }
    response = requests.post(
        url=f'{host}{wallet_config["create"]}', headers=headers, json=post_data
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()
