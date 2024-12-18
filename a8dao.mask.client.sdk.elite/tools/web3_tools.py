import time

import api.local.web3.eth as eth
import api.local.web3.starknet as starknet
from model import ChainId, wallet_data
from tools.logger import task_log


class TxRecorder:
    def __init__(self, task_id: str, wallet: wallet_data):
        self.task_id = task_id
        self.wallet = wallet
        self.address = wallet["address"]
        self.chain_id = ChainId(self.wallet["chain_id"])
        self.nonce = 0

    def get_nonce(self) -> int:
        if self.wallet["chain_id"] == ChainId.ETH_STARK_ARGENTX.value:
            res = starknet.get_nonce(self.address)
            if res["code"] == 1:
                raise Exception(f"get nonce failed: {res['message']}")
            return res["data"]
        else:
            return eth.get_nonce(self.chain_id, self.address)["data"]

    def __enter__(self):
        self.nonce = self.get_nonce()
        task_log(
            self.task_id,
            f"before transaction, get nonce of address: {self.address} is {self.nonce}. sending transaction...",
        )

    def __exit__(self, exc_type, exc_value, trace):
        for _ in range(120):
            if self.get_nonce() - self.nonce > 0:
                break
            else:
                time.sleep(1)
        else:
            raise Exception("no new transaction")

        try:
            # TODO:other chain support
            if self.wallet["chain_id"] == ChainId.ETH_STARK_ARGENTX.value:
                tx = starknet.get_latest_transaction(self.address)
                assert tx["code"] == 0 and (
                    tx["data"]["status"] == "Accepted on L2"
                    or tx["data"]["status"] == "Accepted on L1"
                ), "transaction failed"
            else:
                tx = eth.get_latest_transaction(self.chain_id, self.address)
                assert tx["code"] == 0 and (
                    # tx["data"]["status"] != "failed"
                    tx["data"]["isError"]
                    == "0"
                ), "transaction failed"
        except Exception as e:
            task_log(
                self.task_id,
                "transaction is sent but failed to fetch on block explorer or save wallet addrees chain",
            )
            raise e


def starknet_approve_tool(
    task_id: str,
    token_contract: str,
    spender_contract: str,
    owner_address: str,
    amount: int,
) -> starknet.CallRequest | None:
    approved_amount_res = starknet.call(
        token_contract,
        "allowance",
        {
            "owner": owner_address,
            "spender": spender_contract,
        },
    )
    assert approved_amount_res["code"] == 0, "fetch approved amount failed"
    if (approved_amount := approved_amount_res["data"]["remaining"]) < amount:
        task_log(
            task_id,
            f"approved token amount is {approved_amount}, should approve {amount}",
        )
        return {
            "contract_address": token_contract,
            "function_name": "approve",
            "function_args": {
                "spender": spender_contract,
                "amount": amount,
            },
        }
    else:
        task_log(
            task_id,
            f'approved token amount is {approved_amount_res["data"]}, already approved',
        )
