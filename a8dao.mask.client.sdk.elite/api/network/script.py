import requests
from api.network import *
from api import headers

script_config = network_config["script"]


def get_by_id(id: str):
    response = requests.get(
        url=f'{host}{script_config["get_by_id"]}?id={id}',
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


