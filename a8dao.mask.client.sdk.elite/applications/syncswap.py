import time
from enum import Enum, auto

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys
from api.remote.resource.resource import save_extend_information
from extensions.metamask import MetaMask
from fingerprint.browser import Browser
from model import ChainId, ResourceType, wallet_data
from tools.logger import task_log
from tools.web3_tools import TxRecorder


class Token(Enum):
    ETH = auto()
    USDC = auto()
    USDT = auto()
    WBTC = auto()


class Pool(Enum):
    USDC_ETH = "0x80115c708E12eDd42E504c1cD52Aea96C547c05c"
    USDT_ETH = "0xd3D91634Cf4C04aD1B76cE2c06F7385A897F54D3"
    ETH_WBTC = "0xb3479139e07568BA954C8a14D5a8B3466e35533d"


class Syncswap:
    def __init__(self, task_id: str, browser: Browser, metamask: MetaMask) -> None:
        self.task_id = task_id
        self.browser = browser
        self.metamask = metamask
        pass

    def home(self):
        task_log(self.task_id, "Visit SyncSwap home page")
        self.browser.initialized_get("https://syncswap.xyz/")
        task_log(self.task_id, "Process tour")
        start_button_elements = self.browser.find_elements_and_wait(
            ".col.align.relative div div button"
        )
        if len(start_button_elements) > 0 and start_button_elements[0].text == "Start":
            self.browser.click(start_button_elements[0])
        self.browser.wait(3, 5)
        while True:
            intro_button_elements = self.browser.find_elements_and_wait(
                ".introjs-nextbutton", 5
            )
            if len(intro_button_elements) > 0:
                self.browser.click(intro_button_elements[0], [3, 5])
            else:
                break
        pass

    def connect_wallet(self):
        task_log(self.task_id, "Start connect wallet")
        connect_wallet_button_element = self.browser.find_element_and_wait(
            "#navi-tool button.MuiButton-containedSizeMedium"
        )
        if connect_wallet_button_element.text == "Connect":
            self.browser.wait(1, 3)
            self.browser.click(connect_wallet_button_element)
            wallet_button_elements = self.browser.find_elements_and_wait(
                ".relative.flex-center.row.align.pointer"
            )
            self.browser.wait(1, 3)
            self.browser.click(wallet_button_elements[0])
            self.browser.wait_tabs(2)
            self.browser.wait(3, 5)
            self.metamask.connect()
            self.browser.wait(3, 5)
            switch_network_button_element = self.browser.find_element_and_until(
                "#swap-box .col.gap-10 + button", EC.element_to_be_clickable
            )
            if switch_network_button_element.text == "Switch to zkSync Era":
                task_log(self.task_id, "Switch network to era")
                self.browser.click(switch_network_button_element)
                while True:
                    try:
                        sub_switch_network_button_element = self.browser.find_element_and_until(
                            "button[aria-label='Click to switch the network with your wallet.']",
                            EC.element_to_be_clickable,
                        )
                        self.browser.click(sub_switch_network_button_element)
                        break
                    except:
                        task_log(self.task_id,
                                 "Wait switch network button appear")
                        self.browser.wait(3, 5)
                self.browser.wait_tabs(2)
                self.metamask.add_and_switch_network()
                self.browser.wait(3, 5)
                enter_an_amount_button_element = self.browser.find_element_and_until(
                    ".swap-confirm", EC.presence_of_element_located
                )
                assert enter_an_amount_button_element.text == "Enter an amount"
            task_log(self.task_id, "Finish connect wallet")

    def swap_eth_to_token(self, token: Token, amount: float):
        task_log(self.task_id, f"Start swap eth to {token.name}")
        self.browser.initialized_get("https://syncswap.xyz/swap")
        if token != Token.USDC:
            token_button_elements = self.browser.find_elements_and_until(
                ".swap-input + button", EC.presence_of_all_elements_located
            )
            self.browser.click(token_button_elements[1])
            token_input_element = self.browser.find_element_and_until(
                ".w100.input", EC.presence_of_element_located
            )
            self.browser.send_keys(token_input_element, token.name)

            token_list_item_elements = self.browser.find_elements_and_wait(
                ".w100.row2.align", EC.presence_of_all_elements_located
            )
            assert len(
                token_list_item_elements) > 0, f"No token name {token.name}"
            self.browser.click(token_list_item_elements[0])
            enter_an_amount_button_element = self.browser.find_element_and_until(
                ".swap-confirm", EC.presence_of_element_located
            )
            assert (
                enter_an_amount_button_element.text == "Enter an amount"
            ), "Can not find Enter an amount button"

        swap_input_elements = self.browser.find_elements_and_until(
            "input[class=swap-input]", EC.presence_of_all_elements_located
        )
        assert len(swap_input_elements) == 2, "Can not find enough swap inputs"
        self.browser.send_keys(swap_input_elements[0], str(amount))
        self.browser.wait(3, 5)
        swap_button_element = self.browser.find_element_and_until(
            ".swap-confirm", EC.element_to_be_clickable, 180
        )
        self.browser.click(swap_button_element)
        self.browser.wait_tabs(2)
        self.metamask.confirm()
        self.browser.wait(3, 5)
        task_log(self.task_id, f"Finish swap eth to {token.name}")
        pass

    def swap_token_to_eth(self, token: Token, amount: float | None = None):
        task_log(self.task_id, f"Start swap {token.name} to eth")
        self.browser.get("https://syncswap.xyz/")
        exchange_button_element = self.browser.find_element_and_until(
            ".swap-exchange-icon", EC.element_to_be_clickable
        )
        self.browser.click(exchange_button_element)
        if token != Token.USDC:
            token_button_elements = self.browser.find_elements_and_until(
                ".swap-input + button", EC.presence_of_all_elements_located
            )
            self.browser.click(token_button_elements[0])
            token_input_element = self.browser.find_element_and_until(
                ".w100.input", EC.presence_of_element_located
            )
            self.browser.send_keys(token_input_element, token.name)
            token_list_item_elements = self.browser.find_elements_and_until(
                ".w100.row2.align", EC.presence_of_all_elements_located
            )
            assert len(
                token_list_item_elements) > 0, f"No token name {token.name}"
            self.browser.click(token_list_item_elements[0])
            enter_an_amount_button_element = self.browser.find_element_and_until(
                ".swap-confirm", EC.presence_of_element_located
            )
            assert (
                enter_an_amount_button_element.text == "Enter an amount"
            ), "Can not find Enter an amount button"

        if amount is None:
            swap_percent_button_elements = self.browser.find_element_and_until(
                "#swap-input button", EC.presence_of_all_elements_located
            )
            self.browser.wait(1, 3)
            self.browser.click(swap_percent_button_elements[-1])
        else:
            swap_input_element = self.browser.find_element_and_until(
                "input[class=swap-input]", EC.presence_of_element_located
            )
            self.browser.send_keys(swap_input_element, str(amount))

        unlock_token_button_element = self.browser.find_element_and_until(
            ".col.gap-12 .arrow.row.gap-8 + button", EC.element_to_be_clickable, 60
        )
        if (
            unlock_token_button_element is not None
            and unlock_token_button_element.text == f"Unlock {token.name}"
        ):
            task_log(self.task_id, f"Unlock {token.name}")
            self.browser.click(unlock_token_button_element)
            self.browser.wait_tabs(2)
            self.metamask.confirm()
            self.browser.wait(3, 5)

        swap_confirm_element = self.browser.find_element_and_until(
            ".swap-confirm", EC.element_to_be_clickable
        )
        while True:
            self.browser.click(swap_confirm_element)
            if self.browser.wait_tabs(2, 10):
                break
        self.metamask.confirm()
        self.browser.wait(3, 5)
        task_log(self.task_id, f"Finish swap {token.name} to eth")
        pass

    def add_liquidity(self, wallet: wallet_data, pool: Pool, amount: float = None):
        task_log(self.task_id, f"Start add liquidity {pool.name}")
        amount_index = pool.name.split("_").index("ETH")
        self.browser.initialized_get(f"https://syncswap.xyz/pool/{pool.value}")
        menu_item_elements = self.browser.find_elements_and_until(
            ".pointer.row.gap-8.align", EC.presence_of_all_elements_located
        )
        deposit_menu_item_element = [
            e for e in menu_item_elements if e.text.strip() == "Deposit"
        ][0]
        self.browser.click(deposit_menu_item_element)
        if amount:
            input_elements = self.browser.find_elements_and_until(
                ".add-liquidity-input", EC.presence_of_all_elements_located
            )
            self.browser.send_keys(input_elements[amount_index], str(amount))
        else:
            max_elements = self.browser.find_elements_and_until(
                ".row.gap-6.align.pointer + button", EC.presence_of_all_elements_located
            )
            self.browser.click(max_elements[amount_index])
        deposit_button_element = self.browser.find_element_and_until(
            ".col + button", EC.element_to_be_clickable
        )
        self.browser.click(deposit_button_element)
        self.browser.wait_tabs(2)
        with TxRecorder(self.task_id, wallet):
            self.metamask.confirm()
        pass

    def remove_liquidity(self, wallet: wallet_data, pool: Pool):
        task_log(self.task_id, "Start remove liquidity")
        self.browser.initialized_get(f"https://syncswap.xyz/pool/{pool.value}")
        menu_item_elements = self.browser.find_elements_and_until(
            ".pointer.row.gap-8.align", EC.presence_of_all_elements_located
        )
        withdraw_menu_item_element = [
            e for e in menu_item_elements if e.text.strip() == "Withdraw"
        ][0]
        self.browser.click(withdraw_menu_item_element)

        button_elements = self.browser.find_elements_and_until(
            ".row.gap-8 button", EC.presence_of_all_elements_located
        )
        max_button_element = button_elements[3]
        self.browser.click(max_button_element)

        single_button_element = button_elements[4]
        self.browser.click(single_button_element)
        while True:
            try:
                eth_radio_element = self.browser.find_element_and_until(
                    "input[aria-label='WETH']", EC.presence_of_element_located
                )
                self.browser.click(eth_radio_element)
                break
            except:
                task_log(self.task_id,
                         "Can not find input[aria-label='WETH'],try again")

        try:
            unlock_lp_button_element = self.browser.find_element_and_until(
                ".col.gap-6.align .w100 button", EC.element_to_be_clickable
            )
            self.browser.click(unlock_lp_button_element)
            self.browser.wait_tabs(2)
            self.metamask.sign()
            if len(self.browser.driver.window_handles) > 1:
                self.metamask.confirm()
            self.browser.wait(1, 3)
            self.browser.send_keys(
                self.browser.find_element("body"), Keys.ESCAPE, False)
        except:
            task_log(self.task_id, "Lp has been unlocked")

        withdraw_button_element = self.browser.find_element_and_until(
            ".col.gap-12 + button", EC.element_to_be_clickable
        )
        self.browser.click(withdraw_button_element)
        self.browser.wait_tabs(2)
        with TxRecorder(self.task_id, wallet):
            self.metamask.confirm()
        pass

    def add_liquidity_usdc_eth(self, wallet: wallet_data):
        task_log(self.task_id, "add liquidity usdc-eth")
        self.browser.initialized_get(
            "https://syncswap.xyz/pool/0x80115c708E12eDd42E504c1cD52Aea96C547c05c"
        )
        WebDriverWait(self.browser.driver, 10).until(
            lambda d: len(d.find_elements(
                By.CSS_SELECTOR, ".pointer.row.gap-8.align"))
            == 5
        )
        self.browser.find_elements_and_wait(
            ".pointer.row.gap-8.align")[3].click()
        time.sleep(2)
        self.browser.find_element_and_wait(
            ".MuiButtonBase-root.MuiButton-root.MuiButton-outlined.MuiButton-outlinedPrimary.MuiButton-sizeSmall.MuiButton-outlinedSizeSmall.MuiButton-root.MuiButton-outlined.MuiButton-outlinedPrimary.MuiButton-sizeSmall.MuiButton-outlinedSizeSmall.css-1j71u5l"
        ).click()
        self.browser.find_element(
            ".MuiSwitch-root.MuiSwitch-sizeMedium.css-ecvcn9"
        ).click()
        time.sleep(1)
        btns = self.browser.find_elements_and_wait(
            ".MuiButtonBase-root.MuiButton-root.MuiButton-contained.MuiButton-containedSecondary.MuiButton-sizeLarge.MuiButton-containedSizeLarge.MuiButton-fullWidth.MuiButton-root.MuiButton-contained.MuiButton-containedSecondary.MuiButton-sizeLarge.MuiButton-containedSizeLarge.MuiButton-fullWidth.css-i455tr",
            2,
        )
        if btns:
            self.browser.click(btns[0])
            task_log(self.task_id, "approve usdc")

            with TxRecorder(self.task_id, wallet):
                self.metamask.confirm()

            self.browser.initialized_get(
                "https://syncswap.xyz/pool/0x80115c708E12eDd42E504c1cD52Aea96C547c05c"
            )
            WebDriverWait(self.browser.driver, 10).until(
                lambda d: len(
                    d.find_elements(By.CSS_SELECTOR,
                                    ".pointer.row.gap-8.align")
                )
                == 5
            )
            self.browser.find_elements_and_wait(
                ".pointer.row.gap-8.align")[3].click()
            time.sleep(2)
            self.browser.find_element_and_wait(
                ".MuiButtonBase-root.MuiButton-root.MuiButton-outlined.MuiButton-outlinedPrimary.MuiButton-sizeSmall.MuiButton-outlinedSizeSmall.MuiButton-root.MuiButton-outlined.MuiButton-outlinedPrimary.MuiButton-sizeSmall.MuiButton-outlinedSizeSmall.css-1j71u5l"
            ).click()
            self.browser.find_element(
                ".MuiSwitch-root.MuiSwitch-sizeMedium.css-ecvcn9"
            ).click()
        time.sleep(1)
        self.browser.find_element(
            ".MuiButtonBase-root.MuiButton-root.MuiButton-contained.MuiButton-containedSecondary.MuiButton-sizeLarge.MuiButton-containedSizeLarge.MuiButton-root.MuiButton-contained.MuiButton-containedSecondary.MuiButton-sizeLarge.MuiButton-containedSizeLarge.swap-confirm.css-z5neor"
        ).click()
        task_log(self.task_id, "add liquidity")
        with TxRecorder(self.task_id, wallet):
            self.metamask.confirm()
