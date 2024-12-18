from extensions.metamask import MetaMask
from fingerprint.browser import Browser
from model import ChainId
from tools.logger import task_log


class XMetaWeb:
    def __init__(
        self, task_id: str, browser: Browser, extension: MetaMask, host: str
    ) -> None:
        self.task_id = task_id
        self.browser = browser
        self.extension = extension
        self.host = host
        pass

    def login(self, user_name: str, password: str) -> bool:
        url = f"{self.host}/#/pages/public/login"
        self.browser.get(url)
        self.browser.wait(3, 5)
        self.extension.switch_to_network(ChainId.ETH_ARBITRUM, False)
        input_elements = self.browser.find_elements_and_wait(".uni-input-input")
        if len(input_elements) > 1:
            self.browser.send_keys(input_elements[0], user_name, True)
            self.browser.send_keys(input_elements[1], password, True)
            self.browser.click(self.browser.find_element_and_wait("uni-button"))
            self.browser.wait(3, 5)
            return True
        else:
            return False

    def connect(self) -> None:
        task_log(self.task_id, "Connect wallet")
        self.browser.get(f"{self.host}/#/pages/user/index")

        self.browser.wait(5, 8)
        self.browser.click(self.browser.find_element_and_wait("uni-view.rounded-full"))
        self.browser.wait(3, 5)
        self.browser.click(self.browser.find_element_and_wait("uni-text.rounded-full"))
        self.browser.wait(3, 5)
        self.extension.click()
        pass

    def sell(self, price: float, token_id: int, collection_name: str) -> None:
        task_log(self.task_id, "Start to Sell nft")
        self.browser.get(f"{self.host}/#/pages/user/index")
        self.browser.wait(1, 3)
        search_input_element = self.browser.find_element_and_wait("input")
        self.browser.send_keys(search_input_element, token_id, True, True)
        self.browser.wait(3, 5)
        index = 0
        product_elements = self.browser.find_elements_and_wait(
            ".relative.rounded-lg.overflow-hidden"
        )
        product_collection_name_elements = self.browser.find_elements_and_wait(
            ".relative.rounded-lg.overflow-hidden .text-sm.truncate"
        )

        for i in range(len(product_collection_name_elements)):
            index = i
            if product_collection_name_elements[i].text == collection_name:
                self.browser.click(product_elements[i])

                break
        list_button_elements = self.browser.find_elements_and_wait(
            ".bg-light-black.text-green-400.rounded-md.py-1.px-2"
        )
        self.browser.click(list_button_elements[index * 2])
        list_button_confirm_element = self.browser.find_element_and_wait(
            ".rounded-lg.text-sm.bg-gradient-to-r.from-green-1000.to-blue-1000.px-2.py-1.text-center.text-white"
        )
        self.browser.click(list_button_confirm_element)

        price_element = self.browser.find_element_and_wait(
            "uni-page-body uni-view uni-view.mx-2.py-2 uni-view uni-view:nth-child(3) uni-view.u-input.flex-1.u-border.u-input--radius.u-input--square uni-view uni-view uni-input div input"
        )

        self.browser.send_keys(price_element, price, True)
        listing_button_element = self.browser.find_element_and_wait("uni-button")
        self.browser.click(listing_button_element)
        self.extension.click(timeout=15)
        self.browser.wait(3, 5)
        pass

    def buy(self, product_id: int) -> None:
        task_log(self.task_id, "Start to Buy nft")

        self.browser.get(f"{self.host}/#/pages/collection/detail?id={product_id}&=")
        self.browser.wait(3, 5)
        sell_tab_element = self.browser.find_element_and_wait(
            ".u-tabs__wrapper__nav__item.u-tabs__wrapper__nav__item-1"
        )
        self.browser.driver.execute_script(
            "arguments[0].scrollIntoView()", sell_tab_element
        )
        self.browser.click(sell_tab_element)
        self.browser.wait(3, 5)
        self.browser.click(self.browser.find_element_and_wait(".bg-green-1000"))
        self.browser.wait(3, 5)
        input_elements = self.browser.find_elements_and_wait("input")
        self.browser.send_keys(input_elements[-1], "1", True)
        self.browser.click(self.browser.find_element_and_wait("uni-button"))
        self.extension.click(15)
        self.browser.wait(3, 5)
        pass

    def delist(self, product_id: int) -> None:
        pass

    def mint(self, series_id: int) -> None:
        task_log(self.task_id, "Start to mint")
        self.browser.get(f"#/pages/issue/detail?id={series_id}&=")
        self.browser.wait(3, 5)
        self.browser.click(self.browser.find_elements_and_wait("uni-button")[-1])
        self.browser.wait(3, 5)
        self.browser.click(self.browser.find_element_and_wait("uni-button"))
        self.extension.click()
        self.browser.wait(3, 5)
        button_element = self.browser.find_element_and_wait(".uni-modal__btn_primary")
        assert len(button_element.text) > 0
        pass
