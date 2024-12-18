from enum import Enum

import requests
from selenium.webdriver.support import expected_conditions as EC

from api.local.web3.starknet import CallRequest, get_token_balance, multicall
from config import config
from extensions.argentx import ArgentX
from fingerprint.browser import Browser
from model import wallet_data
from tools.logger import task_log
from tools.web3_tools import TxRecorder, starknet_approve_tool

myswap_contract = "0x010884171baf1914edc28d7afb619b40a4051cfae78a094a55d230f19e944a28"
eth_contract = config["contract"]["starknet"]["eth"]
usdc_contract = config["contract"]["starknet"]["usdc"]


class Token(Enum):
    eth = "ETH"
    dai = "DAI"
    usdc = "USDC"
    wbtc = "WBTC"
    usdt = "USDT"
    wstETH = "wstETH"
    lords = "LORDS"


class MySwap:
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

    def home_and_connect_wallet(self):
        task_log(self.task_id, "Visit myswap swap page")
        assert self.browser is not None, "browser instance is required"
        assert self.argentx is not None, "argentx instance is required"
        self.browser.initialized_get("https://www.myswap.xyz/#/swap")
        try:
            connect_wallet_header = self.browser.find_element_and_wait(
                "header>h1", timeout=5
            )
            task_log(self.task_id, "connect to argentx")
            assert connect_wallet_header.text == "Connect a wallet"
            argentx_btn = self.browser.find_element_and_wait(
                "ul.flex.flex-col.gap-3>li"
            )
            self.browser.click(argentx_btn)
            self.argentx.confirm()
        except:
            task_log(self.task_id, "wallet already connected")
            pass
        try:
            i_understand_btn = self.browser.find_element_and_wait(
                "#breaking-changes-dialog-content+div"
            )
            task_log(self.task_id, "close mainnet disclaimer")
            self.browser.click(i_understand_btn)
        except:
            pass
        try:
            close_braavos = self.browser.find_element_and_wait(
                "svg.cursor-pointer.absolute.text-white"
            )
            task_log(self.task_id, "close braavos ad")
            self.browser.click(close_braavos)
        except:
            pass

    def swap_eth_to_token(self, amount: float, token: Token, wallet: wallet_data):
        task_log(self.task_id, f"swap eth to {token.value}")
        assert self.browser is not None, "browser instance is required"
        assert self.argentx is not None, "argentx instance is required"
        select_token_btn = self.browser.find_element_and_wait(
            "span.select-none.flex.w-full.justify-center.items-center.text-md"
        )
        self.browser.click(select_token_btn)
        self.browser.wait(1, 1.5)
        token_list = self.browser.find_elements_and_wait(
            "div.flex.flex-col.text-4>span.font-bold"
        )
        token_ul = [t for t in token_list if t.text == token.value][0]
        self.browser.click(token_ul)
        eth_input = self.browser.find_element_and_wait(
            "input.bg-transparent.text-right.text-white.outline-none.w-full"
        )
        self.browser.send_keys(eth_input, amount)
        swap_btn = self.browser.find_element_and_until(
            "div.mt-4.cursor-pointer.rounded-lg.flex.p-2.items-center.justify-center.text-white",
            EC.element_to_be_clickable,
        )
        assert swap_btn is not None
        self.browser.wait(5, 8)
        self.browser.click(swap_btn)
        for _ in range(60):
            self.browser.wait(1, 3)
            if len(self.browser.driver.window_handles) == 1:
                self.browser.click(swap_btn)
            else:
                break
        else:
            raise Exception("cannot click the swap button")
        with TxRecorder(self.task_id, wallet):
            self.argentx.confirm()

    def add_liquidity(self, wallet: wallet_data, token1: Token, token2: Token):
        """
        default amount is the max amount of token2, if you want to custom the amount pls modify the code by yourself
        """
        task_log(self.task_id, f"add liquidity {token1.value}-{token2.value}")
        assert self.browser is not None, "browser instance is required"
        assert self.argentx is not None, "argentx instance is required"
        self.browser.initialized_get("https://www.myswap.xyz/#/swap?isPools=true")
        assert (
            self.browser.find_element_and_wait(
                "div.relative.flex.justify-between.items-center>span"
            ).text
            == "Add Liquidity"
        ), "this page is not the expected page"

        select_token1_btn = self.browser.find_element_and_wait(
            "div.w-full.relative.cursor-pointer"
        )
        self.browser.click(select_token1_btn)
        token_list = self.browser.find_elements_and_wait(
            "div.flex.flex-col.text-4>span.font-bold"
        )
        token1_ul = [t for t in token_list if t.text == token1.value][0]
        self.browser.click(token1_ul)

        select_token2_btn = self.browser.find_element_and_wait(
            "span.select-none.flex.w-full.justify-center.items-center.text-md.py-1.px-2.rounded-full"
        )
        self.browser.click(select_token2_btn)
        token_list = self.browser.find_elements_and_wait(
            "div.flex.flex-col.text-4>span.font-bold"
        )
        token2_ul = [t for t in token_list if t.text == token2.value][0]
        self.browser.click(token2_ul)

        token2_max = self.browser.find_elements_and_wait(
            "button.MuiButtonBase-root.MuiButton-root.MuiButton-text.MuiButton-textPrimary.MuiButton-sizeSmall.MuiButton-textSizeSmall"
        )[1]
        self.browser.click(token2_max)

        self.browser.wait(5, 8)
        add_liquidity_btn = self.browser.find_element_and_wait(
            "div.cursor-pointer.rounded-lg.flex.p-2.items-center.justify-center.text-white"
        )
        self.browser.click(add_liquidity_btn)
        for _ in range(60):
            self.browser.wait(1, 3)
            if len(self.browser.driver.window_handles) == 1:
                self.browser.click(add_liquidity_btn)
            else:
                break
        else:
            raise Exception("cannot click the add liquidity button")
        with TxRecorder(self.task_id, wallet):
            self.argentx.confirm()
        pass

    def swap(
        self,
        token_in: Token,
        token_out: Token,
        token_in_amount: int,
        address: str,
        private_key: str,
    ):
        assert (token_in == Token.eth and token_out == Token.usdc) or (
            token_in == Token.usdc and token_out == Token.eth
        ), "pool_id is not recorded in this script yet"
        if token_in == Token.eth:
            token_in_contract = eth_contract
            token_out_contract = usdc_contract
            token_in_name = "ethereum"
            token_out_name = "usd-coin"
        else:
            token_in_contract = usdc_contract
            token_out_contract = eth_contract
            token_in_name = "usd-coin"
            token_out_name = "ethereum"
        pool_id = 1
        task_log(
            self.task_id,
            f"swap {token_in_contract} to {token_out_contract}, pool_id is {pool_id}",
        )

        token_in_balance_res = get_token_balance(address, token_in_contract)
        assert (
            token_in_balance_res["code"] == 0
        ), f'get token_in balance failed: {token_in_balance_res["message"]}'
        token_out_balance_res = get_token_balance(address, token_out_contract)
        assert (
            token_out_balance_res["code"] == 0
        ), f'get token_out balance failed: {token_out_balance_res["message"]}'
        price_res = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?vs_currencies=usd&ids=ethereum,dai,usd-coin,tether,wrapped-steth,bitcoin,lords"
        )
        assert price_res.status_code == 200, f"get price failed: {price_res.reason}"
        amount_to_min = int(
            token_in_amount
            / 10 ** token_in_balance_res["data"]["decimals"]
            * price_res.json()[token_in_name]["usd"]
            / price_res.json()[token_out_name]["usd"]
            * 10 ** token_out_balance_res["data"]["decimals"]
            * 0.99  # slippage is 0.01
        )
        task_log(self.task_id, f"amount_to_min: {amount_to_min}")

        calls: list[CallRequest] = []

        approve_call = starknet_approve_tool(
            self.task_id, token_in_contract, myswap_contract, address, token_in_amount
        )
        if approve_call is not None:
            calls.append(approve_call)

        calls.append(
            {
                "contract_address": myswap_contract,
                "function_name": "swap",
                "function_args": {
                    "pool_id": pool_id,
                    "token_from_addr": token_in_contract,
                    "amount_from": token_in_amount,
                    "amount_to_min": amount_to_min,
                },
            }
        )
        res = multicall(address, private_key, calls)
        assert res["code"] == 0, f'swap failed: {res["message"]}'
        task_log(self.task_id, "swap successfully")
