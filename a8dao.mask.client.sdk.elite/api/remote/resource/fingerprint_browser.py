import requests
from api.remote.resource import *
from api import headers
from api.remote import *

fingerprint_browser_config = resource_config["fingerprint_browser"]


def get_key_list() -> dict:
    response = requests.get(
        f'{host}{fingerprint_browser_config["get_key_list"]}',
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()
