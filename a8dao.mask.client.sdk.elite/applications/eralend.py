import time
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from extensions.metamask import MetaMask
from fingerprint.browser import Browser
from tools.logger import task_log


class Eralend:
    def __init__(self, task_id: str, browser: Browser, metamask: MetaMask) -> None:
        self.task_id = task_id
        self.browser = browser
        self.metamask = metamask
        pass

    def home(self):
        task_log(self.task_id, "got to https://app.eralend.com/")
        self.browser.initialized_get("https://app.eralend.com/")
        pass

    def connect_wallet(self):
        task_log(self.task_id, "Start connect wallet")
        connect_button_element = self.browser.find_element_and_until(
            ".MuiButton-containedSizeMedium", EC.element_to_be_clickable
        )
        self.browser.click(connect_button_element)
        agree_checkbox_elements = self.browser.find_elements_with_shadow_root(
            "onboard-v2", "input[type=checkbox]"
        )
        self.browser.click(agree_checkbox_elements[-1])
        wallet_elements = self.browser.find_elements_with_shadow_root(
            "onboard-v2", ".wallet-button-container .name"
        )
        metamask_element = [w for w in wallet_elements if w.text == "MetaMask"][0]
        self.browser.click(metamask_element)
        self.browser.wait_tabs(2)
        self.metamask.connect()
        self.browser.wait(3, 5)
        task_log(self.task_id, "Finish connect wallet")
        pass

    def supply_from_syncswap_usdc_eth_lp(self):
        task_log(self.task_id, "Start supply sync usdc/eth lp")
        self.browser.find_element_and_until(
            "div[wt-id='all-markets-table'] button", EC.element_to_be_clickable
        )
        supply_name_elements = self.browser.find_elements_and_until(
            "div[wt-id='all-markets-table'] .MuiGrid-root.MuiGrid-container",
            EC.presence_of_all_elements_located,
        )
        index = 0
        for i in range(supply_name_elements):
            if supply_name_elements[i].text.strip().startswith("SYNC USDC/WETH"):
                index = i
        supply_button_elements = self.browser.find_elements_and_until(
            "div[wt-id='all-markets-table'] button", EC.presence_of_all_elements_located
        )
        syncswap_usdc_eth_lp_supply_element = supply_button_elements[index]
        self.browser.click(syncswap_usdc_eth_lp_supply_element)
        percent_elements = self.browser.find_elements_and_until(
            "#simple-tabpanel-0 form p", EC.presence_of_all_elements_located
        )

        use_as_collateral_element = self.browser.find_element_and_until(
            "input[type=checkbox]", EC.element_to_be_clickable
        )
        self.browser.click(use_as_collateral_element)
        self.browser.wait_tabs(2)
        self.metamask.confirm()
        self.browser.wait(3, 5)
        
        max_percent_element = [p for p in percent_elements if p.text == "MAX"][0]
        self.browser.click(max_percent_element)
        submit_button_element = self.browser.find_element_and_until(
            "button[type='submit']", EC.element_to_be_clickable
        )
        if submit_button_element.text.strip() == "Approve":
            self.browser.click(submit_button_element)
            self.browser.wait_tabs(2)
            self.metamask.confirm()
            submit_button_element = self.browser.find_element_and_until(
                "button[type='submit']", EC.element_to_be_clickable
            )
        self.browser.click(submit_button_element)
        self.browser.wait_tabs(2)
        self.metamask.confirm()

        pass

    def supply_eth(self, amount: float):
        task_log(self.task_id, "supply_eth")
        self.browser.get("https://app.eralend.com/")
        self.browser.find_element_and_wait(".css-qdk8f8").click()
        self.browser.find_element_and_wait("input[type=number]").send_keys(amount)
        self.browser.find_element_and_wait(
            "input.MuiSwitch-input.PrivateSwitchBase-input.css-1m9pwf3[type=checkbox]"
        ).click()
        self.metamask.confirm()
        time.sleep(3)
        self.browser.find_element_and_wait("button[type=submit]").click()
        self.metamask.confirm()

    def borrow_usdc(self, amount: int):
        task_log(self.task_id, "borrow_usdc")
        self.browser.get("https://app.eralend.com/")
        self.browser.find_elements_and_wait(".css-qdk8f8")[1].click()
        self.browser.find_elements_and_wait(
            "button.MuiButtonBase-root.MuiTab-root.MuiTab-textColorPrimary.MuiTab-fullWidth.css-1pvtu0w"
        )[2].click()
        self.browser.find_element_and_wait("input[type=number]").send_keys(amount)
        self.browser.find_element_and_wait("button[type=submit]").click()
        self.metamask.confirm()

    def repay_usdc(self, amount):
        task_log(self.task_id, "repay usdc")
        self.browser.get("https://app.eralend.com/")
        self.browser.find_elements_and_wait(".css-qdk8f8")[1].click()
        self.browser.find_elements_and_wait(
            "button.MuiButtonBase-root.MuiTab-root.MuiTab-textColorPrimary.MuiTab-fullWidth.css-1pvtu0w"
        )[3].click()
        self.browser.find_element_and_wait("input[type=number]").send_keys(amount)
        submit_btn = self.browser.find_element_and_wait("button[type=submit]")
        if submit_btn.text == "Approve":
            submit_btn.click()
            self.metamask.confirm()
        WebDriverWait(self.browser.driver, 10).until(
            lambda d: d.find_element(By.CSS_SELECTOR, "button[type=submit]").text
            == "Repay"
        )
        self.browser.find_element_and_wait("button[type=submit]").click()
        self.metamask.confirm()

    def withdraw_eth(self, amount: float | None = None):
        task_log(self.task_id, "withdraw_eth")
        self.browser.get("https://app.eralend.com/")
        self.browser.find_element_and_wait(".css-qdk8f8").click()
        self.browser.find_elements_and_wait(
            "button.MuiButtonBase-root.MuiTab-root.MuiTab-textColorPrimary.MuiTab-fullWidth.css-1pvtu0w"
        )[1].click()
        if amount is None:
            self.browser.find_element_and_wait(
                "p.MuiTypography-root.MuiTypography-body1.css-15zdict"
            ).click()
            amount_input = self.browser.find_element_and_wait("input[type=number]")
            amount = float(amount_input.get_attribute("value")[:10])
            amount_input.clear()
        self.browser.find_element_and_wait("input[type=number]").send_keys(amount)
        self.browser.find_element_and_wait("button[type=submit]").click()
        self.metamask.confirm()
