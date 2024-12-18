import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from extensions.metamask import MetaMask
from fingerprint.browser import Browser
from tools.logger import task_log


class Izumi:
    def __init__(self, task_id: str, browser: Browser, metamask: MetaMask) -> None:
        self.task_id = task_id
        self.browser = browser
        self.metamask = metamask
        pass

    def swap_page(self, password: str):
        self.browser.get("https://www.google.com")
        self.metamask.unlock(password)
        task_log(self.task_id, "got to https://izumi.finance/trade/swap")
        self.browser.initialized_get("https://izumi.finance/trade/swap")
        self.metamask.connect()

    def swap_eth_to_usdc(self, usdc: int):
        task_log(self.task_id, "swap eth to usdc")
        self.browser.find_elements_and_wait("input.chakra-input.f1dlhus7.css-kvjvgw")[
            1
        ].send_keys(usdc)
        time.sleep(1)
        self.browser.find_element_and_wait(
            "button.f1rrgmdj.css-lsctov").click()
        WebDriverWait(self.browser.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.f1rrgmdj.css-lsctov"))
        ).click()
        self.metamask.confirm()

    def swap_usdc_to_eth(self, usdc: int | None = None):
        task_log(self.task_id, "swap usdc to eth")
        self.browser.initialized_get("https://izumi.finance/trade/swap")
        WebDriverWait(self.browser.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".css-1an41go"))
        ).click()
        if usdc is None:
            self.browser.find_element_and_wait(".f1nhfu51.css-1hkjvi2").click()
        else:
            self.browser.find_element_and_wait(
                "input.chakra-input.f1dlhus7.css-kvjvgw"
            ).send_keys(usdc)
            time.sleep(1)
            self.browser.find_element_and_wait(
                "button.f1rrgmdj.css-lsctov").click()
        confirm_btns = self.browser.driver.find_elements(
            By.CSS_SELECTOR, "button.f1rrgmdj.css-lsctov"
        )
        if confirm_btns[1].get_attribute("hidden") is None:
            confirm_btns[1].click()
            self.metamask.confirm()
            time.sleep(1)
        WebDriverWait(self.browser.driver, 10).until(
            lambda d: (
                swap_btn := d.find_elements(
                    By.CSS_SELECTOR, "button.f1rrgmdj.css-lsctov"
                )[0]
            ).get_attribute("hidden")
            is None
            and swap_btn.get_attribute("disabled") != "true"
        )
        confirm_btns[0].click()
        self.metamask.confirm()
