from typing import Literal

from api.local.web3.starknet import (
    CallRequest,
    call,
    get_token_balance,
    invoke,
    multicall,
)
from config import config
from tools.logger import task_log

eth_contract = config["contract"]["starknet"]["eth"]
nostra_eth_token_contract = (
    "0x04f89253e37ca0ab7190b2e9565808f105585c9cacca6b2fa6145553fa061a41"
)


class Nostra:
    def __init__(self, task_id: str) -> None:
        self.task_id = task_id

    def deposit_eth(self, eth_amount: float, address: str, private_key: str):
        task_log(self.task_id, f"deposit {eth_amount} eth to nostra")
        amount = int(eth_amount * 10**18)
        calls: list[CallRequest] = []

        approved_amount_res = call(
            eth_contract,
            "allowance",
            {
                "owner": address,
                "spender": nostra_eth_token_contract,
            },
        )
        assert approved_amount_res["code"] == 0, "fetch approved amount failed"
        if (approved_amount := approved_amount_res["data"]["remaining"]) < amount:
            task_log(
                self.task_id,
                f"approved eth amount is {approved_amount}, should approve {amount}",
            )
            calls.append(
                {
                    "contract_address": eth_contract,
                    "function_name": "approve",
                    "function_args": {
                        "spender": nostra_eth_token_contract,
                        "amount": amount,
                    },
                }
            )
        else:
            task_log(
                self.task_id,
                f'approved eth amount is {approved_amount_res["data"]}, already approved',
            )

        calls.append(
            {
                "contract_address": nostra_eth_token_contract,
                "function_name": "mint",
                "function_args": {"to": address, "amount": amount},
            }
        )
        res = multicall(address, private_key, calls)
        assert res["code"] == 0, f'deposit failed: {res["message"]}'
        task_log(self.task_id, "deposit successfully")

    def withdraw_eth(
        self, address: str, private_key: str, eth_amount: float | Literal["all"] = "all"
    ):
        task_log(self.task_id, f"withdraw {eth_amount} eth from nostra")
        if eth_amount == "all":
            balance_res = get_token_balance(address, nostra_eth_token_contract)
            assert (
                balance_res["code"] == 0
            ), f'get nostra eth balance failed: {balance_res["message"]}'
            amount = balance_res["data"]["balance"]
        else:
            amount = eth_amount * 10**18
        task_log(self.task_id, f"withdraw amount is {amount}")

        withdraw_res = invoke(
            nostra_eth_token_contract,
            "burn",
            {"burnFrom": address, "to": address, "amount": amount},
            address,
            private_key,
        )
        assert withdraw_res["code"] == 0, f'withdraw failed: {withdraw_res["message"]}'
        task_log(self.task_id, "withdraw successfully")

    def get_nostra_eth_balance(self, address):
        task_log(self.task_id, "get nostra eth balance")
        balance_res = get_token_balance(address, nostra_eth_token_contract)
        assert balance_res["code"] == 0, f'get balance failed: {balance_res["message"]}'
        return balance_res["data"]["balance"]
