import requests
from api.remote.resource import *
from api import headers
from api.remote import *

email_config = resource_config["email"]


def add(email: dict) -> dict:
    response = requests.post(
        f'{host}{email_config["add"]}',
        json=email,
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()
