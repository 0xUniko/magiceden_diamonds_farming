import os
import random

import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait

import api.remote.resource.aigc
from extensions.metamask import MetaMask
from fingerprint.browser import Browser
from tools.logger import task_log


class MintSquare:
    def __init__(self, task_id: str, browser: Browser, metamask: MetaMask) -> None:
        self.task_id = task_id
        self.browser = browser
        self.metamask = metamask
        pass

    def home_mint(self):
        task_log(self.task_id, "got to https://mintsquare.io/zksync")
        self.browser.initialized_get("https://mintsquare.io/zksync")
        self.browser.find_element_and_wait("mui-6", By.ID).click()

    def connect_wallet(self, password: str):
        self.metamask.unlock(password)
        task_log(self.task_id, "connect_wallet")
        self.browser.find_element_and_wait("mui-4", By.ID).click()
        self.browser.find_element_and_wait("mui-13", By.ID).click()
        self.metamask.connect()
        self.browser.find_elements_and_wait("div[size='24'].sc-hLBbgP.hoZIJV")[
            -1
        ].click()

    def generate_image(self, candidates: list[str]):
        task_log(self.task_id, "generate image")
        prompt = random.choice(candidates)
        pic_url = api.remote.resource.aigc.image(
            f"a picture include {prompt}", "512x512")["data"]
        pic = requests.get(pic_url).content
        if not os.path.exists("c:/mintsquare"):
            os.makedirs("c:/mintsquare")
        with open(f"c:/mintsquare/{prompt}.jpg", "wb") as f:
            f.write(pic)

    def mint(self):
        task_log(self.task_id, "mint")
        dir_path = "c:/mintsquare"
        file_list = [
            os.path.join(dir_path, f)
            for f in os.listdir(dir_path)
            if f.endswith(".jpg")
        ]
        assert len(file_list) > 0, "jpg not found in directory"
        first_jpg_path = file_list[0]
        first_jpg_name = os.path.basename(first_jpg_path)
        task_log(self.task_id, "mint")
        self.browser.get("https://mintsquare.io/mint")
        self.browser.find_element_and_wait(
            "input[type=file]").send_keys(first_jpg_path)
        self.browser.find_element_and_wait("#name").send_keys(first_jpg_name)
        self.browser.find_element_and_wait("#mui-6").click()
        self.metamask.confirm(15)
