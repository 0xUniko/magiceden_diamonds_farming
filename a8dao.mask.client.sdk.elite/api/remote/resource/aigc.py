from typing import List
import requests
from api.remote.resource import *
from api import *
from api.remote import *

aigc_config = resource_config["aigc"]


def image(prompt: str, size: str):
    response = requests.post(
        f'{host}{aigc_config["image"]}',
        json={"prompt": prompt, "size": size},
        headers=headers
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def ask(messages: List[dict]) -> dict:
    response = requests.post(
        f'{host}{aigc_config["ask"]}',
        json={"messages": messages},
        headers=headers
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def extract_verification_code(content: str) -> dict:
    response = requests.post(
        f'{host}{aigc_config["extract_verification_code"]}',
        json={"content": content},
        headers=headers
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()
