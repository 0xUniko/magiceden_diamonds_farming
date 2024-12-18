from extensions.metamask import MetaMask
from fingerprint.browser import Browser
from tools.logger import task_log


class Tevaera:
    def __init__(self, task_id: str, browser: Browser, metamask: MetaMask) -> None:
        self.task_id = task_id
        self.browser = browser
        self.metamask = metamask
        pass

    def home_mint(self):
        task_log(self.task_id, "got to https://tevaera.com/login")
        self.browser.initialized_get("https://tevaera.com/login")

    def connect_wallet(self, password: str):
        self.metamask.unlock(password)
        task_log(self.task_id, "connect_wallet")
        self.browser.find_element_and_wait(
            "button.hover-pointer.teva-btn-secondary.position-relative"
        ).click()
        self.metamask.connect()
        self.metamask.confirm()

        pass

    def mint_nfts(self):
        task_log(self.task_id, "mint_nfts")
        self.browser.find_element_and_wait(
            ".condition-model-footer.modal-footer > button"
        ).click()
        self.browser.find_element_and_wait(
            "button.col-lg-3.profile-buttons.teva-btn-primary.mt-3"
        ).click()
        self.metamask.confirm()
        self.browser.find_element_and_wait("button.swal2-confirm.swal2-styled").click()
        self.browser.find_element_and_wait(
            "button.btn.btn-secondary.col-lg-3.profile-buttons.teva-btn-primary"
        ).click()
        self.metamask.confirm()
