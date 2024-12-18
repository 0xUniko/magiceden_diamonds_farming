import time

from selenium.webdriver.support.wait import WebDriverWait

from extensions.metamask import MetaMask
from fingerprint.browser import Browser


class ZKS_Network:
    def __init__(self, browser: Browser, metamask: MetaMask) -> None:
        self.browser = browser
        self.metamask = metamask
        pass

    def home(self):
        self.browser.initialized_get("https://zks.network/")
        time.sleep(1)
        if len(self.browser.find_elements(".termsConditionsWrapper")) > 0:
            for checkbox in self.browser.find_elements("input[type=checkbox]"):
                checkbox.click()
            self.browser.find_element(".MuiButton-text").click()

    def connect_wallet(self, password: str):
        self.browser.find_element_and_wait(".btn-primary.btn").click()
        self.browser.find_element_and_wait(
            "button[data-testid=rk-wallet-option-metaMask]"
        ).click()
        self.metamask.connect(password)
        self.browser.switch_to(0)
        pass

    def search_name(self, name: str):
        self.browser.find_element_and_wait(".value-input").send_keys(name)
        self.browser.find_element_and_wait(".btn-search").click()

    def registry(self):
        assert (
            self.browser.find_element_and_wait(".availability").text == "Available"
        ), "the domain name is not available"
        self.browser.clean_tabs()

        self.browser.find_element_and_wait(".btn-search").click()
        time.sleep(1)
        self.browser.find_element_and_wait(".btn-primary").click()
        self.browser.find_element_and_wait(".btn-primary.step-2").click()
        WebDriverWait(self.browser.driver, 10).until(
            lambda d: len(d.window_handles) == 2
        )
        self.browser.switch_to(-1)
        self.metamask.confirm()
