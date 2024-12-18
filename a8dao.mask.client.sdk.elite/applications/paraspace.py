from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

from api.local.web3.eth import send_raw_transaction
from extensions.metamask import MetaMask
from fingerprint.browser import Browser
from model import ChainId, wallet_data
from tools.logger import task_log
from tools.web3_tools import TxRecorder

paraspace_eth_contract = {
    "eth-zks": "0x07765123EAF3cF6dd2f7b5ab717385b43B18765c",
    "eth-erc20": "0x92D6C316CdE81f6a179A60Ee4a3ea8A76D40508A",
}
paraspace_proxy_contract = {
    "eth-zks": "0x05254db23880E93f597480A29B7A75f8434D9536",
    "eth-erc20": "0x638a98BBB92a7582d07C52ff407D49664DC8b3Ee",
}

chain_name_to_paraspace_chain_name = {"eth-erc20": "mainnet", "eth-zks": "zksync"}


class Paraspace:
    def __init__(
        self,
        task_id: str,
        chain_id: ChainId,
        browser: Browser | None = None,
        metamask: MetaMask | None = None,
    ) -> None:
        self.task_id = task_id
        self.metamask = metamask
        self.chain_id = chain_id
        self.browser = browser
        self.metamask = metamask

    def home_and_connect_wallet(self):
        home = f"https://app.para.space/?chain={chain_name_to_paraspace_chain_name[self.chain_id.value]}"
        task_log(
            self.task_id,
            f"go to {home} and connect wallet",
        )
        assert self.browser is not None, "browser instance is required"
        assert self.metamask is not None, "metamask instance is required"
        self.browser.initialized_get(home)
        self.metamask.confirm()

    def deposit_eth_onchain(
        self,
        amount: float,
        address: str,
        private_key: str,
    ):
        """
        ATTENTION: this function is potentially dangerous!! you would send eth directly to the contract!!
        """
        task_log(self.task_id, "deposit_eth_onchain")
        return send_raw_transaction(
            self.chain_id,
            private_key,
            paraspace_eth_contract[self.chain_id.value],
            "depositETH(address,uint16)",
            [address, 0],
            int(amount * 10**18),
        )

    def withdraw_eth(self, wallet: wallet_data):
        task_log(self.task_id, "withdraw eth")
        assert self.browser is not None, "browser instance is required"
        assert self.metamask is not None, "metamask instance is required"
        if withdraw_btns := [
            btn
            for btn in self.browser.find_elements_and_wait("button")
            if btn.text == "Withdraw"
        ]:
            task_log(self.task_id, "withdrawing...")
            assert len(withdraw_btns) == 1, f"{len(withdraw_btns)} to withdraw"
            self.browser.click(withdraw_btns[0])
            self.browser.wait(1, 1.5)
            max_btns = [
                btn
                for btn in self.browser.find_elements_and_wait("button")
                if btn.text == "Max"
            ]
            self.browser.click(max_btns[0])
            withdraw_btns = [
                btn
                for btn in self.browser.find_elements_and_wait("button")
                if btn.text[:8] == "Withdraw" and btn.text[-3:] == "ETH"
            ]
            self.browser.click(withdraw_btns[0])
            with TxRecorder(self.task_id, wallet):
                self.metamask.confirm()
            close_btn = self.browser.find_element_and_wait(
                "button[data-testid=close-button]"
            )
            self.browser.click(close_btn)
        else:
            task_log(self.task_id, "nothing to withdraw")
        for _ in range(12):
            task_log(self.task_id, "waiting for releasing...")
            self.browser.wait(4.5, 5.5)
            claim_btns = [
                btn
                for btn in self.browser.find_elements_and_wait("button")
                if btn.text == "Claim"
            ]
            if claim_btns:
                assert len(claim_btns) == 1, f"{len(claim_btns)} to claim"
                WebDriverWait(self.browser.driver, 70).until(
                    lambda d: [
                        btn
                        for btn in d.find_elements(By.CSS_SELECTOR, "button")
                        if btn.text == "Claim"
                    ][0].is_enabled()
                )
                claim_btns = [
                    btn
                    for btn in self.browser.find_elements_and_wait("button")
                    if btn.text == "Claim"
                ]
                self.browser.click(claim_btns[0])
                self.browser.wait(1, 1.5)
                claim_btns = [
                    btn
                    for btn in self.browser.find_elements_and_wait("button")
                    if btn.text == "Claim"
                ]
                assert len(claim_btns) == 2, f"here should be 2 claim buttons"
                self.browser.click(claim_btns[1])
                task_log(self.task_id, "claiming...")
                with TxRecorder(self.task_id, wallet):
                    self.metamask.confirm()
                task_log(self.task_id, "claim successfully")
                break
        else:
            raise Exception("nothing to claim")

    # def withdraw_eth_onchain(self, address: str, private_key: str):
    #     # withdraw all
    #     if self.chain_name == ChainNameType.ETH_ZKSYNC:
    #         task_log(self.task_id, "withdraw all eth onchain")
    #         timelockQueue_res = requests.post(
    #             "https://api.para.space/graphql",
    #             json={
    #                 "operationName": "TimelockQueues",
    #                 "query": "query TimelockQueues($filter: TimelockQueueFilter) {\n  timelockQueues(filter: $filter) {\n    agreementId\n    timeAdded\n    actionType\n    assetInfo {\n      type\n      token\n      tokenIds\n      amount\n      __typename\n    }\n    transaction\n    expectedRelease\n    status\n    __typename\n  }\n}",
    #                 "variables": {"filter": {"address": address}},
    #             },
    #         )
    #         assert (
    #             timelockQueue_res.status_code == 200
    #         ), f"failed to get timelockQueue: {timelockQueue_res.reason}"
    #         unlocked_timelock_queues = [
    #             queue
    #             for queue in timelockQueue_res.json()["data"]["timelockQueues"]
    #             if queue["status"] == 0
    #         ]
    #         if unlocked_timelock_queues:
    #             task_log(
    #                 self.task_id,
    #                 f"already have unlocked timelock queue, token is {unlocked_timelock_queues[-1]['assetInfo']['token']} ATTENTION!!! you should check if this token is weth!!!",
    #             )
    #         else:
    #             task_log(self.task_id, "not withdrawn, withdrawing...")
    #             withdraw_queue_res = send_raw_transaction_with_data(
    #                 self.chain_name,
    #                 private_key,
    #                 paraspace_proxy_contract[self.chain_name.value],
    #                 0,
    #                 # this is the weth address
    #                 f"0x69328dec0000000000000000000000005bf39bde21b95d77fb18f27bbcb07f3648720a2effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff000000000000000000000000{address.lower()[2:]}",
    #             )
    #             assert (
    #                 withdraw_queue_res["code"] == 0
    #             ), f'withdraw queue failed: {withdraw_queue_res["message"]}'
    #             task_log(self.task_id, "withdraw queue succeeded")
    #             timelockQueue_res = requests.post(
    #                 "https://api.para.space/graphql",
    #                 json={
    #                     "operationName": "TimelockQueues",
    #                     "query": "query TimelockQueues($filter: TimelockQueueFilter) {\n  timelockQueues(filter: $filter) {\n    agreementId\n    timeAdded\n    actionType\n    assetInfo {\n      type\n      token\n      tokenIds\n      amount\n      __typename\n    }\n    transaction\n    expectedRelease\n    status\n    __typename\n  }\n}",
    #                     "variables": {"filter": {"address": address}},
    #                 },
    #             )
    #             assert (
    #                 timelockQueue_res.status_code == 200
    #             ), f"failed to get timelockQueue: {timelockQueue_res.reason}"
    #             unlocked_timelock_queues = [
    #                 queue
    #                 for queue in timelockQueue_res.json()["data"]["timelockQueues"]
    #                 if queue["status"] == 0
    #             ]
    #         wait_time = (
    #             datetime.fromisoformat(unlocked_timelock_queues[-1]["expectedRelease"])
    #             - datetime.now(tz=pytz.UTC)
    #         ).total_seconds()
    #         if wait_time > 0:
    #             time.sleep(5 + wait_time)
    #         withdraw_queue_res = send_raw_transaction_with_data(
    #             self.chain_name,
    #             private_key,
    #             paraspace_proxy_contract[self.chain_name.value],
    #             0,
    #             # this is the weth address
    #             f"0x69328dec0000000000000000000000005bf39bde21b95d77fb18f27bbcb07f3648720a2effffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff000000000000000000000000{address.lower()[2:]}",
    #         )
    #         assert (
    #             withdraw_queue_res["code"] == 0
    #         ), f'withdraw queue failed: {withdraw_queue_res["message"]}'

    #     else:
    #         raise Exception(
    #             "only support zksync now, pls modify the code by yourself to support other chains"
    #         )
