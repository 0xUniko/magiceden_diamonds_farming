import json
import random
from typing import List, Optional
import requests
from api.local.fingerprint import *
from api.local import *
from proxies.models import UserProxy
import time

hubstudio_config = fingerprint_config["hubstudio"]
url_base = f'{host}:{hubstudio_config["port"]}'


def login(post_data: dict, loop_count: int = 30) -> dict:
    while_count = 0
    while True:
        response = requests.post(
            url=f'{url_base}{hubstudio_config["login"]}',
            json=post_data,
            headers=headers,
        )
        if response.status_code == 200 and response.json()["code"] == 0:
            return response.json()
        elif while_count == loop_count:
            return {"code": response.status_code, "message": response.reason}
        else:
            while_count += 1
            time.sleep(random.randint(1, 5))


def start(containerCode: str, is_incognito: bool = False, loop_count: int = 30) -> dict:
    post_data = {
        "containerCode": containerCode,
        "isWebDriverReadOnlyMode": False,
        "args": ["--whitelisted-ips"],
    }
    if is_incognito:
        post_data["args"] = ["--whitelisted-ips", "--incognito"]
    while_count = 0
    while True:
        response = requests.post(
            url=f'{url_base}{hubstudio_config["start"]}',
            json=post_data,
            headers=headers,
        )
        print(
            f"start post done,response_status_code:{response.status_code},response_json:{json.dumps(response.json())}"
        )
        if response.status_code == 200 or response.json()["code"] == 0:
            return response.json()
        elif while_count == loop_count:
            return {"code": response.status_code, "message": response.reason}
        else:
            while_count += 1
            time.sleep(random.randint(1, 5))


def stop(containerCode: str, loop_count: int = 30) -> dict:
    post_data = {
        "containerCode": containerCode,
    }
    while_count = 0
    while True:
        response = requests.post(
            url=f'{url_base}{hubstudio_config["stop"]}',
            json=post_data,
            headers=headers,
        )
        print(
            f"stop post done,response_status_code:{response.status_code},response_json:{json.dumps(response.json())}"
        )
        if response.status_code == 200 or response.json()["code"] == 0:
            return response.json()
        elif while_count == loop_count:
            return {"code": response.status_code, "message": response.reason}
        else:
            while_count += 1
            time.sleep(random.randint(1, 5))


def status(containerCode: str, loop_count: int = 30) -> dict:
    post_data = {
        "containerCodes": [containerCode],
    }
    while_count = 0
    while True:
        response = requests.post(
            url=f'{url_base}{hubstudio_config["status"]}',
            json=post_data,
            headers=headers,
        )
        print(
            f"status post done,response_status_code:{response.status_code},response_json:{json.dumps(response.json())}"
        )
        if response.status_code == 200 or response.json()["code"] == 0:
            return response.json()
        elif while_count == loop_count:
            return {"code": response.status_code, "message": response.reason}
        else:
            while_count += 1
        time.sleep(random.randint(1, 5))


def list(containerName: Optional[str] = None, loop_count: int = 30) -> dict:
    post_data = {}
    if containerName is not None:
        post_data["containerName"] = containerName
    while_count = 0
    while True:
        response = requests.post(
            url=f'{url_base}{hubstudio_config["list"]}',
            json=post_data,
            headers=headers,
        )
        print(
            f"list post done,response_status_code:{response.status_code},response_json:{json.dumps(response.json())}"
        )
        if response.status_code == 200 or response.json()["code"] == 0:
            return response.json()
        elif while_count == loop_count:
            return {"code": response.status_code, "message": response.reason}
        else:
            while_count += 1
            time.sleep(random.randint(1, 5))


def create(containerName: str, ua_version: str, loop_count: int = 30) -> dict:
    post_data = {
        "containerName": containerName,
        "advancedBo": {
            "languageType": 1,
            "uiLanguage": "en",
            "languages": ["en"],
            "uaVersion": ua_version,
        },
        "asDynamicType": 2,
        "proxyTypeName": "不使用代理",
    }
    while_count = 0
    while True:
        response = requests.post(
            url=f'{url_base}{hubstudio_config["create"]}',
            json=post_data,
            headers=headers,
        )
        print(
            f"create post done,response_status_code:{response.status_code},response_json:{json.dumps(response.json())}"
        )
        if response.status_code == 200 or response.json()["code"] == 0:
            return response.json()
        elif while_count == loop_count:
            return {"code": response.status_code, "message": response.reason}
        else:
            while_count += 1
            time.sleep(random.randint(1, 5))


def delete(containerCodes: List[str], loop_count: int = 30) -> dict:
    post_data = {
        "containerCodes": containerCodes,
    }
    while_count = 0
    while True:
        response = requests.post(
            url=f'{url_base}{hubstudio_config["delete"]}',
            json=post_data,
            headers=headers,
        )
        print(
            f"delete post done,response_status_code:{response.status_code},response_json:{json.dumps(response.json())}"
        )
        if response.status_code == 200 or response.json()["code"] == 0:
            return response.json()
        elif while_count == loop_count:
            return {"code": response.status_code, "message": response.reason}
        else:
            while_count += 1
            time.sleep(random.randint(1, 5))


def update_proxy(
    containerCode: str, user_proxy: UserProxy, loop_count: int = 30
) -> dict:
    post_data = {
        "containerCode": containerCode,
        "asDynamicType": 2,
        "proxyTypeName": user_proxy.protocol.upper(),
        "proxyHost": user_proxy.host,
        "proxyPort": user_proxy.port,
    }
    if user_proxy.user_name is not None:
        post_data["proxyAccount"] = user_proxy.user_name
    if user_proxy.password is not None:
        post_data["proxyPassword"] = user_proxy.password
    while_count = 0
    while True:
        response = requests.post(
            url=f'{url_base}{hubstudio_config["update_proxy"]}',
            json=post_data,
            headers=headers,
        )
        print(
            f"update_proxy post done,response_status_code:{response.status_code},response_json:{json.dumps(response.json())}"
        )
        if response.status_code == 200 or response.json()["code"] == 0:
            return response.json()
        elif while_count == loop_count:
            return {"code": response.status_code, "message": response.reason}
        else:
            while_count += 1
            time.sleep(random.randint(1, 5))
