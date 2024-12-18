import json
from typing import Optional

import httpx

import api.local.fingerprint.default
import api.remote.resource.fingerprint
import api.remote.resource.fingerprint_browser
from config import config
from fingerprint.browser import Browser
from fingerprint.browser_client import BrowserClient
from tools.logger import task_log


class DefaultClient(BrowserClient):
    def __init__(self, task_id: str) -> None:
        super().__init__(task_id)

        pass

    def login(self) -> bool:
        return True

    # def exists(self, name: str) -> bool:
    #     browser_id = self.__get_by_name__(name)
    #     response = api.local.fingerprint.default.exist(browser_id)
    #     response = api.local.fingerprint.default.exist(name)
    #     exist = len(response["data"]["list"]) > 0
    #     if not exist:
    #         response = api.remote.resource.fingerprint.modify_browser_id(
    #             name, "")
    #     return exist

    def exists(self, user_id: str):
        return (
            len(
                httpx.get(
                    "http://localhost:50325" + "/api/v1/user/list",
                    params={"user_id": user_id},
                ).json()["data"]["list"]
            )
            > 0
        )

    def start(
        self,
        name: str,
        user_proxy=None,
        is_incognito: bool = False,
    ) -> Optional[Browser]:
        # response = api.local.fingerprint.default.start(name)
        response = httpx.get(
            "http://localhost:50325/api/v1/browser/start", params={"user_id": name}
        ).json()
        if response["code"] == 0:
            webdriver = response["data"]["webdriver"]
            debugger_address = f'127.0.0.1:{response["data"]["debug_port"]}'
            count = 0
            while count < 10:
                # active_response = api.local.fingerprint.default.active(name)
                active_response = httpx.get(
                    "http://localhost:50325/api/v1/browser/active",
                    params={"user_id": name},
                ).json()
                if (
                    active_response["code"] == 0
                    and str(active_response["data"]["status"]).lower() == "active"
                ):
                    return self.get_browser(
                        name,
                        webdriver,
                        debugger_address,
                        user_proxy,
                    )
                else:
                    count += 1
        task_log(self.task_id, f"start error: {json.dumps(response)}")
        return None

    # def stop(self, name: str) -> bool:
    #     try:
    #         if self.browser is not None:
    #             self.browser.close()
    #         browser_id = self.__get_by_name__(name)
    #         if browser_id is not None:
    #             response = api.local.fingerprint.default.stop(browser_id)
    #             if response["code"] == 0:
    #                 return True
    #             task_log(self.task_id, f"stop error: {json.dumps(response)}")
    #             return False
    #         return True
    #     except Exception as e:
    #         task_log(self.task_id, f"stop error: {e}")
    #         return False

    def stop(self, user_id: str):
        return httpx.get(
            "http://localhost:50325" + "/api/v1/browser/stop",
            params={"user_id": user_id},
        ).json()

    def create(self, name: str) -> Optional[str]:
        if self.__get_by_name__(name) is None:
            response = api.local.fingerprint.default.create(name)
            if response["code"] == 0:
                browser_id = response["data"]["id"]
                response = api.remote.resource.fingerprint.modify_browser_id(
                    name, browser_id
                )
                if response["code"] != 0:
                    task_log(self.task_id, response["message"])
                return browser_id
            task_log(self.task_id, f"create browser error: {json.dumps(response)}")
            return None
        task_log(self.task_id, f"browser exists")
        return None

    def delete(self, name: str) -> bool:
        try:
            browser_id = self.__get_by_name__(name)
            if browser_id is not None:
                response = api.local.fingerprint.default.delete([browser_id])
                if response["code"] == 0:
                    response = api.remote.resource.fingerprint.modify_browser_id(
                        name, ""
                    )
                    return True
                task_log(self.task_id, f"delete error: {json.dumps(response)}")
                return False
            return True
        except Exception as e:
            task_log(self.task_id, f"delete error: {str(e)}")
            return False

    def update_proxy(self, name: str, user_proxy=None) -> bool:
        browser_id = self.__get_by_name__(name)
        if browser_id is not None:
            if user_proxy is not None:
                user_proxy_dict = config["fingerprint_proxy"]
                response = api.local.fingerprint.default.update_proxy(
                    browser_id, user_proxy_dict
                )
                if response["code"] == 0:
                    return True
                task_log(self.task_id, f"update_proxy error: {json.dumps(response)}")
        return False

    def create_and_start(
        self,
        name: str,
        user_proxy=None,
        is_incognito: bool = False,
    ) -> Optional[Browser]:
        if not self.exists(name):
            browser_id = self.create(name)
            if browser_id is None:
                return None
            return self.start(name, user_proxy)
        return None

    def delete_all(self) -> bool:
        return False
