from typing import Literal, Optional, TypedDict, TypeVar

import requests

from api import headers
from api.remote import *
from api.remote.rpg import *

role_config = rpg_config["role"]


class FailedRes(TypedDict):
    code: Literal[1]
    message: str


def empty_role_bind_resource(
    role_id: str,
    email_id: Optional[str] = None,
    discord_id: Optional[str] = None,
    twitter_id: Optional[str] = None,
) -> dict:
    post_data = {
        "role_id": role_id,
    }
    if email_id:
        post_data["email_id"] = email_id
    if discord_id:
        post_data["discord_id"] = discord_id
    if twitter_id:
        post_data["twitter_id"] = twitter_id

    response = requests.post(
        f'{host}{role_config["empty_role_bind_resource"]}',
        json=post_data,
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


class RoleIdsRes(TypedDict):
    code: Literal[0]
    message: Literal["OK"]
    data: list[str]


def batch_create_empty_role(
    role_label_id_list: list[int], role_amount: int, user_org_id: str
) -> FailedRes | RoleIdsRes:
    res = requests.post(
        f'{host}{role_config["batch_create_empty_role"]}',
        json={
            "role_label_id_list": role_label_id_list,
            "role_amount": role_amount,
            "user_org_id": user_org_id,
        },
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def modify_extend_information(
    role_id: str, extend_information: dict
) -> FailedRes | RoleIdsRes:
    res = requests.post(
        f'{host}{role_config["modify_extend_information"]}',
        json={"role_id": role_id, "extend_information": extend_information},
        headers=headers,
    )
    if res.status_code != 200:
        return {"code": 1, "message": res.reason}
    return res.json()


def get_empty_role_list(search_text: str, page_index: int = 1, page_size: int = 10) -> dict:
    response = requests.get(
        url=f'{host}{role_config["get_empty_role_list"]}',
        params={
            "search_text": search_text,
            "page_index": str(page_index),
            "page_size": str(page_size)
        },
        headers=headers)
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def get_role_list(search_text: str, page_index: int = 1, page_size: int = 10) -> dict:
    response = requests.get(
        url=f'{host}{role_config["get_role_list"]}',
        params={
            "search_text": search_text,
            "page_index": str(page_index),
            "page_size": str(page_size)
        },
        headers=headers)
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def get_role_by_id(id: str) -> dict:
    response = requests.get(
        url=f'{host}{role_config["get_role_by_id"]}',
        params={"id": id},
        headers=headers)
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()
