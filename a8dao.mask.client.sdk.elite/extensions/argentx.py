import logging

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

import api.network.wallet
import api.remote.resource.wallet
from extensions.extension import Extension
from fingerprint.browser import Browser
from model import ChainId, role_data
from tools.logger import task_log


class ArgentX(Extension):
    def __init__(
        self, browser: Browser, task_id: str, config: dict | None = None
    ) -> None:
        super().__init__(browser, task_id, config)
        self.base_url = "chrome-extension://dlcobpjiigpikoobohmabehhmhfoodbb/index.html"
        self.onboarding_url = (
            "chrome-extension://dlcobpjiigpikoobohmabehhmhfoodbb/onboarding/start"
        )
        self.lock_screen_url = (
            "chrome-extension://dlcobpjiigpikoobohmabehhmhfoodbb/lock-screen"
        )
        self.unlocked_url = (
            "chrome-extension://dlcobpjiigpikoobohmabehhmhfoodbb/account/tokens"
        )
        self.launcher_url = "https://starknet-demo-app.vercel.app"

    def enable(self):
        pass

    def load(self, role: role_data):
        self.load_extension(role, "argentx", ChainId.ETH_ETHEREUM)
        pass

    def active(self, role: role_data, mnemonics: str, password: str):
        self.launch()
        match self.browser.driver.current_url:
            case self.onboarding_url:
                self.restore_an_existing_wallet(mnemonics, password)
                # self.upload_wallet_data(
                #     role["role_label_data"]["label"],
                #     role["hd_wallet_id"],
                #     mnemonics,
                #     password,
                # )
            case self.lock_screen_url:
                self.unlock(password)
                if (
                    len(
                        [
                            w
                            for w in role["wallet_data"]
                            if w["chain_id"] == ChainId.ETH_STARK_ARGENTX.value
                        ]
                    )
                    == 0
                ):
                    self.upload_wallet_data(
                        role["role_label_data"]["label"],
                        role["hd_wallet_id"],
                        mnemonics,
                        password,
                    )
            case self.unlocked_url:
                task_log(self.task_id, "wallet already unlocked")
        pass

    def upload_wallet_data(
        self, role_label: str, hd_wallet_id: str, mnemonic: str, password: str
    ):
        address = self.get_account_address()

        task_log(self.task_id, f"address: {address}")
        private_key = self.get_private_key(password)
        print(f"private_key:{private_key}")

        wallet_response = api.network.wallet.create(
            address,
            private_key,
            mnemonic,
            password,
            ChainId.ETH_STARK_ARGENTX,
        )
        assert wallet_response["code"] == 0, Exception(wallet_response["message"])
        task_log(self.task_id, f'Wallet address id is: {wallet_response["data"]["id"]}')
        import_list = []
        import_list.append(
            api.remote.resource.wallet.WalletAddressDTO(
                id=int(wallet_response["data"]["id"]),
                wallet_api_id=str(wallet_response["data"]["id"]),
                address=address,
                private_key=private_key,
                status=1,
                chain_id=ChainId.ETH_STARK_ARGENTX,
                label=role_label,
            )
        )
        batch_import_response = api.remote.resource.wallet.batch_import(import_list)
        assert batch_import_response["code"] == 0, Exception(
            batch_import_response["message"]
        )
        wallet_append_wallet_address_response = (
            api.remote.resource.wallet.wallet_append_wallet_address(
                hd_wallet_id, wallet_response["data"]["id"]
            )
        )
        assert wallet_append_wallet_address_response["code"] == 0, Exception(
            wallet_append_wallet_address_response["message"]
        )
        task_log(self.task_id, "argentx wallet data upload success")
        pass

    def launch(self):
        self.browser.driver.switch_to.new_window()
        self.browser.get(self.base_url)
        pass

    def restore_an_existing_wallet(self, mnemonics: str, password: str):
        task_log(self.task_id, "import wallet")
        restore_an_existing_wallet_btn = self.browser.find_element_and_wait(
            "button[type=button].chakra-button+button[type=button].chakra-button"
        )
        assert (
            restore_an_existing_wallet_btn.text == "Restore an existing wallet"
        ), "failed to find Restore an existing wallet button"
        self.browser.click(restore_an_existing_wallet_btn)
        for i, word in enumerate(mnemonics.split(" ")):
            self.browser.send_keys(
                self.browser.find_element_and_wait(
                    f"input[data-testid=seed-input-{i}]"
                ),
                word,
            )
        self.browser.click(self.browser.find_element_and_wait("button[type=submit]"))
        # disclaimer_lost_of_funds_checkbox = self.browser.find_element_and_wait(
        #     "input[type=checkbox][value=lossOfFunds]+div"
        # )
        # self.browser.click(disclaimer_lost_of_funds_checkbox)
        # disclaimer_alpha_version = self.browser.find_element_and_wait(
        #     "input[type=checkbox][value=alphaVersion]+div"
        # )
        # self.browser.click(disclaimer_alpha_version)
        # continue_btn = self.browser.find_element_and_wait("span[role=link]+div>button")
        # self.browser.click(continue_btn)
        for ipt in self.browser.find_elements_and_wait("input[type=password]"):
            self.browser.send_keys(ipt, password)
        assert (
            submit_btn := self.browser.find_element_and_until(
                "button[type=submit]", EC.element_to_be_clickable
            )
        ) is not None
        self.browser.click(submit_btn)
        self.browser.wait(2, 3)
        WebDriverWait(self.browser.driver, 90).until(
            lambda d: d.find_element(By.CSS_SELECTOR, "button[type=button]").text
            == "Finish"
        )
        self.browser.click(self.browser.find_element_and_wait("button[type=button]"))
        self.browser.wait(2, 3)
        self.browser.switch_to()

    def unlock(self, password: str):
        task_log(self.task_id, "unlock argentx")
        self.launch()
        self.browser.send_keys(
            self.browser.find_element_and_wait("input[name=password]"), password
        )
        self.browser.click(self.browser.find_element_and_wait("button[type=submit]"))
        try:
            self.browser.find_element_and_wait(
                'button[aria-label="Selected network"]', timeout=5
            )
        except:
            cancel_btns = self.browser.find_elements_and_wait(
                "button[type=button].chakra-button"
            )
            if cancel_btns:
                self.browser.click(cancel_btns[0])
            if not self.browser.driver.current_url.endswith("user-review"):
                raise Exception("unlock argentx failed")
        self.browser.clean_tabs()

    def confirm(self, wait: int = 5):
        count = wait
        self.browser.driver.maximize_window()
        while count > 0:
            try:
                if len(self.browser.driver.window_handles) > 1:
                    self.browser.switch_to(-1)
                    WebDriverWait(self.browser.driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.CSS_SELECTOR, "button[type=submit]")
                        )
                    )
                    self.browser.find_element_and_wait("button[type=submit]").click()
                    self.browser.switch_to()
            except Exception as e:
                logging.warning(e)
            self.browser.wait(3, 5)
            count -= 1

    def get_account_address(self):
        task_log(self.task_id, "get account")
        self.browser.initialized_get(self.launcher_url)
        self.browser.click(self.browser.find_element_and_wait("#argentX"))
        self.browser.wait_tabs_and_switch_to(2)
        self.browser.driver.maximize_window()
        self.browser.click(
            self.browser.find_element_and_wait("button[type=submit].chakra-button")
        )
        WebDriverWait(self.browser.driver, 10).until(EC.number_of_windows_to_be(1))
        self.browser.switch_to()
        return self.browser.find_element_and_wait("#address").text

    def get_private_key(self, password: str):
        self.browser.get(self.base_url)
        show_settings = self.browser.find_element_and_wait(
            '[aria-label="Show settings"]'
        )
        self.browser.click(show_settings)
        account = self.browser.find_element_and_wait('[aria-label="Select Account 1"]')
        self.browser.click(account)
        export_private_key = self.browser.find_element_and_wait(
            "a.chakra-button+div+button[type=button].chakra-button+button[type=button].chakra-button"
        )
        self.browser.click(export_private_key)
        self.browser.find_element_and_wait('input[name="password"]').send_keys(password)
        export = self.browser.find_element_and_wait("button[type=submit]")
        self.browser.click(export)
        return self.browser.find_element_and_wait(
            'div[data-testid="privateKey"]>div'
        ).text
