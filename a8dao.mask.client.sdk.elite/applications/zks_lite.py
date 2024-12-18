from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.remote.webelement import WebElement
from extensions.metamask import MetaMask
from fingerprint.browser import Browser

from tools.logger import task_log


class ZksLite:
    def __init__(self, task_id: str, browser: Browser, metamask: MetaMask) -> None:
        self.task_id = task_id
        self.browser = browser
        self.metamask = metamask

    def home(self):
        task_log(self.task_id, "go to https://lite.zksync.io")
        self.browser.get("https://lite.zksync.io/account")
        pass

    def connect_metamask(self):
        while True:
            try:
                self.browser.get("https://lite.zksync.io/account")
                self.browser.wait(5, 10)
                shadow_root: WebElement = self.browser.driver.execute_script(
                    'return document.querySelector("onboard-v2").shadowRoot'
                )
                self.browser.wait(3, 5)
                wallet_elements = shadow_root.find_elements(
                    By.CSS_SELECTOR, ".wallet-button-container")
                self.browser.wait(3, 5)
                metamask_wallet: WebElement = [
                    w for w in wallet_elements if w.text == "MetaMask"][0]
                self.browser.click(metamask_wallet)
                if self.browser.wait_tabs(2, 10):
                    self.metamask.confirm()
                    self.browser.wait(3, 5)
                    self.browser.switch_to(0)
                    title_elements = self.browser.find_elements_and_wait(
                        ".header")
                    if len(title_elements) > 0 and "Wrong network" in title_elements[0].text:
                        self.browser.wait_tabs(2)
                        self.browser.wait(3, 5)
                        self.metamask.add_and_switch_network()
                        self.browser.wait(3, 5)
                        self.browser.switch_to(0)
                    break
            except:
                task_log(self.task_id, "Connect to metamask error, try again")

        pass

    def transfer(self, to_address: str, amount: float | None = None) -> dict:
        task_log(self.task_id, "transfer on zksync lite")
        self.browser.get("https://lite.zksync.io/transaction/transfer")
        self.browser.wait(3, 5)
        while True:
            activation_div_element = self.browser.find_element_and_wait(
                "div[data-cy=account_activation_modal]>.modal-overlay"
            )
            if not activation_div_element.is_displayed():
                break
            activation_button_element = self.browser.find_element_and_wait(
                "button[data-cy=account_activation_sign_button]")
            self.browser.click(activation_button_element)
            self.browser.wait_tabs(2)
            self.metamask.confirm()
            self.browser.wait(3, 5)

        address_block_input_element = self.browser.find_element_and_wait(
            "input[data-cy=address_block_wallet_address_input]")
        self.browser.send_keys(address_block_input_element, to_address)
        self.browser.wait(1, 2)
        if amount is None:
            amount_max_button_element = self.browser.find_element_and_wait(
                "div[data-cy=amount_block_token_max_amount]")
            self.browser.click(amount_max_button_element)
        else:
            amount_button_element = self.browser.find_element_and_wait(
                "input[data-cy=amount_block_token_input]"
            )
            self.browser.send_keys(amount_button_element, str(amount))
        commit_transaction_button = self.browser.find_element_and_wait(
            "button[data-cy=commit_transaction_button]")

        if "Authorize to Send on zkSync" in commit_transaction_button.text:
            self.browser.click(commit_transaction_button)
            self.browser.wait_tabs(2)
            self.metamask.confirm()
        commit_button_element = self.browser.find_element_and_wait(
            "button[data-cy=commit_transaction_button]")
        self.browser.click(commit_button_element)
        title_segments = ["Transfer warning", "Fee changed"]
        while True:
            if not self.browser.wait_tabs(2, 15):
                display_modal_element = self.browser.find_element_and_wait(
                    "div.modal-overlay[style=''] .modal.-md.-light")
                title = display_modal_element.find_element(
                    By.CSS_SELECTOR, ".header").text.strip()
                if title in title_segments:
                    button = display_modal_element.find_element(
                        By.CSS_SELECTOR, ".button")
                    self.browser.click(button)
                else:
                    print(title)
            else:
                break
        self.browser.wait(1, 3)
        self.metamask.confirm()
        self.browser.wait(3, 5)

        if not self.browser.wait_url("https://lite.zksync.io/transaction/transfer/", True, 180):
            raise Exception("Transfer failed")
        self.browser.wait(5, 10)
        button_ok_element = self.browser.find_element_and_wait(
            "button[data-cy='success_block_ok_button']")

        transfered_amount_elements = self.browser.find_elements_and_wait(
            ".infoBlockItem._margin-top-1 .amount")

        transfered_amount = float(
            transfered_amount_elements[0].text.split(" ")[1].strip())
        fee = float(transfered_amount_elements[1].text.split(" ")[1].strip())
        response = {
            "amount": transfered_amount,
            "fee": fee
        }
        self.browser.click(button_ok_element)
        return response

    def has_connected(self):
        self.browser.get("https://lite.zksync.io/account")
        self.browser.wait(3, 5)
        total_elements = self.browser.find_elements_and_wait(".total")
        return len(total_elements) > 0

    def get_balance(self):
        WebDriverWait(self.browser.driver, 30).until(
            lambda d: float(d.find_element(
                By.CLASS_NAME, "total").text.split(" ")[-1])
            is not None
        )
        return float(self.browser.find_element_and_wait(".total").text.split(" ")[-1])
