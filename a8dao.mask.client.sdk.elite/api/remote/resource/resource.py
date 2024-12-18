import json
from typing import TypedDict

import requests

from api import headers
from api.remote import *
from api.remote.resource import *
from model import ChainId, ResourceType
from api import Response, get_response
from api import _get_chain_name


class ExtendInformation(TypedDict):
    resource_type_code: ResourceType
    resource_id: int
    extend_information: dict


resource_config = resource_config["resource"]


def save_extend_information(extend_information: ExtendInformation) -> dict:
    response = requests.post(
        f'{host}{resource_config["save_extend_information"]}',
        json={
            "resource_type_code": extend_information["resource_type_code"].value,
            "resource_id": extend_information["resource_id"],
            "extend_information": json.dumps(extend_information["extend_information"]),
        },
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def assets_update_asset(chain_name: ChainId, address: str) -> dict:
    response = requests.post(
        f'{host}{resource_config["assets_update_asset"]}',
        json={"chain_name": _get_chain_name(chain_name), "address": address},
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


class HubstudioAPIPassportResponse(TypedDict):
    is_pass: str


def hubstudio_api_passport() -> Response[HubstudioAPIPassportResponse]:
    response = requests.get(
        f'{host}{resource_config["hubstudio_api_passport"]}',
        params={},
        headers=headers,
    )
    return get_response(response, HubstudioAPIPassportResponse)
