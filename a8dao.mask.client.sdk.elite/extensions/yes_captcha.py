import time
from selenium.webdriver.common.by import By
from fingerprint.browser import Browser


class YesCaptcha():
    def __init__(self, browser: Browser, config) -> None:

        self.browser = browser
        self.config = config
        pass

    def browser_init(self) -> None:
        if self.config["enable"]:
            self.browser.driver.get(self.config["url"])
            self.browser.wait_document_load_complete()
            time.sleep(0.1)
            inputs = self.browser.driver.find_elements(
                By.CSS_SELECTOR, 'input[type="text"]')
            inputs[0].send_keys(self.config["api_key"])
            time.sleep(0.1)
            save_button = self.browser.driver.find_elements(
                By.TAG_NAME, "button")[-1]
            save_button.click()
            self.browser.wait_document_load_complete()
            count = 0
            while count < 10:
                if len(self.browser.driver.find_elements(By.CSS_SELECTOR, "button")) > 1:
                    count = count + 1
                    time.sleep(3)
                else:
                    break
        pass
