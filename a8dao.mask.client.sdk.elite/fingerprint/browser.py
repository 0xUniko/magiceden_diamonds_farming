import json
import logging
import random
import time
from typing import Any, List, Optional

import retrying
from selenium.webdriver.chromium.webdriver import ChromiumDriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.keys import Keys


class Browser:
    def __init__(
        self, name: str, driver: ChromiumDriver, user_proxy=None
    ) -> None:
        self.name = name
        self.driver = driver
        self.driver.execute_cdp_cmd("Network.enable", {})
        self.user_proxy = user_proxy
        self.wait_document_load_complete()
        pass

    def wait_url(self, url: str, is_full_match: bool = False, count: int = 30) -> bool:
        current_count = 0
        if is_full_match:
            while current_count < count:
                if self.driver.current_url != url:
                    self.wait(1, 2)
                    current_count += 1
                else:
                    return True
        else:
            while current_count < count:
                if url not in self.driver.current_url:
                    self.wait(1, 2)
                    current_count += 1
                else:
                    return True
        return False

    def close(self) -> None:
        while len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[-1])
            self.driver.close()
        self.driver.quit()
        pass

    def switch_to(self, index: int = 0) -> None:
        self.driver.switch_to.window(self.driver.window_handles[index])
        pass

    def get(self, url: str, is_wait: bool = True) -> None:
        self.driver.get(url)
        if is_wait:
            self.wait(3, 5)
        pass

    def load_fetches(self) -> None:
        self.fetches = {}
        logs = [
            json.loads(log["message"])["message"]
            for log in self.driver.get_log("performance")
        ]
        for log in logs:
            if log["method"] == "Network.requestWillBeSent" and (
                log["params"]["type"].lower() == "xhr"
                or log["params"]["type"].lower() == "fetch"
            ):
                request_id = log["params"]["requestId"]
                self.fetches[request_id] = {"request": log["params"]}
        for log in logs:
            if log["method"] == "Network.responseReceived" and log["params"][
                "requestId"
            ] in list(self.fetches.keys()):
                try:
                    self.fetches[log["params"]["requestId"]]["response"] = (
                        self.driver.execute_cdp_cmd(
                            "Network.getResponseBody",
                            {"requestId": log["params"]["requestId"]},
                        )
                    )

                except Exception as e:
                    print(
                        f"Could not retrieve response body for {log['params']['response']['url']}: {str(e)}"
                    )

        pass

    def initialized_get(self, url: str) -> None:
        while len(self.driver.window_handles) > 1:
            try:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.driver.close()
            except:
                pass
        self.driver.switch_to.window(self.driver.window_handles[0])
        self.get(url)
        self.wait(3, 5)
        pass

    def get_parent(self, element: WebElement, parent_dom_index: int) -> WebElement:
        parent_str = ""
        for i in range(parent_dom_index):
            parent_str = parent_str + ".parentElement"
        return self.driver.execute_script("return arguments[0]" + parent_str, element)

    def clean_tabs(self):
        while len(self.driver.window_handles) > 1:
            try:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.wait_document_load_complete()
                self.driver.close()
            except:
                pass
        self.driver.switch_to.window(self.driver.window_handles[0])
        pass

    def clean_tabs_last(self):
        self.driver.switch_to.new_window("tab")
        while len(self.driver.window_handles) > 1:
            self.driver.switch_to.window(self.driver.window_handles[0])
            self.wait_document_load_complete()
            self.driver.close()
        self.driver.switch_to.window(self.driver.window_handles[0])

    def wait_load_completed(self):
        while True:
            if self.driver is not None:
                self.clean_tabs()
                break
            time.sleep(1)
        pass

    def wait_document_load_complete(self):
        while True:
            try:
                if (
                    self.driver.execute_script("return document.readyState")
                    == "complete"
                ):
                    break
                time.sleep(1)
            except Exception as e:
                logging.warning(e)
        pass

    def find_elements_and_until(
        self,
        css_selector: str,
        ec_func=EC.visibility_of_all_elements_located,
        timeout=30,
    ) -> List[WebElement]:
        try:
            return WebDriverWait(self.driver, timeout).until(
                ec_func((By.CSS_SELECTOR, css_selector))
            )
        except:
            return []

    def find_elements_and_wait(self, css_selector: str, timeout=30) -> List[WebElement]:
        try:
            return WebDriverWait(self.driver, timeout).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, css_selector))
            )
        except:
            return []

    def find_elements(self, css_selector: str) -> List[WebElement]:
        return self.driver.find_elements(By.CSS_SELECTOR, css_selector)

    def find_element(
        self, value: str = "", by: str = By.CSS_SELECTOR
    ) -> Optional[WebElement]:
        try:
            return self.driver.find_element(by, value)
        except:
            return None

    def find_element_and_until(
        self,
        css_selector: str,
        ec_func=EC.visibility_of_element_located,
        timeout: int = 30,
    ) -> WebElement | None:
        try:
            return WebDriverWait(self.driver, timeout).until(
                ec_func((By.CSS_SELECTOR, css_selector))
            )
        except:
            return None

    def find_element_and_wait(
        self, css_selector: str, by=By.CSS_SELECTOR, timeout=30
    ) -> WebElement:
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located((by, css_selector))
        )

    def send_keys(
        self,
        element: WebElement,
        text: Any,
        is_clickboard_mode: bool = False,
        is_enter: bool = False,
    ) -> None:
        if is_clickboard_mode:
            element.send_keys(str(text))
        else:
            for key in str(text):
                element.send_keys(key)
                time.sleep(random.uniform(0, 0.2))
        if is_enter:
            self.click(element, is_element_click=False)
            element.send_keys(Keys.ENTER)
        time.sleep(random.uniform(1, 1.5))
        pass

    def wait_tabs(self, tab_number: int, timeout: int = 30) -> bool:
        count = 0
        while count < timeout:
            if len(self.driver.window_handles) == tab_number:
                return True
            time.sleep(1)
            count = count + 1
        return False

    def wait_tabs_and_switch_to(self, tab_number: int, timeout: int = 30):
        count = 0
        while count < timeout:
            if len(self.driver.window_handles) >= tab_number:
                self.driver.switch_to.window(self.driver.window_handles[-1])
                self.wait_document_load_complete()
                break
            time.sleep(1)
            count = count + 1
        pass

    def switch_tabs(self, tab_number: int):
        currentWindowHandle = ""
        try:
            currentWindowHandle = self.driver.current_window_handle
        except Exception as e:
            logging.warning(e)
            logging.warning("Can not get currentWindowHandle.")
        try:
            if (
                len(currentWindowHandle) > 0
                or currentWindowHandle is not self.driver.window_handles[tab_number]
            ):
                self.driver.switch_to.window(self.driver.window_handles[tab_number])
                logging.info("Switch Tab %s" % tab_number)
                time.sleep(0.5)
        except Exception as e:
            logging.warning(e)
            logging.warning("Can not switch tab.")

    def click(
        self,
        web_element: WebElement,
        wait_range: List[int] = [1, 3],
        is_element_click: bool = True,
    ) -> None:
        try:
            if is_element_click:
                web_element.click()
            else:
                w_offset, h_offset = self.__get_offset__(web_element)
                actions = ActionChains(self.driver).move_to_element_with_offset(
                    web_element, w_offset, h_offset
                )
                actions.click().perform()
        except:
            web_element.click()
        self.wait(wait_range[0], wait_range[1])
        pass

    def wait(self, least: float, most: float) -> None:
        time.sleep(random.uniform(least, most))

    def __get_offset__(self, web_element: WebElement):
        h = web_element.size["height"] / 3
        h_offset = random.uniform(-h, h)
        w = web_element.size["width"] / 3
        w_offset = random.uniform(-w, w)
        return w_offset, h_offset

    def retry(self, func, max_attempts=10, wait_time=1000):
        """重试
        func: 执行方法 需返回Bool
        max_attempts: 最大重试次数(默认=10次)
        wait_time: 重试间隔(默认=1000毫秒)
        """

        @retrying.retry(stop_max_attempt_number=max_attempts, wait_fixed=wait_time)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            if not result:
                raise Exception("Function %s returned False" % func.__name__)
            return result

        return wrapper

    def find_elements_with_shadow_root(
        self, css_selector_shadow_segments: List[str], css_selector: str
    ) -> List[WebElement]:
        script = "return document"
        for css_selector_shadow in css_selector_shadow_segments:
            script += f'.querySelector("{css_selector_shadow}").shadowRoot'
        shadow_root: WebElement = self.driver.execute_script(script)
        if shadow_root is not None:
            return shadow_root.find_elements(By.CSS_SELECTOR, css_selector)
        return []
