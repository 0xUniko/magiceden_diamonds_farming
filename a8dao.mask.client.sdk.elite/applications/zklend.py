from enum import Enum
from typing import Literal

from api.local.web3.starknet import CallRequest, invoke, multicall
from config import config
from extensions.argentx import ArgentX
from fingerprint.browser import Browser
from tools.logger import task_log
from tools.web3_tools import starknet_approve_tool

zklend_contract = "0x04c0a5193d58f74fbace4b74dcf65481e734ed1714121bdc571da345540efa05"
zklend_zeth_contract = (
    "0x01b5bd713e72fdc5d63ffd83762f81297f6175a5e0a4771cdadbc1dd5fe72cb1"
)
eth_contract = config["contract"]["starknet"]["eth"]
usdc_contract = config["contract"]["starknet"]["usdc"]


# you should add other tokens by yourself
class Token(Enum):
    eth = eth_contract
    usdc = usdc_contract


class ZkLend:
    def __init__(
        self,
        task_id: str,
        browser: Browser | None = None,
        argentx: ArgentX | None = None,
    ) -> None:
        self.task_id = task_id
        self.browser = browser
        self.argentx = argentx
        pass

    def home(self):
        task_log(self.task_id, "Visit zklend markets page")
        assert self.browser is not None, "browser instance is required"
        assert self.argentx is not None, "argentx instance is required"
        self.browser.initialized_get("https://app.zklend.com/markets")
        try:
            btns = self.browser.find_elements_and_wait("button")
            if len(accept_btn := [b for b in btns if b.text == "ACCEPT"]) > 0:
                accept_btn[0].click()
        except:
            pass

    def connect_wallet(self):
        task_log(self.task_id, "Start connect wallet")
        assert self.browser is not None, "browser instance is required"
        assert self.argentx is not None, "argentx instance is required"
        btns = self.browser.find_elements_and_wait("button")
        if len(connect_btn := [b for b in btns if b.text == "CONNECT"]) > 0:
            self.browser.click(connect_btn[0])
            wallet_btns = self.browser.find_elements_and_wait(
                "button.w-full.py-2.px-4.mb-4.rounded-xs.inline-flex.items-center.justify-start.border-neutral-200.border.button-text2.text-neutral-00"
            )
            self.browser.click(wallet_btns[0])
            self.argentx.confirm()
        pass

    def supply_eth(self, amount: float, collateral=True):
        task_log(self.task_id, f"supply {amount} eth")
        assert self.browser is not None, "browser instance is required"
        assert self.argentx is not None, "argentx instance is required"
        btns = self.browser.find_elements_and_wait("button")
        supply_btns = [b for b in btns if b.text == "SUPPLY"]
        task_log(self.task_id, "click supply eth")
        self.browser.click(supply_btns[0])
        if collateral:
            collateral_btn = self.browser.find_element_and_wait(
                ".flex.center.ml-1.z-10"
            )
            self.browser.click(collateral_btn)
        self.browser.find_element_and_wait(
            'input[placeholder="Enter amount"]'
        ).send_keys(amount)
        enable_and_supply_btn = self.browser.find_element_and_wait(
            "button.w-full.h-full.l2C"
        )
        self.browser.click(enable_and_supply_btn)
        self.argentx.confirm()

    def deposit_onchain(
        self, token: Token, amount: int, address: str, private_key: str
    ):
        task_log(self.task_id, f"deposit {amount} {token.value} onchain")
        calls: list[CallRequest] = []
        approve_call = starknet_approve_tool(
            self.task_id, token.value, zklend_contract, address, amount
        )
        if approve_call is not None:
            calls.append(approve_call)
        calls.append(
            {
                "contract_address": zklend_contract,
                "function_name": "deposit",
                "function_args": {"token": token.value, "amount": amount},
            }
        )
        res = multicall(address, private_key, calls)
        assert res["code"] == 0, f'deposit failed: {res["message"]}'
        task_log(self.task_id, f"deposit successfully")

    def withdraw_onchain(
        self,
        token: Token,
        address: str,
        private_key: str,
        amount: int | Literal["all"] = "all",
    ):
        task_log(self.task_id, f"withdraw {amount} {token.value} onchain")
        if amount == "all":
            res = invoke(
                zklend_contract,
                "withdraw_all",
                {"token": token.value},
                address,
                private_key,
            )
        else:
            res = invoke(
                zklend_contract,
                "withdraw",
                {"token": token.value, "amount": amount},
                address,
                private_key,
            )
        assert res["code"] == 0, f'withdraw failed: {res["message"]}'
        task_log(self.task_id, "withdraw successfully")
