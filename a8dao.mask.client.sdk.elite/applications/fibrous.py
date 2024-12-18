import requests

from api.local.web3.starknet import call, invoke
from tools.logger import task_log

fibrous_router_contract = (
    "0x1b23ed400b210766111ba5b1e63e33922c6ba0c45e6ad56ce112e5f4c578e62"
)


class Fibrous:
    def __init__(self, task_id: str) -> None:
        self.task_id = task_id

    def swap_by_contract(
        self,
        token_in_contract: str,
        token_out_contract: str,
        # pool_address: str,
        token_in_amount: int,
        address: str,
        private_key: str,
    ):
        task_log(
            self.task_id,
            f"swap {token_in_amount} amount of token {token_in_contract} to token {token_out_contract}",
        )
        swap_info_res = requests.get(
            "https://api.fibrous.finance/route",
            params={
                "amount": hex(token_in_amount),
                "tokenInAddress": token_in_contract.lower(),
                "tokenOutAddress": token_out_contract.lower(),
            },
        )
        assert (
            swap_info_res.status_code == 200
        ), f"get swap routes failed: {swap_info_res.reason}"
        swap_info = swap_info_res.json()
        task_log(self.task_id, f"swap info is: {swap_info}")
        assert len(swap_info["route"]) == 1, f"more than one swap route"
        swaps = swap_info["route"][0]["swaps"]
        assert all(
            [len(swap) == 1 for swap in swaps]
        ), f"failed to assert the swaps format"
        approved_amount_res = call(
            token_in_contract,
            "allowance",
            {
                "owner": int(address, 16),
                "spender": int(fibrous_router_contract, 16),
            },
        )
        assert approved_amount_res["code"] == 0, "fetch approved amount failed"
        if (
            approved_amount := approved_amount_res["data"]["remaining"]
        ) < token_in_amount:
            task_log(
                self.task_id,
                f"approved token_in amount is {approved_amount}, should approve {token_in_amount}",
            )
            approve_res = invoke(
                token_in_contract,
                "approve",
                {
                    "spender": fibrous_router_contract,
                    "amount": token_in_amount,
                },
                address,
                private_key,
            )
            assert approve_res["code"] == 0, f"approve failed: {approve_res['message']}"
            task_log(self.task_id, f"approve tx hash: {approve_res['data']}")
        else:
            task_log(
                self.task_id,
                f'approved token_in amount is {approved_amount_res["data"]}, already approved',
            )

        # token0_res = call(pool_address, "token0", {})
        # assert token0_res["code"] == 0, f'get token0 failed: {token0_res["message"]}'

        # reserve_res = call(pool_address, "get_reserves", {})
        # assert (
        #     reserve_res["code"] == 0
        # ), f'get reserves failed: {reserve_res["message"]}'

        # price = (
        #     reserve_res["data"]["reserve1"] / reserve_res["data"]["reserve0"]
        #     if token0_res["data"]["address"] == int(token_in_address, 16)
        #     else reserve_res["data"]["reserve0"] / reserve_res["data"]["reserve1"]
        # )

        swap_res = invoke(
            fibrous_router_contract,
            "swap",
            {
                "swaps": [
                    # {
                    #     "token_in": int(token_in_address, 16),
                    #     "token_out": int(token_out_address, 16),
                    #     # default rate is 0.01
                    #     "rate": int("0xf4240", 16),
                    #     "protocol": 2,
                    #     "pool_address": int(pool_address, 16),
                    # }
                    {
                        "token_in": swap[0]["fromTokenAddress"],
                        "token_out": swap[0]["toTokenAddress"],
                        # default rate is 0.01
                        "rate": int("0xf4240", 16),
                        "protocol": swap[0]["protocol"],
                        "pool_address": swap[0]["poolAddress"],
                    }
                    for swap in swaps
                ],
                "params": {
                    "token_in": token_in_contract,
                    "token_out": token_out_contract,
                    "amount": token_in_amount,
                    "min_received": int(int(swap_info["outputAmount"]) * 0.99),
                    "destination": address,
                },
            },
            address,
            private_key,
        )
        assert swap_res["code"] == 0, f"swap failed: {swap_res['message']}"
        task_log(self.task_id, f'swap succeeded: {swap_res["data"]}')
