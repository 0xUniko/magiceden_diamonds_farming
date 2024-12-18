import json
import time
from typing import List

from api import get_requests
from api.local import *
from api.local.fingerprint import *
from config import config

url_base = config["fingerprint_service_url_base"]


def start(browser_id: str) -> dict:
    url = f"{url_base}/Fingerprint/Start?browserId={browser_id}"

    ticket = (
        get_requests()
        .get(
            url=url,
            headers=headers,
        )
        .text
    )

    return _get_result(ticket)


def stop(browser_id: str) -> dict:
    url = f"{url_base}/Fingerprint/Stop?browserId={browser_id}"

    ticket = (
        get_requests()
        .get(
            url=url,
            headers=headers,
        )
        .text
    )

    return _get_result(ticket)


def exist(browser_id: str) -> dict:
    url = f"{url_base}/Fingerprint/Exist?browserId={browser_id}"

    ticket = (
        get_requests()
        .get(
            url=url,
            headers=headers,
        )
        .text
    )

    return _get_result(ticket)


def active(browser_id: str) -> dict:
    url = f"{url_base}/Fingerprint/Active?browserId={browser_id}"

    ticket = (
        get_requests()
        .get(
            url=url,
            headers=headers,
        )
        .text
    )

    return _get_result(ticket)


def create(name: str) -> dict:
    post_data = {"name": name}

    url = f"{url_base}/Fingerprint/Create"

    ticket = (
        get_requests()
        .post(
            url=url,
            json=post_data,
            headers=headers,
        )
        .text
    )

    return _get_result(ticket)


def delete(browser_ids: List[str]) -> dict:
    post_data = {"browserIds": browser_ids}

    url = f"{url_base}/Fingerprint/Delete"

    ticket = (
        get_requests()
        .post(
            url=url,
            json=post_data,
            headers=headers,
        )
        .text
    )

    return _get_result(ticket)


def update_proxy(browser_id: str, user_proxy: dict) -> dict:
    post_data = {"browserId": browser_id, "userProxy": user_proxy}

    url = f"{url_base}/Fingerprint/UpdateProxy"
    ticket = get_requests().post(url, json=post_data, headers=headers).text
    return _get_result(ticket)


def _get_result(ticket: str) -> dict:
    url = f"{url_base}/Fingerprint/GetResult?ticket={ticket}"
    while True:
        response = get_requests().get(url).json()
        if response["result"] != "":
            try:
                return json.loads(response["result"])
            except:
                return {"code": 1, "message": response["result"]}
        else:
            time.sleep(1)
