import random
import time

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

from fingerprint.browser import Browser
from tools.logger import task_log


class Discord:
    def __init__(self, task_id: str, browser: Browser) -> None:
        self.browser = browser
        self.task_id = task_id
        self.in_channel_url_prefix = "https://discord.com/channels/"
        pass

    # 登录
    def login(self, config) -> bool:
        task_log(self.task_id, "Discord登录")
        try:
            self.browser.get("https://discord.com/login")
            js = 'function login(token) {setInterval(() => {document.body.appendChild(document.createElement `iframe`).contentWindow.localStorage.token = `"${token}"`}, 50);setTimeout(() => {location.reload();}, 500);}'
            self.browser.driver.execute_script(
                js + 'login("' + config["token"] + '")')
            time.sleep(5)
            WebDriverWait(self.browser.driver, 10).until(
                EC.url_contains(self.in_channel_url_prefix)
            )
            return self.browser.driver.current_url[:29] == self.in_channel_url_prefix
        except Exception as e:
            task_log(self.task_id, str(e))
        return False

    # 邀请
    def invite(self, url: str) -> bool:
        task_log(self.task_id, f"invite url is: {url}")
        try:
            self.browser.get(url)
            time.sleep(random.uniform(2, 4))
            submit_button = self.browser.driver.find_element(
                By.CSS_SELECTOR, "button")
            submit_button.click()
            self.browser.wait_document_load_complete()
            time.sleep(random.uniform(2, 4))
            WebDriverWait(self.browser.driver, 30).until(
                EC.url_contains(self.in_channel_url_prefix)
            )
            return self.browser.driver.current_url[:29] == self.in_channel_url_prefix

        except Exception as e:
            task_log(self.task_id, str(e))
        return False

    # 进入频道
    def enter_channel(self, discord_url: str) -> bool:
        """进入频道"""
        return False

    # 发送消息
    def fundatmental_verification(self) -> bool:
        """初始验证方法"""
        try:
            btns = WebDriverWait(self.browser.driver, 10).until(
                EC.presence_of_all_elements_located(
                    (By.CLASS_NAME, "contents-3ca1mk"))
            )

            [b for b in btns if b.text == "Complete"][0].click()

            WebDriverWait(self.browser.driver, 10).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[type=checkbox]")
                )
            ).click()

            [
                c
                for c in self.browser.driver.find_elements(
                    By.CLASS_NAME, "contents-3ca1mk"
                )
                if c.text == "Submit"
            ][0].click()

            WebDriverWait(self.browser.driver, 10).until(
                lambda d: len(
                    [
                        e
                        for e in d.find_elements(By.CLASS_NAME, "contents-3ca1mk")
                        if e.text == "Complete"
                    ]
                )
                == 0
            )

            return True
        except Exception as e:
            task_log(self.task_id, str(e))
        return False

    def registry(
        self, email: str, username: str, password: str, year: int, month: int, day: int
    ):
        """注册"""
        task_log(self.task_id, "Discord注册")
        response = {"code": 0, "message": "OK", "data": {}}
        try:
            self.browser.get("https://discord.com/register")
            self.browser.find_element_and_wait(
                "email", By.NAME).send_keys(email)
            self.browser.find_element_and_wait(
                "username", By.NAME).send_keys(username)
            self.browser.find_element_and_wait(
                "password", By.NAME).send_keys(password)
            birth = self.browser.find_elements_and_wait(".css-1hwfws3")
            birth[0].click()
            ActionChains(self.browser.driver).send_keys(month).perform()
            ActionChains(self.browser.driver).send_keys(Keys.TAB).perform()
            birth[1].click()
            ActionChains(self.browser.driver).send_keys(day).perform()
            birth[2].click()
            ActionChains(self.browser.driver).send_keys(year).perform()
            self.browser.find_element("button[type=submit]").click()
            try:
                WebDriverWait(self.browser.driver, 120).until(
                    lambda d: d.current_url == "https://discord.com/channels/@me"
                )
            except:
                raise Exception("破解验证码失败")
            return response
        except Exception as e:
            task_log(self.task_id, str(e))
            response["code"] = 1
            response["message"] = str(e)
        return response
