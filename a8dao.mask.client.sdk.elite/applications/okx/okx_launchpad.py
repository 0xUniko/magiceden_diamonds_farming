from applications.twitter import Twitter
from extensions.okx_web3 import OkxWeb3
from fingerprint.browser import Browser
from tools.logger import TaskLog


class OkxLaunchpad:
    def __init__(self, task_log: TaskLog, browser: Browser, okxweb3: OkxWeb3) -> None:
        self.task_log = task_log
        self.task_id = task_log.task_id
        self.okxweb3 = okxweb3
        self.browser = browser
        pass

    def home(self, event_name: str):
        self.task_log.info(f"okx launchpad load {event_name}")
        self.browser.get(
            f"https://www.okx.com/cn/web3/marketplace/launchpad/event/{event_name}")
        self.browser.get(
            f"https://www.okx.com/cn/web3/marketplace/launchpad/event/{event_name}")
        pass

    def connect(self):
        self.task_log.info("connect to wallet")
        connect_wallet_elements = self.browser.find_elements_and_wait(
            ".address-span", 15)
        if len(connect_wallet_elements) > 0:
            self.task_log.info("Already connected.")
            return
        connect_wallet_element = self.browser.find_element_and_wait(
            ".wallet-pc-connect-button.connect-wallet-button", timeout=5)
        self.browser.click(connect_wallet_element)
        connect_wallet_button_element = self.browser.find_element_and_wait(
            "#scroll-box button", timeout=5)
        self.browser.click(connect_wallet_button_element)
        self.okxweb3.connect()
        pass

    def connect_to_twitter(self, twitter: Twitter) -> bool:
        try:
            self.task_log.info("connect to twitter")
            connect_to_twitter_button_element = self.browser.find_element_and_wait(
                ".okui-popup.okui-tooltip.okui-tooltip-neutral button")
            if not connect_to_twitter_button_element.is_enabled():
                self.task_log.info("already connected to twitter")
                return True
            connect_to_twitter_button_element.click()
            self.browser.wait(1, 3)
            connect_button_element = self.browser.find_element_and_wait(
                ".okui-dialog-window.okui-dialog-window-float button.btn-fill-highlight")
            self.browser.click(connect_button_element)
            while True:
                if not self.browser.wait_tabs(2, 10):
                    self.task_log.warn("Can not authorize twitter")
                    return False
                break
            self.browser.switch_to(-1)
            twitter.authorize_app()
            if self.browser.wait_tabs(1, 30):
                self.browser.switch_to(0)
                self.browser.wait(5, 10)
                return True
            return False
        except:
            return False

    def verify(self):
        self.task_log.info("verify task")
        button_elements = self.browser.find_elements_and_wait(
            ".okui-btn.btn-md.btn-fill-highlight.index_btn__Ypg7f")
        action_button_elements = [obj for index, obj in enumerate(
            button_elements) if index % 2 == 0 and obj.is_displayed()]
        for action_button in action_button_elements:
            action_button.click()
            self.browser.wait_tabs(2, timeout=5)
            self.browser.wait(1, 3)
            self.browser.clean_tabs()
        verify_button_elements = [obj for index, obj in enumerate(
            button_elements) if index % 2 == 1 and obj.is_displayed()]
        for verify_button in verify_button_elements:
            verify_button.click()
            self.browser.wait(1, 2)
        pass

    def check_result(self) -> str:
        try:
            return self.browser.find_element_and_wait(".index_text__ggQ0M").text
        except:
            return ""

    def check_ticket(self) -> str:
        self.task_log.info("check ticket")
        try:
            ticket_elements = self.browser.find_elements_and_wait(
                ".index_number__Hm24k.font-bold", 5)
            if len(ticket_elements) > 0:
                return ticket_elements[0].text
        except:
            self.task_log.info("No ticket found.")
        try:
            join_button_element = self.browser.find_element_and_wait(
                ".btn-fill-highlight.index_button-sub__X3Dbw", timeout=5)
            self.browser.click(join_button_element)
            self.browser.wait(1, 3)
            ticket_elements = self.browser.find_elements_and_wait(
                ".index_number__Hm24k.font-bold", 5)
            if len(ticket_elements) > 0:
                ticket = ticket_elements[0].text
                self.task_log.info(f"Ticket: {ticket}")
                return ticket
            return ""
        except:
            return ""
