import random
import time
from uuid import uuid4

import requests
from okx import Funding
from selenium.webdriver import Chrome
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
from api.remote.resource.aigc import extract_verification_code
from fingerprint.browser import Browser
from tools.imap import Imap


class OkxAPI:

    # def __init__(self, task_id: str, browser: Browser) -> None:
    #     self.browser = browser
    #     self.task_id = task_id
    #     self.sms = SMS()

    def __init__(self, api_key: str, secret_key: str,
                 passphrase: str) -> None:
        self.api_key = api_key
        self.secret_key = secret_key
        self.passphrase = passphrase

        self.flag = "0"  # live trading: 0, demo trading: 1
        # self.task_id = task_id
        # self.sms = SMS()

    def withdrawal(self, address: str, ccy: str, chain: str, amount: str, dest: str, fee: str):
        """
        提币
        :param address:如果选择链上提币，address必须是认证过的数字货币地址。某些数字货币地址格式为地址:标签，如 ARDOR-7JF3-8F2E-QUWZ-CAN7F:123456
如果选择内部转账，address必须是接收方地址，可以是邮箱、手机或者账户名
        :param ccy: 币种，如 ETH
        :param chain:币种链信息，如ETH-Arbitrum one
        :param amount:数量
        :param dest:3：内部转账，4：链上提币
        :param fee:网络手续费≥0，提币到数字货币地址所需网络手续费可通过获取币种列表接口查询
        :return:
        """
        funding_api = Funding.FundingAPI(
            self.api_key, self.secret_key, self.passphrase, False, self.flag)
        client_id = str(uuid4()).replace("-", "1")[0:32]
        print(f"client_id:{client_id}")
        print(
            f"提币结果:{funding_api.withdrawal(ccy, amount, dest, address, fee, chain, client_id)}")
