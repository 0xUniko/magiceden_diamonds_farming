from enum import Enum
from typing import Literal, TypedDict

import requests

from config import config
from extensions.metamask import MetaMask
from fingerprint.browser import Browser
from model import wallet_data
from tools.logger import task_log
from tools.web3_tools import TxRecorder


class Dmail:
    def __init__(self, task_id: str, browser: Browser, metamask: MetaMask) -> None:
        self.task_id = task_id
        self.browser = browser
        self.argentx = metamask

    def home_and_connect_wallet(self):
        task_log(self.task_id, "go to dmail and connect wallet")
        self.browser.initialized_get("https://mail.dmail.ai/inbox")
        log_in = self.browser.find_element_and_wait(
            "span.overflow-hidden.flex.flex-col.items-center.justify-center"
        )
