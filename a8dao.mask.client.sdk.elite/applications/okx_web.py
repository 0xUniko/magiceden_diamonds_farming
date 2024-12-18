import random
import time
from uuid import uuid4

import requests
from selenium.webdriver import Chrome, ActionChains
from selenium.webdriver.common.by import By
# from selenium.webdriver.support.ui import WebDriverWait
from api.remote.resource.aigc import extract_verification_code
from fingerprint.browser import Browser
from tools.imap import Imap
from selenium.webdriver.common.keys import Keys

class OkxWeb:

    # def __init__(self, task_id: str, browser: Browser) -> None:
    #     self.browser = browser
    #     self.task_id = task_id
    #     self.sms = SMS()

    def __init__(self, browser: Browser, email: str, email_password: str) -> None:
        self.browser = browser
        self.headers = {
            "Content-Type": "application/json",
            "user_flow_token": "user_flow_token",
        }
        self.imap = Imap()
        if not self.imap.login(email, email_password):
            raise Exception("imap login failed")
        # self.task_id = task_id
        # self.sms = SMS()

    def set_withdrawal_whitelist(self, set_withdrawal_address_url: str, network_index: int, address_list: list) -> bool:
        """
        设置okx提现白名单
        :param set_withdrawal_address_url: 白名单url
        :param network_index: 网络索引
        :param address_list: 白名单地址列表
        :return:
        """
        self.browser.get(set_withdrawal_address_url)

        time.sleep(10)

        # 点击弹框
        self.browser.driver.find_element(
            By.CSS_SELECTOR, '.okui-btn.btn-xs.btn-fill-highlight.filter-search-form-btn').click()
        time.sleep(2)
        # 获取弹框
        window_dialog = self.browser.driver.find_element(
            By.CSS_SELECTOR, 'div.okui-dialog-window')
        time.sleep(2)
        # 点击选择网络下拉框
        window_dialog.find_elements(
            By.CSS_SELECTOR, '.okui-input.okui-input-md.okui-select-value')[0].click()
        time.sleep(random.random() + 1)
        # 选择网络
        window_dialog.find_elements(By.CSS_SELECTOR, '.okui-select-item.okui-select-item-border-box')[
            network_index].click()
        time.sleep(random.random() + 1)
        for address in address_list:
            # 输入address
            window_dialog.find_elements(
                By.CSS_SELECTOR, 'input[placeholder*=".crypto domain"]')[-1].send_keys(address)
            time.sleep(random.random() + 1)
            if address_list[-1] != address:
                # 点击继续添加地址
                window_dialog.find_element(
                    By.CSS_SELECTOR, 'div.add-address-form-btn').click()
                time.sleep(random.random() + 1)

        time.sleep(random.random() + 1)

        # 设为免验证地址，后续提现无需验证
        window_dialog.find_elements(
            By.CSS_SELECTOR, '.okui-checkbox')[0].click()
        time.sleep(1)
        # 保存为通用地址，同网络下其他币种也可用此地址提币
        window_dialog.find_elements(
            By.CSS_SELECTOR, '.okui-checkbox')[1].click()
        time.sleep(1)
        send_code_button_list = window_dialog.find_elements(By.CSS_SELECTOR, '.okui-input-code-btn')
        # 点击发送邮箱验证码
        send_code_button_list[0].click()

        # 接收邮箱验证码
        # 仅支持outlook处理
        email = None
        email_verify_code = None
        retry_count = 0
        while retry_count < 10:
            time.sleep(10)
            emails = self.imap.search(
                ".okx.com", "验证码", "验证码")
            if len(emails) > 0:
                email = emails[-1]
                self.imap.delete_email(emails[-1]["num"])
                break
            else:
                retry_count += 1
                print("No Email")
        if email:
            extract_response = extract_verification_code(email["body"][0][0:3500])
            if extract_response["code"] != 0:
                print("邮箱接收验证码失败2")
            else:
                email_verify_code = extract_response["data"]

                # 输入邮箱验证码
                window_dialog.find_elements(By.CSS_SELECTOR, 'input[maxlength="6"]')[0].click()
                ActionChains(self.browser.driver).send_keys(email_verify_code).send_keys(
                    Keys.TAB
                ).perform()
                # window_dialog.find_elements(By.CSS_SELECTOR, 'input[maxlength="6"]')[
                #     0].send_keys(email_verify_code)

        else:
            print("邮箱接收验证码失败1")

        time.sleep(1)
        # 点击发送短信验证码
        send_code_button_list[1].click()
        # 接收短信验证码
        sms_verify_code = None
        retry_count = 0
        okx_path_url = "http://47.92.250.119:8080/resource-api/okx/get_sms"
        while retry_count < 10:
            time.sleep(10)
            response = requests.get(url=okx_path_url, headers=self.headers)
            if response.status_code != 200:
                print("No SMS")
                retry_count += 1
            response = response.json()
            if response["data"] is None or response["data"]["okx_sms"] is None:
                print("No Data SMS")
                retry_count += 1
            else:
                sms_verify_code = str(response["data"]["okx_sms"])
                break
        if sms_verify_code:
            # 输入短信验证码
            window_dialog.find_elements(By.CSS_SELECTOR, 'input[maxlength="6"]')[1].click()
            ActionChains(self.browser.driver).send_keys(sms_verify_code).send_keys(
                Keys.TAB
            ).perform()
            # window_dialog.find_elements(By.CSS_SELECTOR, 'input[maxlength="6"]')[1].send_keys(sms_verify_code)

        time.sleep(1)

        if email_verify_code and sms_verify_code:
            # 点击确认按钮
            window_dialog.find_elements(By.CSS_SELECTOR, 'span.btn-content')[0].click()
            return True
        else:
            return False
