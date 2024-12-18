import json
import logging
import os
import time
from enum import Enum
from typing import List, Optional, TypedDict

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import api.remote.resource.resource
from extensions.extension import Extension
from fingerprint.browser import Browser
from model import ChainId, ResourceType, role_data
from tools.logger import TaskLog, task_log


class Currency(TypedDict):
    name: str
    symbol: str
    decimals: int


class Chain(TypedDict):
    chainId: str  # 0x38
    chainName: str
    nativeCurrency: Currency
    rpcUrls: list[str]
    blockExplorerUrls: list[str]


class ActionType(Enum):
    UNKNOWN = 0
    CONNECT = 1
    SWITCH_TO_NETWORK = 2
    SIGN = 3
    APPROVE = 4
    TRANSACTION = 5


class OkxWeb3(Extension):
    def __init__(
        self, browser: Browser, task_id: str, config: dict | None = None
    ) -> None:
        super().__init__(browser, task_id, config)
        self.welcome_url = (
            f"chrome-extension://cdolfjcacbhaadmmkdnlbelpnnjhljfh/popup.html"
        )
        self.task_log = TaskLog(task_id)

    pass

    def enable(self):
        pass

    def active(self, role: role_data, mnemonics: str, password: str):
        self.browser.driver.switch_to.new_window("tab")
        self.browser.switch_to(-1)
        self.browser.initialized_get(self.welcome_url)
        import_wallet_btn = self.browser.find_element_and_until(
            "button.okui-btn.btn-xl.btn-outline-primary.block",
            EC.presence_of_element_located,
            timeout=5,
        )
        if import_wallet_btn is None:
            self.unlock(password)
        else:
            self.recover(
                str(mnemonics).split(" "),
                password,
            )
        self.browser.clean_tabs()
        pass

    def load(self, role: role_data):
        self.load_extension(role, "okxweb3", ChainId.ETH_ETHEREUM)
        pass

    def unlock(self, password: str):
        self.task_log.info("okxweb3 wallet unlock")
        password_input_element = self.browser.find_element_and_wait("input")
        self.browser.send_keys(password_input_element, password)
        unlock_button_element = self.browser.find_element_and_wait("button")
        self.browser.click(unlock_button_element)
        self.browser.wait(1, 3)
        self.task_log.info("okxweb3 wallet unlock completed")
        pass

    def recover(self, mnemonics: List[str], password: str) -> None:
        self.task_log.info("okxweb3 recover")
        self.browser.get(self.welcome_url + "#initialize-import")
        okd_popup_list = self.browser.find_elements_and_wait(
            'div[data-testid="okd-popup"]'
        )
        self.browser.click(okd_popup_list[1])
        input_list: List[dict] = []
        for i, input in enumerate(
            self.browser.find_elements_and_wait(
                "input.mnemonic-words-inputs__container__input"
            )
        ):
            input_item = {"input": input, "mnemonic": mnemonics[i]}
            input_list.insert(0, input_item)
        for item in input_list:
            self.browser.send_keys(item["input"], item["mnemonic"], True)
        submit_btn = self.browser.find_element_and_wait('button[type="submit"]')
        self.browser.click(submit_btn)
        for password_input in self.browser.find_elements_and_wait(
            'input[type="password"]'
        ):
            self.browser.send_keys(password_input, password, True)
        submit_btn = self.browser.find_element_and_wait('button[type="submit"]')
        submit_btn.click()
        self.browser.wait(3, 5)
        try:
            confirm_button_elements = self.browser.find_elements_and_wait("button")
            self.browser.click(confirm_button_elements[0])
            self.browser.wait(1, 3)
            confirm_button_elements = self.browser.find_elements_and_wait("button")
            self.browser.click(confirm_button_elements[-1])
            self.browser.wait(1, 3)
        except:
            self.task_log.warn("okxweb3 confirm recover error")
        self.task_log.info("okxweb3 recover completed")
        pass

    def connect(self, timeout: int = 5) -> None:
        if not self.browser.wait_tabs(2, timeout=timeout):
            task_log(
                self.task_id, f"Wait okxweb3 connect timeout or no need to connect"
            )
            return
        self.browser.switch_to(-1)
        button_elements = self.browser.find_elements_and_wait("button")
        self.browser.click(button_elements[-1])
        self.browser.switch_tabs(0)
        self.browser.wait(3, 5)
        pass

    def confirm(self, timeout: int = 5) -> None:
        if not self.browser.wait_tabs(2, timeout=timeout):
            task_log(self.task_id, f"Wait okxweb3 timeout")
            return
        for i in range(10):
            if len(self.browser.driver.window_handles) == 2:
                task_log(self.task_id, f"Start to confirm: {i}")
                self.browser.switch_to(-1)
                button_elements = self.browser.find_elements_and_wait("button")
                self.browser.click(button_elements[-1])
                time.sleep(2)
            else:
                break
        self.browser.switch_to(0)
        task_log(self.task_id, "Finish confirming")

    def sign(self, timeout: int = 5) -> None:
        time.sleep(2)
        if not self.browser.wait_tabs(2, timeout=timeout):
            task_log(self.task_id, f"Wait okxweb3 timeout")
            return
        task_log(self.task_id, "Start to sign")
        self.browser.switch_to(-1)
        button_elements = self.browser.find_elements_and_wait("button")
        self.browser.click(button_elements[-1])
        self.browser.switch_to(0)
        task_log(self.task_id, "Finish signing")

    def switch_to_all_networks_on_ui(self):
        self.browser.driver.switch_to.new_window("tab")
        self.browser.switch_to(-1)
        self.browser.initialized_get(self.welcome_url)
        # TODO: ATTENTION: this class name might change!!!
        current_network_btn = self.browser.find_element_and_wait(
            "div._currentNetwork_knly2_63"
        )
        self.browser.click(current_network_btn)
        all_networks_tab_pane = self.browser.find_element_and_wait(
            "div.okui-tabs-pane.okui-tabs-pane-spacing.okui-tabs-pane-xl.okui-tabs-pane-grey.okui-tabs-pane-underline.okui-tabs-pane-no-padding"
        )
        self.browser.click(all_networks_tab_pane)
        time.sleep(2)
        all_network = self.browser.find_element_and_wait(
            "div.okui-virtual-list-holder-inner"
        ).find_element(By.CSS_SELECTOR, "div")
        self.browser.click(all_network)
        time.sleep(4)

    # def sign(self) -> None:
    #     task_log(self.task_id, "Start sign to okxweb3")
    #     self.browser.switch_to(-1)
    #     self.browser.driver.maximize_window()
    #     try:
    #         scroll_element = self.browser.find_element_and_until(
    #             "div[data-testid='signature-request-scroll-button']",
    #             EC.element_to_be_clickable,
    #             timeout=2,
    #         )
    #         if scroll_element:
    #             self.browser.click(scroll_element)
    #             self.browser.wait(1, 2)

    #         button_elements = self.browser.find_elements_and_wait("button")
    #         self.browser.click(button_elements[-1])
    #         task_log(self.task_id, "Finish sign to okxweb3")
    #     except Exception as e:
    #         task_log(self.task_id, str(e))
    #     finally:
    #         self.browser.switch_to(0)
    #         self.browser.wait(1, 3)
    #     pass
