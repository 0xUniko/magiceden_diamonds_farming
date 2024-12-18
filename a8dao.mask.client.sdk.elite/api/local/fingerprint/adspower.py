from typing import List, Optional
from api.local.fingerprint import *
from api.local import *
from api import get_requests
import time


adspower_config = fingerprint_config["adspower"]
url_base = f'{host}:{adspower_config["port"]}'


def start(user_id: str) -> dict:
    url = f'{url_base}/api/v1/browser/start?user_id={user_id}&open_tabs=1&ip_tab=0'

    response = get_requests().get(
        url=url,
        headers=headers,
    )
    time.sleep(1)
    if response.status_code == 200:
        return response.json()
    else:
        return {"code": response.status_code, "message": response.reason}


def stop(user_id: str) -> dict:
    url = f'{url_base}/api/v1/browser/stop?user_id={user_id}'

    response = get_requests().get(
        url=url,
        headers=headers,
    )
    time.sleep(1)

    if response.status_code == 200:
        return response.json()
    else:
        return {"code": response.status_code, "message": response.reason}


def active(user_id: str) -> dict:
    url = f'{url_base}/api/v1/browser/active?user_id={user_id}'

    response = get_requests().get(
        url=url,
        headers=headers,
    )
    time.sleep(1)

    if response.status_code == 200:
        return response.json()
    else:
        return {"code": response.status_code, "message": response.reason}


def list(containerName: Optional[str] = None) -> dict:
    return {}


def create(name: str, application_id: int = 0, user_proxy: Optional[dict] = None) -> dict:
    post_data = {
        "name": name,
        "group_id": "0",
        "sys_app_cate_id": application_id,
        "fingerprint_config": {},
        "user_proxy_config": {
            "proxy_soft": "no_proxy"
        }
    }
    if user_proxy:
        post_data["user_proxy_config"] = user_proxy

    url = f'{url_base}/api/v1/user/create'

    response = get_requests().post(
        url=url,
        json=post_data,
        headers=headers,
    )
    time.sleep(1)

    if response.status_code == 200:
        return response.json()
    else:
        return {"code": response.status_code, "message": response.reason}


def delete(user_ids: List[str]) -> dict:
    post_data = {
        "user_ids": user_ids
    }

    url = f'{url_base}/api/v1/user/delete'

    response = get_requests().post(
        url=url,
        json=post_data,
        headers=headers,
    )
    time.sleep(1)

    if response.status_code == 200:
        return response.json()
    else:
        return {"code": response.status_code, "message": response.reason}


def update_proxy(user_id: str, user_proxy: dict) -> dict:
    post_data = {
        "user_id": user_id,
        "group_id": "0",
        "user_proxy_config": user_proxy
    }

    url = f'{url_base}/api/v1/user/update'

    response = get_requests().post(
        url=url,
        json=post_data,
        headers=headers,
    )
    time.sleep(1)

    if response.status_code == 200:
        return response.json()
    else:
        return {"code": response.status_code, "message": response.reason}
