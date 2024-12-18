import requests
from api.remote.resource import *
from api import headers
from api.remote import *

discord_config = resource_config["discord"]


def add(discord: dict) -> dict:
    response = requests.post(
        f'{host}{discord_config["add"]}',
        json=discord,
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()
