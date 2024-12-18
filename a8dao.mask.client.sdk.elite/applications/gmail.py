import hashlib
import re
import time
import uuid
from typing import Optional

from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select
from selenium.webdriver.support.wait import WebDriverWait

import api.remote.resource.sms
import tools.text
from api.remote.resource.aigc import extract_verification_code
from fingerprint.browser import Browser
from tools.imap import Imap
from tools.logger import task_log


class Gmail:
    def __init__(self, task_id: str, browser: Browser) -> None:
        self.task_id = task_id
        self.browser = browser
        self.imap = Imap()
        pass

    def signup(self, role: dict, country: str) -> dict:
        self.browser.get("https://accounts.google.com/")
        self.browser.wait(5, 10)
        button_elements = self.browser.find_elements_and_wait("button")
        self.browser.click(button_elements[-1])
        ul_element = self.browser.find_elements_and_wait("ul")[0]
        li_element = ul_element.find_elements(By.CSS_SELECTOR, "li")[0]
        self.browser.click(li_element)
        task_log(self.task_id, "Personal useage selected")
        self.browser.wait(5, 10)

        if self.browser.driver.current_url.startswith(
            "https://accounts.google.com/signup/v2"
        ):
            return self._signup_v2(role, country)
        return self._signup_v3(role, country)

    def _signup_v2(self, role: dict, country: str) -> dict:
        response = {"code": 0, "message": "OK", "data": {}}
        task_log(self.task_id, "Start signup v2")
        task_log(self.task_id, "Start to process names")
        first_name_input_element = self.browser.find_element_and_wait("#firstName")
        self.browser.send_keys(first_name_input_element, role["firstname"])
        last_name_input_element = self.browser.find_element_and_wait("#lastName")
        self.browser.send_keys(last_name_input_element, role["lastname"])
        sumbit_button_element = self.browser.find_element_and_wait("button")
        self.browser.click(sumbit_button_element)
        task_log(self.task_id, "Finish process names")
        self.browser.wait(10, 15)
        task_log(self.task_id, "Start to process birthday and gender")
        day_input_element = self.browser.find_element_and_wait("#day")
        self.browser.send_keys(day_input_element, str(role["day"]))
        month_select_element = Select(self.browser.find_element_and_wait("#month"))
        self.browser.wait(1, 3)
        month_select_element.select_by_value(str(role["month"]))
        self.browser.wait(1, 3)
        year_input_element = self.browser.find_element_and_wait("#year")
        self.browser.send_keys(year_input_element, str(role["year"]))
        gender_select_element = Select(self.browser.find_element_and_wait("#gender"))
        self.browser.wait(1, 3)
        gender_select_element.select_by_value(str(role["gender"]))
        self.browser.wait(1, 3)
        sumbit_button_element = self.browser.find_element_and_wait("button")
        self.browser.click(sumbit_button_element)
        task_log(self.task_id, "Finish process birthday and gender")
        self.browser.wait(10, 15)

        task_log(self.task_id, "Start to process email")
        radio_elements = self.browser.find_elements_and_wait("div[role='radio']")
        if len(radio_elements) > 0:
            self.browser.click(radio_elements[-1])
            self.browser.wait(1, 3)
        email_input_element = self.browser.find_element_and_wait(
            "input[name='Username']"
        )
        email_header = self._generate_email_prefix(role)
        self.browser.send_keys(email_input_element, email_header)
        sumbit_button_element = self.browser.find_element_and_wait("#next")
        self.browser.click(sumbit_button_element)
        task_log(self.task_id, "Finish process birthday and gender")
        self.browser.wait(10, 15)

        task_log(self.task_id, "Start to process password")
        password = tools.text.generate_password(16)
        password_input_elements = self.browser.find_elements_and_wait(
            "input[type='password']"
        )
        self.browser.send_keys(password_input_elements[0], password)
        self.browser.send_keys(password_input_elements[1], password)
        sumbit_button_element = self.browser.find_element_and_wait(
            "#createpasswordNext"
        )
        self.browser.click(sumbit_button_element)
        task_log(self.task_id, "Finish process birthday and gender")
        self.browser.wait(10, 15)

        process_phone_number_response = self._process_phone_number(role, country)
        if process_phone_number_response["code"] != 0:
            return process_phone_number_response

        task_log(self.task_id, "Start to skip recovery email")
        button_elements = self.browser.find_elements_and_wait("button")
        self.browser.click(button_elements[1])
        task_log(self.task_id, "Finish skip recovery email")
        self.browser.wait(5, 10)

        task_log(self.task_id, "Start to skip recovery phone number")
        button_elements = self.browser.find_elements_and_wait("button")
        self.browser.click(button_elements[1])
        task_log(self.task_id, "Finish skip recovery phone number")
        self.browser.wait(5, 10)
        task_log(self.task_id, "Start to process terms and policy")
        button_elements = self.browser.find_elements_and_wait("button")
        self.browser.click(button_elements[0])
        self.browser.wait(5, 10)

        button_elements = self.browser.find_elements_and_wait("button")
        self.browser.click(button_elements[3])
        task_log(self.task_id, "Finish process terms and policy")
        self.browser.wait(15, 30)

        response["data"] = {
            "email": f"{email_header}@gmail.com",
            "password": password,
        }
        task_log(self.task_id, "Finish signup v2")
        return response

    def _signup_v3(self, role: dict, country: str) -> dict:
        response = {"code": 0, "message": "OK", "data": {}}
        try:
            input_elements = self.browser.find_elements_and_wait("input")
            self.browser.send_keys(input_elements[0], role["firstname"])
            self.browser.send_keys(input_elements[1], role["lastname"])
            email_header = self._generate_email_prefix(role)
            input_elements[2].clear()
            self.browser.send_keys(input_elements[2], email_header)

            password = tools.text.generate_password(16)
            self.browser.send_keys(input_elements[3], password)
            self.browser.send_keys(input_elements[4], password)
            button_elements = self.browser.find_elements_and_wait("button")
            self.browser.click(button_elements[1])
            task_log(self.task_id, "Submit signup informations")
            self.browser.wait(5, 10)

            process_phone_number_response = self._process_phone_number(role, country)
            if process_phone_number_response["code"] != 0:
                return process_phone_number_response

            input_elements = self.browser.find_elements_and_wait("input")
            self.browser.send_keys(input_elements[2], str(role["day"]))
            month_select_element = Select(
                self.browser.find_element_and_wait("select#month")
            )
            self.browser.wait(1, 3)
            month_select_element.select_by_value(str(role["month"]))
            self.browser.wait(1, 3)
            self.browser.send_keys(input_elements[3], str(role["year"]))
            gender_select_element = Select(
                self.browser.find_element_and_wait("select#gender")
            )
            self.browser.wait(1, 3)
            gender_select_element.select_by_value(str(role["gender"]))
            self.browser.wait(1, 3)
            button_elements = self.browser.find_elements_and_wait("button")
            self.browser.click(button_elements[0])
            task_log(self.task_id, "Submit personal infomations")
            self.browser.wait(5, 10)
            button_elements = self.browser.find_elements_and_wait("button")
            self.browser.click(button_elements[3])
            self.browser.wait(5, 10)
            button_elements = self.browser.find_elements_and_wait("button")
            self.browser.click(button_elements[3])
            self.browser.wait(5, 10)
            response["data"] = {
                "email": f"{email_header}@gmail.com",
                "password": password,
            }
            return response
        except Exception as e:
            response["code"] = 2
            response["message"] = str(e)
            return response

    def enable_forward(
        self, forward_email: str, forward_password: str, email: str
    ) -> dict:
        response = {"code": 0, "message": "OK", "data": {}}
        input_button_elements = []
        retry_count = 0
        while retry_count < 3:
            self.browser.get("https://mail.google.com/mail/u/0/#settings/fwdandpop")
            task_log(self.task_id, "Open forward settings page and wait")
            self.browser.wait(15, 30)

            input_button_elements = self.browser.find_elements_and_wait(
                "input[type='button']", 5
            )
            if len(input_button_elements) > 0:
                break
            retry_count += 1
        if len(input_button_elements) == 0:
            response["code"] = 1
            response["message"] = "Open forward settings page failed"
            return response

        self.browser.click(input_button_elements[0])
        forward_input_element = self.browser.find_element_and_wait(
            "div[role='alertdialog'] input"
        )
        self.browser.send_keys(forward_input_element, forward_email)

        button_elements = self.browser.find_elements("div[role='alertdialog'] button")
        self.browser.click(button_elements[0])
        task_log(self.task_id, "Submit forward email and wait to verify")
        self.browser.switch_to(-1)
        submit_element = self.browser.find_element_and_wait("input[type='submit']")
        self.browser.click(submit_element)
        if not self.imap.login(forward_email, forward_password):
            response["code"] = 2
            response["message"] = "Forward email login failed"
            return response

        forward_retry_count = 0
        verify_code: Optional[str] = None
        while forward_retry_count < 30:
            emails = self.imap.search("forwarding-noreply@google.com", content=email)
            if len(emails) > 0:
                retry_count = 0
                while retry_count < 3:
                    try:
                        extract_response = extract_verification_code(
                            emails[-1]["body"][0]
                        )
                        if extract_response["code"] == 0:
                            verify_code = extract_response["data"]
                            break
                    except Exception as e:
                        task_log(self.task_id, str(e))

                if verify_code:
                    self.imap.delete_email(emails[0]["num"])
                    break
            self.browser.wait(10, 15)
            forward_retry_count += 1

        if not verify_code:
            response["code"] = 3
            response["message"] = "Forward email verify code not found"
            return response

        self.browser.switch_to(0)
        confirm_button_element = self.browser.find_element_and_wait(
            "div[role='alertdialog'] button"
        )
        self.browser.click(confirm_button_element)

        verify_input_element = self.browser.find_element_and_wait(
            "input[act='verifyText']"
        )
        verify_input_element.clear()
        self.browser.send_keys(verify_input_element, verify_code)
        verify_button_element = self.browser.find_element_and_wait(
            "input[act='verify']"
        )
        self.browser.click(verify_button_element)
        self.browser.wait(5, 10)
        return response

    def _process_phone_number(self, role: dict, country: str) -> dict:
        response = {"code": 0, "message": "ok"}
        phone_number: Optional[str] = None
        number_retry_count = 0
        task_log(self.task_id, "Start to process sms code")
        while number_retry_count < 10:
            get_number_response = api.remote.resource.sms.get_number("go", country)
            if get_number_response["code"] == 0:
                phone_number = str(get_number_response["data"])
                tel_input_element = self.browser.find_element_and_wait("#phoneNumberId")
                self.browser.send_keys(tel_input_element, phone_number)
                button_elements = self.browser.find_elements_and_wait("button")
                self.browser.click(button_elements[0])
                task_log(self.task_id, "Submit phone number")
                self.browser.wait(10, 15)

                if len(self.browser.find_elements("#code")) > 0:
                    task_log(self.task_id, "Phone number is vaild")
                    break
                else:
                    task_log(
                        self.task_id,
                        f"Phone number is invaild, retry times {number_retry_count+1}",
                    )
                    api.remote.resource.sms.release_number(phone_number)
                    phone_number = None
                    tel_input_element = self.browser.find_element_and_wait(
                        "#phoneNumberId"
                    )
                    tel_input_element.clear()
                    self.browser.wait(1, 3)
            else:
                task_log(
                    self.task_id,
                    f"failed to get phone number, retry times {number_retry_count+1}",
                )
            number_retry_count += 1

        if phone_number is None:
            response["code"] = 1
            response["message"] = "Phone number retry max times"
            return response

        sms_code: Optional[str] = None

        retry_count = 0
        task_log(self.task_id, f"Wait to recieve sms code")
        while retry_count < 20:
            sms_response = api.remote.resource.sms.get_code(phone_number)
            if sms_response["code"] == 0:
                sms_code = sms_response["data"]
                task_log(self.task_id, f"Recieve sms code {sms_code}")
                break
            else:
                retry_count += 1
                self.browser.wait(10, 15)

        if sms_code is None:
            api.remote.resource.sms.release_number(phone_number)
            response["code"] = 2
            response["message"] = "SMS code not activated"
            return response

        smscode_input_element = self.browser.find_element_and_wait("input")
        self.browser.send_keys(smscode_input_element, sms_code)
        self.browser.wait(1, 3)
        button_elements = self.browser.find_elements_and_wait("button")
        self.browser.click(button_elements[0])
        task_log(self.task_id, "Finish process sms code")
        self.browser.wait(10, 15)
        return response

    def _generate_email_prefix(self, role: dict) -> str:
        str_header = f'{role["lastname"]}{role["firstname"]}{uuid.uuid4().hex}'
        email_header_md5 = hashlib.md5()
        email_header_md5.update(str_header.encode("utf-8"))
        return email_header_md5.hexdigest()[:16]

    def login(
        self, account: str, password: str, preregistered_email: Optional[str] = None
    ) -> bool:
        driver = self.browser.driver

        task_log(self.task_id, "login gmail")
        self.browser.get("https://accounts.google.com/signin/v2")
        if driver.current_url[:29] == "https://myaccount.google.com/":
            return True
        "https://myaccount.google.com/?utm_source=sign_in_no_continue&pli=1"[:10]
        try:
            self.login_with_username_password(account, password, preregistered_email)
        except TimeoutException:
            btns = driver.find_elements(By.TAG_NAME, "button")
            if len(btns) == 1:
                task_log(self.task_id, "have to confirm login")

                btns[0].click()
                time.sleep(2)

                try:
                    self.login_with_username_password(
                        account, password, preregistered_email
                    )
                except TimeoutException:
                    time.sleep(20)

        time.sleep(5)
        self.browser.get("https://mail.google.com/")
        return (
            driver.current_url == "https://mail.google.com/mail/u/0/#inbox"
            or driver.current_url == "https://mail.google.com/mail/u/0/"
        )

    def login_with_username_password(
        self, account: str, gmail_psw: str, preregistered_email: Optional[str] = None
    ) -> None:
        driver = self.browser.driver

        task_log(self.task_id, "login gmail in with username and password")

        if not driver.find_elements(By.ID, "identifierId"):
            if not driver.find_elements(By.NAME, "password"):
                self.__use_another_account_to_login()
            else:
                driver.find_element(By.NAME, "password").send_keys(gmail_psw)
                driver.find_element(By.ID, "passwordNext").click()

        account_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "identifierId"))
        )

        time.sleep(2)

        if account_input.is_displayed():
            task_log(self.task_id, "enter the gmail account")
            account_input.send_keys(account)
            driver.find_element(By.ID, "identifierNext").click()

        psw_or_captcha = WebDriverWait(driver, 10).until(
            EC.any_of(
                EC.visibility_of_element_located((By.ID, "captchaimg")),
                # EC.visibility_of_element_located((By.NAME, "password")),
                EC.visibility_of_element_located((By.NAME, "Passwd")),
            )
        )

        if psw_or_captcha.get_attribute("id") == "captchaimg":
            task_log(self.task_id, "waiting for inputing captcha")
            psw_input = WebDriverWait(driver, 60).until(
                # EC.visibility_of_element_located((By.NAME, "password"))
                EC.visibility_of_element_located((By.NAME, "Passwd"))
            )
        else:
            psw_input = psw_or_captcha

        # time.sleep(2)
        task_log(self.task_id, "enter the password")

        psw_input.send_keys(gmail_psw)

        driver.find_element(By.ID, "passwordNext").click()

        time.sleep(3)

        try:
            select_preregistered_email = WebDriverWait(driver, 5).until(
                EC.presence_of_all_elements_located(
                    (
                        By.CSS_SELECTOR,
                        'path[d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 14H4V8l8 5 8-5v10zm-8-7L4 6h16l-8 5z"]',
                    )
                )
            )
            task_log(self.task_id, "select preregistered email")
            time.sleep(1)
            select_preregistered_email[1].click()

            task_log(self.task_id, "enter preregistered email")
            preregistered_email_input = WebDriverWait(driver, 3600).until(
                EC.visibility_of_element_located(
                    (By.ID, "knowledge-preregistered-email-response")
                )
            )
            time.sleep(1)
            preregistered_email_input.send_keys(preregistered_email)
            driver.find_element(By.TAG_NAME, "button").click()
        except TimeoutException:
            pass

        try:
            WebDriverWait(driver, 5).until(
                lambda d: len(
                    [
                        e
                        for e in d.find_elements(
                            By.CSS_SELECTOR, 'div[aria-live="assertive"]'
                        )
                        if e.is_displayed()
                    ]
                )
                > 1
            )

            raise GooglePasswordError("google password error")

        except TimeoutException:
            pass

    def __use_another_account_to_login(self):
        driver = self.browser.driver

        task_log(self.task_id, "use another gmail account to login")

        gmail_login_div = driver.find_elements(
            By.XPATH, "//div[contains(@aria-label,'@gmail.com')]"
        )

        if gmail_login_div:
            gmail_login_div[0].click()

            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.TAG_NAME, "ul")) == 2
            )

            driver.find_element(By.TAG_NAME, "ul").find_elements(By.TAG_NAME, "li")[
                -1
            ].click()
        else:
            WebDriverWait(driver, 10).until(
                lambda d: len(d.find_elements(By.TAG_NAME, "ul")) == 2
            )

            driver.find_element(By.TAG_NAME, "ul").find_elements(By.TAG_NAME, "li")[
                -2
            ].click()


class GooglePasswordError(Exception):
    def __init__(self, msg):
        self.msg = msg
