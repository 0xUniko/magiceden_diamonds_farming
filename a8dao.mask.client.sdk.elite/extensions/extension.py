import json
from abc import ABC, abstractmethod

from selenium.webdriver.common.by import By

import api.remote.resource.resource
from fingerprint.browser import Browser
from model import ChainId, ResourceType, role_data
from tools.logger import task_log


class Extension(ABC):
    def __init__(
        self, browser: Browser, task_id: str, config: dict | None = None
    ) -> None:
        self.browser = browser
        self.task_id = task_id
        self.config = config

        super().__init__()
        pass

    def enable(self, name: str) -> bool:
        self.browser.driver.switch_to.new_window("tab")
        self.browser.get(
            "chrome-extension://eepfmglhkpmnfmjeknncjanfobgjhdco/plugins.html"
        )
        tab_elements = self.browser.find_elements_and_wait(".ant-tabs-tab")
        tab_elements[1].click()
        extension_elements = self.browser.find_elements("main div div div")
        for extension_element in extension_elements:
            if name in extension_element.text:
                buttons = extension_element.parent.parent.find_elements(
                    By.CSS_SELECTOR, "button"
                )
                if len(buttons) > 0:
                    buttons[0].click()
                return True
        return False

    @abstractmethod
    def active(self, role: role_data, mnemonics: str, password: str):
        pass

    @abstractmethod
    def load(self, role: role_data):
        pass

    def load_extension(self, role: role_data, extension_name: str, chain_id: ChainId):
        if role["fingerprint_data"]["extend_information"] == {}:
            role["fingerprint_data"]["extend_information"] = {
                "extensions": {extension_name: {"initialize": False}}
            }
        if "extensions" not in role["fingerprint_data"]["extend_information"]:
            role["fingerprint_data"]["extend_information"]["extensions"] = {
                extension_name: {"initialize": False}
            }
        if (
            extension_name
            not in role["fingerprint_data"]["extend_information"]["extensions"]
        ):
            role["fingerprint_data"]["extend_information"]["extensions"][
                extension_name
            ] = {"initialize": False}

        wallet_mainnet = [
            w for w in role["wallet_data"] if w["chain_id"] == chain_id.value
        ][0]
        self.active(
            role, wallet_mainnet["mnemonic"], wallet_mainnet["metamask_password"]
        )
        role["fingerprint_data"]["extend_information"]["extensions"][extension_name][
            "initialize"
        ] = True
        try:
            extend_infomation = api.remote.resource.resource.ExtendInformation()
            extend_infomation["extend_information"] = role["fingerprint_data"][
                "extend_information"
            ]
            extend_infomation["resource_id"] = role["fingerprint_data"]["id"]
            extend_infomation["resource_type_code"] = ResourceType.fingerprint
            api.remote.resource.resource.save_extend_information(
                extend_infomation)
        except Exception as e:
            task_log(self.task_id, str(e))
        pass
