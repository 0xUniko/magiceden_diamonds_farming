import hashlib
import re
import time
import uuid
from typing import Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

import api.remote.resource.sms
import tools.text
from api.remote.resource.aigc import extract_verification_code
from extensions.metamask import MetaMask
from fingerprint.browser import Browser
from tools.imap import Imap
from tools.logger import task_log
from selenium.webdriver.remote.webelement import WebElement


class ZksBridge:
    def __init__(self, task_id: str, browser: Browser, metamask: MetaMask) -> None:
        self.task_id = task_id
        self.browser = browser
        self.metamask = metamask
        pass

    def home(self):
        task_log(self.task_id, "go to https://portal.zksync.io/bridge/")
        self.browser.get("https://portal.zksync.io/bridge/")
        self.browser.wait(3, 5)
        self.browser.find_element_and_until(
            "button.default-button.variant-primary", EC.element_to_be_clickable)
        pass

    def connect_metamask(self):
        connect_wallet_button_element = self.browser.find_element_and_until(
            "button.default-button.variant-primary", EC.element_to_be_clickable)
        self.browser.click(connect_wallet_button_element)
        shadow_segments = ["w3m-modal", "w3m-modal-router",
                           "w3m-connect-wallet-view", "w3m-desktop-wallet-selection"]
        wallet_button_elements = self.browser.find_elements_with_shadow_root(
            shadow_segments, "w3m-modal-footer w3m-wallet-button[name='MetaMask']")
        assert len(wallet_button_elements) > 0, "Can not find metamask button"
        self.browser.click(wallet_button_elements[0])
        if not self.browser.wait_tabs(2):
            raise Exception("Can not connect wallet")
        self.metamask.connect()
        self.browser.wait(3, 5)
        pass

    def deposit(self, amount: float):
        task_log(self.task_id, "deposit eth to zksync era")
        self.browser.driver.execute_script(
            "ethereum.request({method: 'wallet_addEthereumChain', params:[{ chainId: '0x1' }]})"
        )
        WebDriverWait(self.browser.driver, 180).until_not(
            EC.presence_of_element_located(
                (By.CLASS_NAME, "token-balance-loading"))
        )
        self.browser.find_element_and_wait(
            "amount", By.NAME, 180).send_keys(amount)
        WebDriverWait(self.browser.driver, 180).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, ".button.contained.primary.lg.w-full")
            )
        ).click()
        self.browser.wait_tabs(2)
        self.metamask.confirm()
        pass

    def deposit_max(self) -> str:
        task_log(self.task_id, "Start deposit eth to zksync era")
        while True:
            max_button_element = self.browser.find_element_and_until(
                ".amount-input-max-button", EC.element_to_be_clickable)
            self.browser.click(max_button_element)
            submit_button_element = self.browser.find_element_and_until(
                "button[type='submit']", EC.element_to_be_clickable, timeout=180)
            self.browser.click(submit_button_element)
            confirm_button_element = self.browser.find_element_and_until(
                ".default-button.variant-primary-solid.mx-auto", EC.element_to_be_clickable)
            self.browser.click(confirm_button_element)
            if self.browser.wait_tabs(2):
                break
            else:
                task_log(self.task_id, "Fee changed, retry")
                self.home()
        self.metamask.confirm()
        self.browser.wait(3, 5)
        tx_element = self.browser.find_element_and_until(
            ".line-button-container.line-button-with-img.transaction-line-item", EC.presence_of_element_located)
        tx = tx_element.get_attribute("href").replace(
            "https://etherscan.io/tx/", "")
        task_log(self.task_id, f"Tx is {tx}")
        task_log(self.task_id, "Finish deposit eth to zksync era")
        return tx
