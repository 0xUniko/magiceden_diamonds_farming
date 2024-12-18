import base64
import hmac
import json
from datetime import datetime
from typing import Literal
from urllib.parse import urlencode

import httpx

from config import config


class OkxAPI:
    def __init__(self, task_id: str):
        self.task_id = task_id
        self.api_key: str = config["okx_dev_key"]["apiKey"]
        self.secret_key: str = config["okx_dev_key"]["secretKey"]
        self.passphrase: str = config["okx_dev_key"]["passphrase"]

    def send_request(
        self,
        path: str,
        json_data: dict,
        http_method: Literal["post"] | Literal["get"] = "post",
    ):
        json_data = {k: v for k, v in json_data.items() if v is not None}
        timestamp = datetime.utcnow().isoformat("T", "milliseconds") + "Z"
        headers_params = {
            "Content-Type": "application/json",
            "OK-ACCESS-KEY": self.api_key,
            "OK-ACCESS-SIGN": base64.b64encode(
                hmac.new(
                    self.secret_key.encode("utf8"),
                    (
                        timestamp
                        + http_method.upper()
                        + path
                        + (("?" + urlencode(json_data)) if http_method == "get" else "")
                        + (json.dumps(json_data) if http_method == "post" else "")
                    ).encode("utf8"),
                    digestmod="sha256",
                ).digest()
            ).decode(),
            "OK-ACCESS-TIMESTAMP": timestamp,
            "OK-ACCESS-PASSPHRASE": self.passphrase,
        }

        if http_method == "get":
            res = httpx.get(
                "https://www.okx.com" + path,
                params=json_data,
                headers=headers_params,
            ).json()
        else:
            res = httpx.post(
                "https://www.okx.com" + path,
                json=json_data,
                headers=headers_params,
            ).json()
        assert res["code"] == 0, f"failed to send request: {res['msg']}"
        return res["data"]
