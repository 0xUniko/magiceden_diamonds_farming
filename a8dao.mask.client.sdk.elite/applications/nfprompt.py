from selenium.webdriver.common.by import By

from extensions.metamask import MetaMask
from fingerprint.browser import Browser
from model import ChainId
from tools.logger import task_log


class Nfprompt:
    def __init__(self, task_id: str, browser: Browser, metamask: MetaMask) -> None:
        self.task_id = task_id
        self.browser = browser
        self.metamask = metamask

    def login(self):
        self.metamask.switch_to_network(ChainId.OPBNB)
        try:
            self.browser.initialized_get("https://nfprompt.io/")
        except Exception as e:
            print(e)
        get_start = self.browser.find_element_and_wait(
            ".main-btn.text-sm.px-4.py-2.h-auto.cursor-pointer"
        )
        self.browser.click(get_start)
        connet_wallet = self.browser.find_element_and_wait(".login-item")
        self.browser.click(connet_wallet)
        metamask_btn = self.browser.find_elements_with_shadow_root(
            [
                "w3m-modal",
                "w3m-modal-router",
                "w3m-connect-wallet-view",
                "w3m-desktop-wallet-selection",
            ],
            '[name="MetaMask"]',
        )[0]
        self.browser.click(metamask_btn)
        self.metamask.connect()
        self.metamask.sign()
