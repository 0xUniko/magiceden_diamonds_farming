import requests
from api.remote.resource import *
from api import headers
from api.remote import *

twitter_config = resource_config["twitter"]


def add(twitter: dict) -> dict:
    response = requests.post(
        f'{host}{twitter_config["add"]}',
        json=twitter,
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()
