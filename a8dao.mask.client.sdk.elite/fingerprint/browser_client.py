from abc import ABC, abstractmethod
from typing import Optional
from fingerprint.browser import Browser
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import api.remote.resource.fingerprint


class BrowserClient(ABC):
    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        self.request_headers = {"Content-Type": "application/json"}
        pass

    @abstractmethod
    def login(self) -> bool:
        pass

    @abstractmethod
    def exists(self, name: str) -> bool:
        pass

    @abstractmethod
    def start(
        self,
        name: str,
        user_proxy= None,
        is_incognito: bool = False,
    ) -> Optional[Browser]:
        pass

    @abstractmethod
    def stop(self, name: str) -> bool:
        pass

    @abstractmethod
    def create(self, name: str) -> Optional[str]:
        pass

    @abstractmethod
    def delete(self, name: str) -> bool:
        pass

    @abstractmethod
    def update_proxy(self, name: str, user_proxy) -> bool:
        pass

    @abstractmethod
    def create_and_start(
        self,
        name: str,
        user_proxy = None,
        is_incognito: bool = False,
    ) -> Optional[Browser]:
        pass

    @abstractmethod
    def delete_all(self) -> None:
        pass

    def get_browser(
        self,
        name: str,
        web_driver: str,
        debugger_address: str,
        user_proxy,
    ) -> Browser:
        options = Options()
        options.add_experimental_option("debuggerAddress", debugger_address)
        options.set_capability("goog:loggingPrefs", {"performance": "ALL"})
        service = Service(web_driver)

        driver = webdriver.Chrome(service=service, options=options)
        driver.maximize_window()
        self.browser = Browser(name, driver, user_proxy)
        return self.browser

    def __get_by_name__(self, name: str) -> Optional[str]:
        response = api.remote.resource.fingerprint.get_by_fingerprint_name(
            name)
        if response["code"] == 0 and response["data"]["data"]["browser_id"] is not None and response["data"]["data"]["browser_id"] != "":
            return response["data"]["data"]["browser_id"]
        else:
            return None
