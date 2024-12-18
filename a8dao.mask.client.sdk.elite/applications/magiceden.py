import json
import os
import time
from datetime import datetime

from api.local.web3.solana import get_balance, get_spl_balance
from bs4 import BeautifulSoup
from extensions.okx_web3 import OkxWeb3
from fingerprint.browser import Browser
from selenium.webdriver.common.by import By
from tools.logger import task_log


class MagicEden:
    def __init__(self, task_id: str, browser: Browser, okxweb3: OkxWeb3):
        self.task_id = task_id
        self.browser = browser
        self.okxweb3 = okxweb3
        self.task_log = lambda x: task_log(self.task_id, x)

    def auth(self):
        self.task_log("go to https://magiceden.io/")
        self.browser.initialized_get("https://magiceden.io/")
        time.sleep(2)
        if len(self.browser.driver.window_handles) == 1:
            wallet_connect_btn = self.browser.find_element_and_until(
                'div[data-test-id="wallet-connect-button"]', timeout=2
            )
            if wallet_connect_btn:
                self.browser.click(wallet_connect_btn)
        self.connect_wallet()
        sign_in_modal = self.browser.find_element_and_until(
            'div[data-test-id="modal-body"]', timeout=2
        )
        if sign_in_modal:
            self.task_log("sign in")
            sign_in_btn = sign_in_modal.find_element(
                By.CSS_SELECTOR,
                "button[type=button].tw-inline-flex.tw-justify-center.tw-items-center.tw-rounded.tw-transition.tw-ease-in-out.tw-bg-pink-primary",
            )
            self.browser.click(sign_in_btn)
            self.okxweb3.sign()
            time.sleep(5)
            if (
                self.browser.find_element_and_until(
                    'div[data-test-id="modal-body"]', timeout=2
                )
                is not None
            ):
                raise Exception("failed to sign in")
        else:
            self.task_log("no need to sign in")

    def buy(self, mint_address: str, name: str, owner: str):
        self.task_log(f"buy mint_address: {mint_address}, name: {name}")
        # self.browser.get(f'https://magiceden.io/item-details/{mint_address}?name=Generations-%23232164')
        self.browser.get(
            f'https://magiceden.io/item-details/{mint_address}?name={name.split(" #")[0]}-%{name.split(" #")[1]}'
        )
        royalty_items = self.browser.find_elements_and_wait(
            "div.tw-flex.tw-justify-between.tw-mt-2.tw-full"
        )
        assert len(royalty_items) == 2, "error in getting royalty"
        royalty = royalty_items[1].find_element(By.CLASS_NAME, "tw-text-white-1")
        if royalty.text != "0":
            config_btn = royalty_items[1].find_element(
                By.CSS_SELECTOR, 'div.tw-cursor-default[data-state="closed"]'
            )
            self.browser.click(config_btn)
            radios = self.browser.find_elements_and_wait('div[role="radio"]')
            self.browser.click([r for r in radios if r.is_displayed()][2])
        buy_now_btn = self.browser.find_element_and_wait(
            "button[type=button].tw-inline-flex.tw-justify-center.tw-items-center.tw-rounded.tw-text-sm.tw-transition.tw-ease-in-out.tw-bg-pink-primary.tw-w-full"
        )
        self.browser.click(buy_now_btn)
        balance = get_spl_balance(mint_address, owner)
        assert balance["code"] == 0, f"failed to get balance: {balance['message']}"
        previous_balance = balance["data"]["amount"]
        self.task_log("buying...")
        self.okxweb3.confirm()
        for _ in range(90):
            time.sleep(1)
            balance = get_spl_balance(mint_address, owner)
            assert balance["code"] == 0, f"failed to get balance: {balance['message']}"
            if balance["data"]["amount"] > previous_balance:
                self.task_log("buy successfully")
                break
        else:
            # self.task_log("failed to buy")
            raise Exception("failed to buy")
        pass

    def list(self, mint_address: str, name: str, price: float, owner: str):
        self.task_log(f"list mint_address: {mint_address}, name: {name}")
        balance = get_spl_balance(mint_address, owner)
        assert balance["code"] == 0, f"failed to get balance: {balance['message']}"
        previous_balance = balance["data"]["amount"]
        assert previous_balance > 0, "owner does not hold this nft"
        self.browser.get(
            f'https://magiceden.io/item-details/{mint_address}?name={name.split(" #")[0]}-%{name.split(" #")[1]}'
        )
        list_price_input = self.browser.find_element_and_wait("input[type=number]")
        self.browser.send_keys(list_price_input, price)
        list_now_btn = self.browser.find_element_and_wait(
            "button[type=button].tw-inline-flex.tw-justify-center.tw-items-center.tw-rounded.tw-text-sm.tw-text-white-1.tw-bg-pink-primary.flex-1-1-0"
        )
        self.browser.click(list_now_btn)
        self.task_log("listing...")
        self.okxweb3.confirm()
        for _ in range(90):
            time.sleep(1)
            balance = get_spl_balance(mint_address, owner)
            assert balance["code"] == 0, f"failed to get balance: {balance['message']}"
            if balance["data"]["amount"] < previous_balance:
                self.task_log("list successfully")
                break
        else:
            raise Exception("failed to list")
        pass

    def connect_wallet(self):
        self.task_log("connect_wallet")
        connect_wallet_btns = [
            btn
            for btn in self.browser.find_elements_and_wait(
                "button[data-test-id=wallet-connect-button]", 3
            )
            if btn.is_displayed()
        ]
        if connect_wallet_btns:
            self.browser.click(connect_wallet_btns[0])
            okx_wallet = self.browser.find_element_and_until(
                'button[data-test-id="OKX Wallet"]', 3
            )
            if okx_wallet is None:
                phantom_wallet = self.browser.find_element_and_wait(
                    'button[data-test-id="Phantom"]'
                )
                self.browser.click(phantom_wallet)
            else:
                self.browser.click(okx_wallet)
            self.okxweb3.connect()
        else:
            self.task_log("no need to connect")

    def get_reward_data(self, role_id: int, pubkey: str):
        self.browser.get("https://magiceden.io/rewards")
        sign_in_modal = self.browser.find_element_and_until(
            'div[data-test-id="modal-body"]', timeout=2
        )
        if sign_in_modal:
            self.task_log("sign in")
            sign_in_btn = sign_in_modal.find_element(
                By.CSS_SELECTOR,
                "button[type=button].tw-inline-flex.tw-justify-center.tw-items-center.tw-rounded.tw-transition.tw-ease-in-out.tw-bg-pink-primary",
            )
            self.browser.click(sign_in_btn)
            self.okxweb3.sign()
            time.sleep(5)
            if (
                self.browser.find_element_and_until(
                    'div[data-test-id="modal-body"]', timeout=2
                )
                is not None
            ):
                raise Exception("failed to sign in")
        balance_res = get_balance(pubkey)
        assert (
            balance_res["code"] == 0
        ), f'failed to get balance: {balance_res["message"]}'
        soup = BeautifulSoup(self.browser.driver.page_source)
        res = soup.find("span", string="Loyalty")
        assert res is not None
        assert res.parent is not None
        loyalty = (
            repr(res.parent.contents[-1])
            .replace(r"\n", "")
            .replace(" ", "")
            .replace("'", "")
        )

        res = soup.find("span", string="Diamonds Bonus")
        assert res is not None
        assert res.parent is not None
        diamonds_bonus = (
            repr(res.parent.contents[-1])
            .replace(r"\n", "")
            .replace(" ", "")
            .replace("'", "")
        )

        res = soup.find("span", string="Last 7 Days")
        assert res is not None
        assert res.parent is not None
        last_7_days = (
            repr(res.parent.contents[-1])
            .replace(r"\n", "")
            .replace(" ", "")
            .replace("'", "")
        )

        res = soup.find(href="/rewards", class_="tw-mr-1")
        assert res is not None
        total_diamonds = res.find("small").string  # type: ignore

        if os.path.exists("reward_data.json"):
            with open("reward_data.json", "r") as f:
                reward_data = json.load(f)
        else:
            reward_data = []
        new_reward_data = {
            "time": str(datetime.now()),
            "role_id": role_id,
            "pubkey": pubkey,
            "sol_balance": balance_res["data"] / 10e8,
            "loyalty": loyalty,
            "diamonds_bonus": diamonds_bonus,
            "last_7_days": last_7_days,
            "total_diamonds": total_diamonds,
        }
        self.task_log(f"new_reward_data: {new_reward_data}")
        reward_data.append(new_reward_data)
        with open("reward_data.json", "w") as f:
            json.dump(reward_data, f)
