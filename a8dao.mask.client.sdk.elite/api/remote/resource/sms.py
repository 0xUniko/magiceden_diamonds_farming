import requests
from api.remote.resource import *
from api import *
from api.remote import *

sms_config = resource_config["sms"]


def get_number(service: str, country: str) -> dict:
    response = requests.post(
        f'{host}{sms_config["get_number"]}',
        json={"service": service, "country": country},
        headers=headers
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def release_number(number: str) -> dict:
    response = requests.post(
        f'{host}{sms_config["release_number"]}',
        json={"number": number},
        headers=headers
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def get_code(number: str) -> dict:
    response = requests.post(
        f'{host}{sms_config["get_code"]}',
        json={"number": number},
        headers=headers
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()
