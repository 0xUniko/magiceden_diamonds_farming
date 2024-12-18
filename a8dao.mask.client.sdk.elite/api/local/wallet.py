import requests

from api import headers
from api.local.web3 import FailedRes, SuccessRes
from api.local import *

wallet_config = local_config["wallet"]
url_base = f'{host}:{wallet_config["port"]}'


def get_by_id(id: str) -> FailedRes | SuccessRes[dict]:
    response = requests.get(
        url=f'{url_base}{wallet_config["get_by_id"]}?id={id}',
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()

def get_by_role_id(role_id: int) -> FailedRes | SuccessRes[dict]:
    response = requests.get(
        url=f'{url_base}{wallet_config["get_by_role_id"]}?roleId={role_id}',
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()
