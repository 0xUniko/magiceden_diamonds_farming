import logging
import time
from typing import List

from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

# from applications.gmail import Gmail
from fingerprint.browser import Browser
from tools.logger import task_log


class Twitter:
    def __init__(self, task_id: str, browser: Browser) -> None:
        self.browser = browser
        self.task_id = task_id

    def is_logged_in(self):
        self.browser.driver.get("https://twitter.com")

        time.sleep(2)
        # WebDriverWait(self.browser.driver, 10).until(
        #     lambda d: d.current_url == "https://twitter.com/home"
        # )

        if self.browser.driver.find_elements(
            By.CSS_SELECTOR, "div[data-testid=SideNav_AccountSwitcher_Button]"
        ):
            task_log(self.task_id, "already logged in")
            return True
        else:
            task_log(self.task_id, "not logged in")
            return False

    def token_login(self, token: str) -> dict:
        task_log(self.task_id, "twitter login")
        response = {"code": 0,
                    "message": "login twitter successfully", "data": {}}
        self.browser.get("https://twitter.com/i/flow/login")
        self.browser.wait(3, 5)

        for cookie in self.browser.driver.get_cookies():
            if cookie["domain"] == ".twitter.com":
                self.browser.driver.delete_cookie(cookie["name"])
        self.browser.driver.add_cookie(
            {"name": "auth_token", "value": token})
        self.browser.get("https://www.twitter.com")

        count = 0
        while count < 10:
            if self.browser.driver.current_url == "https://twitter.com/home":
                self.close_mask()
                return response
            else:
                count += 1
                time.sleep(1)
        response["code"] = 1
        response["message"] = "twitter login failed"
        return response

    def login(
        self,
        token: str | None = None,
        name: str | None = None,
        password: str | None = None,
    ) -> dict:
        task_log(self.task_id, "twitter登录")
        response = {"code": 0,
                    "message": "login twitter successfully", "data": {}}
        try:
            self.browser.get("https://twitter.com/i/flow/login")
            if token is not None:
                time.sleep(2)
                for cookie in self.browser.driver.get_cookies():
                    if cookie["domain"] == ".twitter.com":
                        self.browser.driver.delete_cookie(cookie["name"])
                self.browser.driver.add_cookie(
                    {"name": "auth_token", "value": token})
                self.browser.get("https://www.twitter.com")

                count = 0
                while count < 10:
                    if self.browser.driver.current_url == "https://twitter.com/home":
                        self.close_mask()
                        return response
                    else:
                        count += 1
                        time.sleep(1)

            assert name is not None and password is not None
            WebDriverWait(self.browser.driver, 30).until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "input[autocomplete=username]")
                )
            ).send_keys(name)

            WebDriverWait(self.browser.driver, 30).until(
                lambda d: len(d.find_elements(
                    By.CSS_SELECTOR, "div[role=button]")) == 4
            )

            buttons = self.browser.driver.find_elements(
                By.CSS_SELECTOR, "div[role=button]"
            )
            # assert len(
            #     buttons) == 4, 'login page should have accurately 4 buttons'
            buttons[2].click()
            # for button in buttons:
            #     if button.text == "Next":
            #         button.click()
            #         time.sleep(1)
            #         break

            # input_name_list = self.browser.driver.find_elements(
            #    By.CSS_SELECTOR, 'input[name=text]')
            # if len(input_name_list) == 1:
            #     input_name_list[0].send_keys(config["name"])
            #     self.browser.driver.find_elements(
            #         By.CSS_SELECTOR, 'div[role=button]')[1].click()
            #     time.sleep(3)
            #     self.browser.driver.find_elements(By.CSS_SELECTOR, 'input[name=password]')[
            #         0].send_keys(config["password"])
            # else:
            WebDriverWait(self.browser.driver, 30).until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, "input[name=password]")
                )
            )[0].send_keys(password)

            WebDriverWait(self.browser.driver, 30).until(
                lambda d: len(d.find_elements(
                    By.CSS_SELECTOR, "div[role=button]")) == 3
            )

            buttons = self.browser.driver.find_elements(
                By.CSS_SELECTOR, "div[role=button]"
            )
            buttons[2].click()
            # for button in buttons:
            #     if button.text == "Log in":
            #         button.click()
            #         time.sleep(1)
            #         break
            self.browser.wait_document_load_complete()
            time.sleep(5)

            if mask := self.browser.driver.find_elements(
                By.CSS_SELECTOR, "div[data-testid=confirmationSheetDialog]"
            ):
                assert len(mask) == 1

                btns = mask[0].find_elements(
                    By.CSS_SELECTOR, "div[role=button]")

                assert len(btns) == 1

                btns[0].click()

            count = 0
            while count < 10:
                if self.browser.driver.current_url == "https://twitter.com/home":
                    self.close_mask()
                    return response
                else:
                    count += 1
                    time.sleep(1)
            return {"code": 2, "message": "login fail"}

        except Exception as e:
            response["code"] = 2
            response["message"] = str(e)
            return response

    # 关注
    def follow(self, follow_url: str) -> bool:
        task_log(self.task_id, f"follow {follow_url}")
        self.browser.driver.get(follow_url)
        time.sleep(3)
        follow_button = self.browser.find_element_and_wait(
            "div[data-testid='confirmationSheetConfirm']")
        self.browser.click(follow_button)
        try:
            unfollow_div = self.browser.find_element_and_wait(
                "div[data-testid='placementTracking'] div[data-testid*='unfollow']", 3)
            return unfollow_div is not None
        except:
            return False

    # 关闭各种弹窗
    def close_mask(self):
        """
        关闭各种弹窗
        """
        if mask := self.browser.driver.find_elements(
            By.CSS_SELECTOR, "div[data-testid=sheetDialog]"
        ):
            assert len(mask) == 1

            btns = mask[0].find_elements(By.CSS_SELECTOR, "div[role=button]")

            if close_btn := [btn for btn in btns if not btn.text]:
                assert len(close_btn) == 1, "fail to locate close button"

                close_btn[0].click()
            else:
                ok_btn = [btn for btn in btns if btn.text]

                assert len(ok_btn) == 1, "fail to locate ok button"

                ok_btn[0].click()

    # 点赞
    def like(self, cell_inner_div: WebElement):
        cell_inner_div.find_element(
            By.CSS_SELECTOR, "div[data-testid=like]").click()

    # 转发
    def retweet(self, cell_inner_div: WebElement):
        cell_inner_div.find_element(
            By.CSS_SELECTOR, "div[data-testid=retweet]").click()

        WebDriverWait(self.browser.driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div[data-testid=retweetConfirm]")
            )
        ).click()

    # 回复
    def reply(self, cell_inner_div: WebElement, text: str):
        cell_inner_div.find_element(
            By.CSS_SELECTOR, "div[data-testid=reply]").click()

        dialog = WebDriverWait(self.browser.driver, 10).until(
            EC.visibility_of_element_located(
                (By.CSS_SELECTOR, "div[role=dialog]"))
        )

        dialog.find_element(
            By.CSS_SELECTOR, "div[role=textbox]").send_keys(text)

        time.sleep(1)

        dialog.find_element(
            By.CSS_SELECTOR, "div[data-testid=tweetButton]").click()

    # 滚动到指定位置
    def swipe_to(self, cell_inner_div: WebElement):
        self.browser.driver.execute_script(
            "arguments[0].scrollIntoView();", cell_inner_div
        )

    def enter_space(self, url: str):
        self.browser.get(url)
        self.browser.find_element_and_wait(
            ".css-18t94o4.css-1dbjc4n.r-1udnf30.r-1uusn97.r-h3s6tt.r-1ny4l3l.r-1udh08x.r-o7ynqc.r-6416eg.r-13qz1uu"
        ).click()

    def authorize_app(self):
        OAuth_Consent_Button = self.browser.find_element_and_wait(
            'div[data-testid="OAuth_Consent_Button"]'
        )
        self.browser.click(OAuth_Consent_Button)
        self.browser.wait(1, 2)

    def follow_by_intent(self, follow_url: str) -> None:
        task_log(self.task_id, f"follow {follow_url}")
        self.browser.get(follow_url)
        self.browser.click(
            self.browser.find_element_and_wait(
                "div[data-testid='confirmationSheetConfirm']"
            )
        )
        self.browser.wait(1, 2)
        pass

    def like_by_intent(self, url: str):
        # url is like https://twitter.com/intent/like?tweet_id=1735238464512364783
        task_log(self.task_id, f"like {url}")
        self.browser.get(url)
        self.browser.click(
            self.browser.find_element_and_wait(
                "div[data-testid='confirmationSheetConfirm']"
            )
        )
        self.browser.wait(1, 2)
        pass

    def tweet_by_intent(self, url: str):
        # url is like https://twitter.com/intent/tweet?text=Just%20entered%20a%20giveaway%20with%20200%20spots%20for%20%40TinFunNFT%20on%20%40OKX%2C%20come%20and%20join%21https://twitter.com/TinFunNFT/status/1735238464512364783
        task_log(self.task_id, f"tweet {url}")
        self.browser.get(url)
        self.browser.wait(1, 2)
        self.browser.click(
            self.browser.find_element_and_wait(
                'div[data-testid="tweetButton"]')
        )
        self.browser.wait(2, 3)
        pass

    def random_follow(self) -> List[str]:
        task_log(self.task_id, "random follow")
        self.browser.get("https://twitter.com/explore")
        follow_button_elements = self.browser.find_elements_and_wait(
            "div[data-testid*='follow']")
        for button in follow_button_elements:
            self.browser.click(button)
            self.browser.wait(1, 3)
        user_elements = self.browser.find_elements_and_wait(
            "div[data-testid='UserCell']")
        user_id_list: List[str] = []
        for user in user_elements:
            user_id_list.append(user.text.split(" ")[-1])
        return user_id_list
