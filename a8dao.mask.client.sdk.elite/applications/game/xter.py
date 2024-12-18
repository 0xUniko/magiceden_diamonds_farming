import decimal
from extensions.metamask import MetaMask
from fingerprint.browser import Browser
from selenium.webdriver.support import expected_conditions as EC
from model import wallet_data
from api.local.web3.eth_erc20 import balance_of
from tools.logger import task_log


class Xter:
    def __init__(self, task_id: str, browser: Browser, extension: MetaMask) -> None:
        self.browser = browser
        self.task_id = task_id
        self.extension = extension
        pass

    def login(self):
        self.browser.get("https://xter.io/")
        try:
            sign_in_button_element = self.browser.find_element_and_wait(
                "#login", timeout=10)
            self.browser.click(sign_in_button_element)
            wallet_elements = self.browser.find_elements_and_wait(
                "ul .h-12.w-full")
            metamask_element = next(
                (w for w in wallet_elements if w.text == "METAMASK"), None)
            if metamask_element:
                self.browser.click(metamask_element)
                self.extension.click()
            self.browser.wait(10, 15)
        except:
            task_log(self.task_id, "Already login in")
        pass

    def launchpad(self, url: str, amount):
        self.browser.get(url)
        place_bid_element = self.browser.find_element_and_until(
            "#place_bid", EC.element_to_be_clickable)
        self.browser.click(place_bid_element)
        input_element = self.browser.find_element_and_wait(
            "input[type='text']")
        self.browser.send_keys(input_element, amount)
        confirm_button_element = self.browser.find_element_and_until(
            "button[data-type='confirm']", EC.element_to_be_clickable)
        self.browser.click(confirm_button_element)
        self.extension.click()
        task_log(self.task_id, "Bid complated")
        pass
