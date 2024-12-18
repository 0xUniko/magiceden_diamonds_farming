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
from tools.logger import task_log


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


class MetaMask(Extension):
    def __init__(self, browser: Browser, task_id: str, config: dict = None) -> None:
        super().__init__(browser, task_id, config)
        self.extension_name = self.load_extension_name()
        self.welcome_url = (
            f"chrome-extension://{self.extension_name}/home.html#onboarding/welcome"
        )
        pass

    def load_extension_name(self) -> str:
        env_path = "configs/extensions/metamask.json"
        with open(env_path, "r", encoding="UTF-8") as f:
            extension_config: dict = json.load(f)
            name = extension_config["name"]
            return name
    pass

    def enable(self):
        pass

    def active(self, role: role_data, mnemonics: str, password: str):
        self.browser.initialized_get(self.welcome_url)
        unlock_button_element = self.browser.find_element_and_until(
            "button[data-testid='unlock-submit']",
            EC.presence_of_element_located,
            timeout=5,
        )
        if unlock_button_element is not None:
            self.unlock(password)
        else:
            self.recover(
                str(mnemonics).split(" "),
                password,
            )
        pass

    def load(self, role: role_data):
        self.load_extension(role, "metamask", ChainId.ETH_ETHEREUM)
        pass

    def get_action(self) -> ActionType:
        self.browser.switch_to(-1)
        self.browser.wait(1, 3)
        if len(self.browser.find_elements(".confirm-approve-content")) > 0:
            return ActionType.APPROVE
        if len(self.browser.find_elements(".signature-request-content")) > 0:
            return ActionType.SIGN
        if len(self.browser.find_elements(".confirm-page-container-content")) > 0:
            return ActionType.TRANSACTION
        if len(self.browser.find_elements(".permissions-connect")) > 0:
            return ActionType.CONNECT
        if len(self.browser.find_elements(".network-droppo")) > 0:
            return ActionType.SWITCH_TO_NETWORK
        return ActionType.UNKNOWN

    def approve(self):
        task_log(self.task_id, "Start approve to metamask")
        self.browser.switch_to(-1)
        try:
            self.browser.driver.maximize_window()
            button_element = self.browser.find_elements_and_wait("button")[-1]
            while True:
                if not button_element.is_enabled():
                    task_log(
                        self.task_id, "confirm button not enabled, try later again"
                    )
                    self.browser.wait(1, 3)
                else:
                    self.browser.click(button_element)
                    break
            self.browser.wait(1, 3)
            if (
                len(
                    self.browser.find_elements_and_wait(
                        css_selector="#popover-content", timeout=3
                    )
                )
                > 0
            ):
                section_element = self.browser.find_element("section")
                if section_element:
                    class_list = section_element.get_dom_attribute(
                        "class").split(" ")
                    if "set-approval-for-all-warning__content" in class_list:
                        button_elements = self.browser.find_elements_and_wait(
                            "section button"
                        )
                        conform_button_element = [
                            b for b in button_elements if b.text == "Approve"
                        ][0]
                        while True:
                            if not conform_button_element.is_enabled():
                                task_log(
                                    self.task_id,
                                    "approve button not enabled, try later again",
                                )
                                self.browser.wait(1, 3)
                            else:
                                self.browser.click(conform_button_element)
                                break
                        self.browser.wait(1, 3)
            task_log(self.task_id, "Finish approve to metamask")
        except Exception as e:
            task_log(self.task_id, str(e))
        finally:
            self.browser.switch_to(0)
            self.browser.wait(1, 3)
        pass

    def confirm_and_approve(self):
        task_log(self.task_id, "confirm to metamask")
        self.browser.switch_to(-1)
        try:
            self.browser.driver.maximize_window()
            if self.welcome_url[:50] in self.browser.driver.current_url:
                button_element = self.browser.find_elements_and_wait(
                    "button")[-1]
                while not button_element.is_enabled():
                    self.browser.wait(1, 3)
                self.browser.click(button_element)
                self.browser.wait(1, 3)

                button_element = self.browser.find_element_and_wait(
                    "#popover-content button.btn-danger-primary"
                )
                while not button_element.is_enabled():
                    self.browser.wait(1, 3)
                self.browser.click(button_element)
                self.browser.wait(1, 3)
        except Exception as e:
            task_log(self.task_id, str(e))
        self.browser.switch_to(0)
        self.browser.wait(1, 3)
        pass

    def confirm(self):
        task_log(self.task_id, "Start confirm to metamask")
        count = 0
        while count < 10:
            self.browser.switch_to(-1)
            size1 = json.dumps(self.browser.driver.get_window_size())
            self.browser.driver.maximize_window()
            size2 = json.dumps(self.browser.driver.get_window_size())
            if size1 != size2:
                break
            task_log(self.task_id, f"Can not resize metamask window,{size2}")
            time.sleep(3)
            count += 1
        try:
            button_elements = self.browser.find_elements_and_wait("button")
            while True:
                if not button_elements[-1].is_enabled():
                    self.browser.wait(1, 3)
                else:
                    button_elements[-1].click()
                    self.browser.wait(1, 3)
                    break
            task_log(self.task_id, "Finish confirm to metamask")
        except Exception as e:
            task_log(self.task_id, str(e))
        finally:
            self.browser.switch_to()
            self.browser.wait(1, 3)
        pass

    def unlock(self, password: str):
        current_window_handle = self.browser.driver.current_window_handle
        self.browser.driver.switch_to.new_window("tab")
        self.browser.get(self.welcome_url)
        time.sleep(3)
        if len(self.browser.find_elements(".unlock-page")) > 0:
            WebDriverWait(self.browser.driver, timeout=30).until(
                EC.presence_of_element_located((By.ID, "password"))
            )
            password_input = self.browser.driver.find_element(
                By.ID, "password")
            password_input.send_keys(password)
            time.sleep(0.1)
            unlock_button = self.browser.driver.find_element(
                By.CSS_SELECTOR, "button")
            unlock_button.click()
            time.sleep(2)
        self.browser.driver.close()
        self.browser.driver.switch_to.window(current_window_handle)
        # return
        # else:
        #     if time.time() > t + 10:
        #         return
        # todo 需要确认下一个界面

    def __import_wallet__(self):
        task_log(self.task_id, "import wallet")
        self.browser.wait_document_load_complete()
        # agree_checkbox_element = self.browser.driver.find_element(
        #     By.CSS_SELECTOR, "#onboarding__terms-checkbox"
        # )
        # assert agree_checkbox_element is not None
        # agree_checkbox_element.click()
        # time.sleep(1)

        for i in range(11):
            try:
                import_wallet_buttons = self.browser.driver.find_elements(
                    By.CSS_SELECTOR, ".button"
                )
                if len(import_wallet_buttons) > 1:
                    import_wallet_buttons[1].click()
                    time.sleep(1)
                    return self
            except Exception as e:
                task_log(self.task_id, str(e), 2)
                time.sleep(1)
            if i == 10:
                raise Exception(
                    f"import wallet error,import_wallet_buttons=0,retry count = 10"
                )

    def __i_agree__(self):
        task_log(self.task_id, "click i agree")
        self.browser.wait_document_load_complete()
        i_agree_button = self.browser.driver.find_elements(
            By.CSS_SELECTOR, "button")[0]
        i_agree_button.click()
        time.sleep(0.5)
        return self

    def __recovery_phrase__(self, mnemonics: List[str]):
        task_log(self.task_id, "recovery phrase")
        self.browser.wait_document_load_complete()
        mnemonic_inputs = self.browser.driver.find_elements(
            By.CSS_SELECTOR, ".MuiInput-input"
        )
        for i in range(len(mnemonic_inputs)):
            mnemonic_inputs[i].send_keys(mnemonics[i])
            time.sleep(0.1)

        submit_button = self.browser.driver.find_element(
            By.CSS_SELECTOR, "button")
        submit_button.click()
        time.sleep(0.5)
        return self

    def __create_password__(self, password: str):
        task_log(self.task_id, "create password")
        self.browser.wait_document_load_complete()
        password_inputs = self.browser.driver.find_elements(
            By.CSS_SELECTOR, ".form-field__input"
        )
        for input in password_inputs:
            input.send_keys(password)
            time.sleep(0.1)

        checkbox = self.browser.driver.find_element(
            By.CSS_SELECTOR, ".check-box")
        checkbox.click()
        time.sleep(0.1)
        submit_button = self.browser.driver.find_element(
            By.CSS_SELECTOR, "button")
        submit_button.click()
        time.sleep(0.5)
        return self

    def __completion__(self) -> None:
        task_log(self.task_id, "completion")
        self.browser.wait_document_load_complete()
        while True:
            if (
                len(self.browser.driver.find_elements(
                    By.CSS_SELECTOR, ".lds-spinner"))
                > 0
            ):
                time.sleep(1)
            else:
                buttons = self.browser.driver.find_elements(
                    By.CSS_SELECTOR, "button")
                if len(buttons) > 0 and buttons[0]:
                    buttons[0].click()
                    break
        self.browser.wait_document_load_complete()
        time.sleep(1)
        self.browser.driver.find_elements(
            By.CSS_SELECTOR, "button")[-1].click()
        self.browser.wait_document_load_complete()
        time.sleep(1)
        self.browser.driver.find_elements(
            By.CSS_SELECTOR, "button")[-1].click()
        time.sleep(2)
        # button_elements = self.browser.find_elements_and_wait(
        #     ".popover-wrap.whats-new-popup__popover button"
        # )
        # self.browser.click(button_elements[0])
        # time.sleep(2)
        self.browser.wait_document_load_complete()
        time.sleep(2)
        pass

    def recover(self, mnemonics: List[str], password: str) -> None:
        task_log(self.task_id, "start")
        self.browser.clean_tabs()
        self.browser.get(self.welcome_url)
        self.__import_wallet__().__i_agree__().__recovery_phrase__(
            mnemonics
        ).__create_password__(password).__completion__()
        pass

    def add_and_switch_network(self) -> None:
        task_log(self.task_id, "Start add and switch network")
        self.browser.switch_to(-1)
        self.browser.driver.maximize_window()
        try:
            button_elements = self.browser.find_elements_and_wait("button")
            switch_button_element = button_elements[-1]
            while not switch_button_element.is_enabled():
                self.browser.wait(1, 3)
            self.browser.click(switch_button_element)
            task_log(self.task_id, "Finish add and switch network")
        except Exception as e:
            task_log(self.task_id, str(e))
        finally:
            self.browser.switch_to(0)
            self.browser.wait(1, 3)
        pass

    def add_and_switch_network_by_chain_params(self, chain: Chain):
        task_log(self.task_id,
                 f"add_and_switch_network_by_chain_params: {str(chain)}")
        self.browser.initialized_get("https://www.google.com")
        if self.chain_id != chain["chainId"]:
            if chain["chainId"] == "0x1":
                self.browser.driver.execute_script(
                    "ethereum.request({ method: 'wallet_switchEthereumChain', params: [{ chainId: '0x1' }] })"
                )
            else:
                self.browser.driver.execute_script(
                    f"ethereum.request({{method: 'wallet_addEthereumChain', params:[{json.dumps(chain)}]}})"
                )
            WebDriverWait(self.browser.driver, timeout=30).until(
                lambda d: len(d.window_handles) == 2
            )
            self.browser.switch_to(-1)
            self.browser.find_element_and_wait(".btn-primary").click()
            time.sleep(1)
            try:
                self.browser.find_element_and_wait(".btn-primary").click()
                time.sleep(1)
            except:
                pass
            self.browser.switch_to()
            self.browser.get(self.welcome_url)
            tippy_tooltip_content = self.browser.find_element_and_until(
                ".tippy-tooltip-content", EC.visibility_of_element_located, 2
            )
            if tippy_tooltip_content:
                self.browser.click(
                    self.browser.find_element_and_wait("i.fa.fa-times"))
            popover_content = self.browser.find_element_and_until(
                "#popover-content", EC.visibility_of_element_located, 2
            )
            if popover_content:
                self.browser.click(
                    self.browser.find_element_and_wait(
                        'button.button.btn-primary[role="button"]'
                    )
                )
        else:
            task_log(self.task_id, "already on this chain")

    def click(self, timeout: int = 5) -> None:
        while True:
            if not self.browser.wait_tabs(2, timeout=timeout):
                task_log(self.task_id,
                         f"Wait metamask timeout or no need to wait")
                break
            self.browser.switch_to(-1)
            action = self.get_action()
            match action:
                case ActionType.CONNECT:
                    self.connect()
                case ActionType.SIGN:
                    self.sign()
                case ActionType.TRANSACTION:
                    self.confirm()
                case ActionType.APPROVE:
                    self.approve()
                case ActionType.SWITCH_TO_NETWORK:
                    self.add_and_switch_network()
                case ActionType.UNKNOWN:
                    task_log(self.task_id,
                             "Unknown action type,catch the html content")
                    task_log(self.task_id, self.browser.driver.page_source)
                    raise (Exception("Unknown action type"))
            self.browser.wait(1, 3)
        pass

    def connect(self) -> None:
        task_log(self.task_id, "Start connect to metamask")
        self.browser.switch_to(-1)
        try:
            self.browser.driver.maximize_window()
            button_element = self.browser.find_element_and_wait(".btn-primary")
            while not button_element.is_enabled():
                self.browser.wait(1, 3)
            self.browser.click(button_element, is_element_click=True)
            self.browser.wait(1, 3)

            if len(self.browser.driver.window_handles) == 2:
                self.browser.switch_to(-1)
                self.browser.driver.maximize_window()
                button_element = self.browser.find_element_and_wait(
                    ".btn-primary")
                while not button_element.is_enabled():
                    self.browser.wait(1, 3)

                self.browser.click(button_element, is_element_click=True)
                self.browser.wait(1, 3)
            task_log(self.task_id, "Finish connect to metamask")
        except Exception as e:
            task_log(self.task_id, str(e))
        finally:
            self.browser.switch_to(0)
            self.browser.wait(1, 3)
        pass

    def is_sign(self) -> bool:
        self.browser.switch_to(-1)
        self.browser.driver.maximize_window()
        try:
            button_element = self.browser.find_element_and_wait(
                "[data-testid='signature-sign-button']"
            )
            if button_element:
                self.browser.wait(1, 3)
                self.browser.switch_to()
                return True
        except:
            time.sleep(1)
        self.browser.wait(1, 3)
        self.browser.switch_to()
        return False

    def sign(self) -> None:
        task_log(self.task_id, "Start sign to metamask")
        self.browser.switch_to(-1)
        self.browser.driver.maximize_window()
        try:
            scroll_element = self.browser.find_element_and_until(
                "div[data-testid='signature-request-scroll-button']",
                EC.element_to_be_clickable,
                timeout=5,
            )
            if scroll_element:
                self.browser.click(scroll_element)
                self.browser.wait(1, 3)

            button_elements = self.browser.find_elements_and_wait("button")
            self.browser.click(button_elements[-1])
            task_log(self.task_id, "Finish sign to metamask")
        except Exception as e:
            task_log(self.task_id, str(e))
        finally:
            self.browser.switch_to(0)
            self.browser.wait(1, 3)
        pass

    @property
    def chain_id(self):
        WebDriverWait(self.browser.driver, timeout=10).until(
            lambda d: d.execute_script(
                "return typeof window.ethereum !== 'undefined'")
        )
        return self.browser.driver.execute_script(
            'return await window.ethereum.request({ method: "eth_chainId" })'
        )

    def switch_to_network(self, chain_id: ChainId):
        with open("configs/extensions/metamask.json", "r") as f:
            data = json.loads(f.read())
            network = data[chain_id.name]
            self.add_and_switch_network_by_chain_params(network)

    def switch_to_zks(self):
        if self.chain_id != "0x144":
            self.add_and_switch_network_by_chain_params(
                {
                    "chainId": "0x144",
                    "chainName": "zkSync Era Mainnet",
                    "rpcUrls": ["https://mainnet.era.zksync.io"],
                    "nativeCurrency": {
                        "name": "Ether",
                        "symbol": "ETH",
                        "decimals": 18,
                    },
                    "blockExplorerUrls": ["https://explorer.zksync.io"],
                }
            )
