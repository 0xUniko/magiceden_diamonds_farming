from selenium.webdriver.common.by import By

from extensions.metamask import MetaMask
from fingerprint.browser import Browser
from model import ChainId
from tools.logger import task_log


class Premint:
    def __init__(self, task_id: str, browser: Browser, metamask: MetaMask) -> None:
        self.task_id = task_id
        self.browser = browser
        self.metamask = metamask

    def login(self, main_page: str):
        self.browser.initialized_get(main_page)
        login_to_register = self.browser.find_element_and_wait(
            ".btn.btn-styled.btn-success.btn-shadow.btn-xl.btn-block.mt-3"
        )
        self.browser.click(login_to_register)
        metamask_btn = self.browser.find_element_and_wait(
            'button[wc-provider="metamask"]'
        )
        self.browser.click(metamask_btn)
        self.metamask.connect()
        self.browser.wait(4, 5)
        self.metamask.sign()
        self.browser.wait(5, 6)
        # self.browser.click(
        #     self.browser.find_element_and_wait(
        #         ".col-start-5.justify-self-end.self-center.flex.items-center.gap-4 > button[type=button]"
        #     )
        # )
        # self.browser.wait(1, 3)
        # if metamask := self.browser.find_elements_and_wait(
        #     "button[data-testid=rk-wallet-option-metaMask]"
        # ):
        #     self.browser.click(metamask[0])
        #     self.metamask.connect()
        # else:
        #     self.browser.click(
        #         # self.browser.find_element_and_wait("button[aria-label=Close]")
        #         self.browser.find_element_and_wait(
        #             "button.absolute.text-secondary-text.right-4.top-3.p-1.justify-self-start.duartion-100.ring-1.ring-secondary-400.transition.bg-secondary-500.rounded-full.items-center"
        #         )
        #     )
