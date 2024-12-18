from selenium.webdriver.common.by import By

from extensions.metamask import MetaMask
from fingerprint.browser import Browser
from model import ChainId
from tools.logger import task_log


def chain_id_to_layerswap_chain_name(chain_id: ChainId):
    match chain_id:
        case ChainId.ETH_ETHEREUM:
            return "ethereum"
        case ChainId.ETH_ZKS_ERA:
            return "zksync era"
        case ChainId.ETH_ZKS_LITE:
            return "zksync lite"
        case ChainId.ETH_OKTC:
            return "okx chain"
        case ChainId.ETH_ARBITRUM:
            return "arbitrum one"
        case ChainId.ETH_OPTIMISM:
            return "optimism"
        case ChainId.ETH_STARK_ARGENTX | ChainId.ETH_STARK_BRAAVOS:
            return "starknet"


class Layerswap:
    def __init__(self, task_id: str, browser: Browser, metamask: MetaMask) -> None:
        self.task_id = task_id
        self.browser = browser
        self.metamask = metamask

    def connect_metamask(self):
        self.browser.initialized_get("https://www.layerswap.io/app/")
        self.browser.click(
            self.browser.find_element_and_wait(
                ".col-start-5.justify-self-end.self-center.flex.items-center.gap-4 > button[type=button]"
            )
        )
        self.browser.wait(1, 3)
        if metamask := self.browser.find_elements_and_wait(
            "button[data-testid=rk-wallet-option-metaMask]"
        ):
            self.browser.click(metamask[0])
            self.metamask.connect()
        else:
            self.browser.click(
                # self.browser.find_element_and_wait("button[aria-label=Close]")
                self.browser.find_element_and_wait(
                    "button.absolute.text-secondary-text.right-4.top-3.p-1.justify-self-start.duartion-100.ring-1.ring-secondary-400.transition.bg-secondary-500.rounded-full.items-center"
                )
            )

    def bridge(self, from_chain: ChainId, to_chain: ChainId, amount: float):
        task_log(
            self.task_id, f"Start to bridge from {from_chain.value} to {to_chain.value}"
        )
        self.browser.get("https://www.layerswap.io/app")
        self.browser.wait(3, 5)
        task_log(self.task_id, f"Select from chain {from_chain.value}")
        from_button_element = self.browser.find_element_and_wait(
            "label[for='from'] + div button"
        )
        self.browser.click(from_button_element)
        self.browser.wait(1, 3)

        layerswap_from_chain = chain_id_to_layerswap_chain_name(from_chain)
        task_log(
            self.task_id,
            f"Input from chain {layerswap_from_chain}",
        )
        self.browser.send_keys(
            self.browser.find_element_and_wait('input[placeholder="Swap from"]'),
            layerswap_from_chain,
        )
        self.browser.wait(1, 3)
        self.browser.click(
            self.browser.find_element_and_wait(
                f'div[data-value="{layerswap_from_chain}"]'
            )
        )

        layerswap_to_chain = chain_id_to_layerswap_chain_name(to_chain)
        self.browser.wait(1, 3)
        task_log(self.task_id, "Select to chain")
        to_button_element = self.browser.find_element_and_wait(
            "label[for='to'] + div button"
        )
        self.browser.click(to_button_element)
        self.browser.wait(1, 3)
        task_log(self.task_id, "Input to chain")
        self.browser.send_keys(
            self.browser.find_element_and_wait('input[placeholder="Swap to"]'),
            layerswap_to_chain,
        )
        self.browser.wait(1, 3)
        self.browser.click(
            self.browser.find_element_and_wait(
                f'div[data-value="{layerswap_to_chain}"]'
            )
        )

        self.browser.wait(1, 3)
        task_log(self.task_id, "Input amount")
        self.browser.send_keys(
            self.browser.find_element_and_wait("input[name=amount]"), str(amount)
        )
        task_log(self.task_id, "Select Address")
        self.browser.click(self.browser.find_element_and_wait("button div.truncate"))
        self.browser.wait(3, 5)
        task_log(self.task_id, "click address avatar")
        self.browser.click(
            self.browser.find_element_and_wait(
                ".flex.text-primary-text.bg-secondary-400.flex-row.items-left.rounded-md.p-2"
            )
        )
        # input_address_elements = self.browser.find_elements_and_wait(
        #     ".text-gray-500", 5
        # )
        # if len(input_address_elements) > 0:  # to check
        #     self.browser.click(input_address_elements[0])
        #     self.browser.wait(3, 5)
        #     input_address_element = self.browser.find_element_and_wait(
        #         "#destination_address", By.CSS_SELECTOR, 5
        #     )
        #     self.browser.send_keys(input_address_element, wallet["address"])
        #     self.browser.wait(1, 3)
        # select_element = self.browser.find_element_and_wait(
        #     ".flex.text-primary-text.flex-row.items-left.px-2.py-1.rounded-md"
        # )
        # self.browser.click(select_element)
        # self.browser.wait(1, 3)

        button_element = self.browser.find_element_and_wait(".grow.text-center")
        for _ in range(2):
            if button_element.text == "Swap now":
                task_log(self.task_id, "Swap now")
                self.browser.click(button_element)
                self.browser.wait(3, 5)
                button_element = self.browser.find_elements_and_wait(
                    ".grow.text-center"
                )[-1]
            if button_element.text == "Send from wallet":
                self.browser.click(button_element)
                # self.browser.wait_tabs(2)
                # self.browser.wait(1, 3)
                # self.browser.switch_to(0)
                # self.browser.wait(1, 3)
                # notice_element = self.browser.find_element_and_wait(
                #     ".text-left.space-y-1"
                # )
                # notice_text = notice_element.text
                # self.browser.switch_to(-1)
                # self.browser.wait(1, 3)
                # if "Network switch" in notice_text:
                #     task_log(self.task_id, "Switch network")
                #     self.metamask.add_and_switch_network()
                #     self.browser.wait(3, 5)
                # task_log(self.task_id, "Send from wallet")
                self.metamask.confirm()
                self.browser.wait(3, 5)
                break
            else:
                task_log(self.task_id, "Can not find button, try again in 10 seconds")
                self.browser.wait(10, 12)
        else:
            task_log(self.task_id, "Failed: Can not find button")
            return False

        task_log(self.task_id, "Wait for swap")
        wait_count = 0
        while wait_count < 10:
            try:
                self.browser.switch_to()
                completed_element = self.browser.find_element_and_wait(
                    ".font-medium.text-primary-text"
                )
                if "completed" in completed_element.text:
                    task_log(self.task_id, "bridge completed")
                    break
                else:
                    raise Exception("bridge failed")
            except:
                task_log(
                    self.task_id, "Can not find swap complated dom,try later again"
                )
                self.browser.wait(5, 10)
                wait_count += 1

        transfer_elements = self.browser.find_elements_and_wait(".text-white.text-lg")
        era_balance = float(transfer_elements[0].text.replace("ETH", "").strip())
        lite_balance = float(transfer_elements[1].text.replace("ETH", "").strip())
        respnse = {
            "from_balance": era_balance,
            "to_balance": lite_balance,
            "fee": era_balance - lite_balance,
        }
        return respnse

    def to_zksync_lite(self, amount: float, wallet: dict) -> dict:
        task_log(self.task_id, "Start era to lite")
        self.browser.get("https://www.layerswap.io/app")
        self.browser.wait(3, 5)
        task_log(self.task_id, "Select from chain")
        from_button_element = self.browser.find_element_and_wait(
            "label[for='from'] + div button"
        )
        self.browser.click(from_button_element)
        self.browser.wait(1, 3)
        task_log(self.task_id, "Input from chain")
        self.browser.send_keys(
            self.browser.find_element_and_wait('input[placeholder="Swap from"]'),
            "zksync era",
        )
        self.browser.wait(1, 3)
        self.browser.click(
            self.browser.find_element_and_wait('div[data-value="zksync era"]')
        )
        self.browser.wait(1, 3)
        task_log(self.task_id, "Select to chain")
        to_button_element = self.browser.find_element_and_wait(
            "label[for='to'] + div button"
        )
        self.browser.click(to_button_element)
        self.browser.wait(1, 3)
        task_log(self.task_id, "Input to chain")
        self.browser.send_keys(
            self.browser.find_element_and_wait('input[placeholder="Swap to"]'),
            "zksync lite",
        )
        self.browser.wait(1, 3)
        self.browser.click(
            self.browser.find_element_and_wait('div[data-value="zksync lite"]')
        )
        self.browser.wait(1, 3)
        task_log(self.task_id, "Input amount")
        self.browser.send_keys(
            self.browser.find_element_and_wait("input[name=amount]"), str(amount)
        )
        task_log(self.task_id, "Select Address")
        self.browser.click(self.browser.find_element_and_wait("button div.truncate"))
        self.browser.wait(3, 5)
        input_address_elements = self.browser.find_elements_and_wait(
            ".text-gray-500", 5
        )
        if len(input_address_elements) > 0:  # to check
            self.browser.click(input_address_elements[0])
            self.browser.wait(3, 5)
            input_address_element = self.browser.find_element_and_wait(
                "#destination_address", 5
            )
            self.browser.send_keys(input_address_element, wallet["address"])
            self.browser.wait(1, 3)
        select_element = self.browser.find_element_and_wait(
            ".flex.text-primary-text.flex-row.items-left.px-2.py-1.rounded-md"
        )
        self.browser.click(select_element)
        self.browser.wait(1, 3)

        while True:
            try:
                button_element = self.browser.find_element_and_wait(".grow.text-center")

                match button_element.text:
                    case "Swap now":
                        task_log(self.task_id, "Swap now")
                        self.browser.click(button_element)
                        self.browser.wait(3, 5)
                    case "Send from wallet":
                        self.browser.click(button_element)
                        self.browser.wait_tabs(2)
                        self.browser.wait(1, 3)
                        self.browser.switch_to(0)
                        self.browser.wait(1, 3)
                        notice_element = self.browser.find_element_and_wait(
                            ".text-left.space-y-1"
                        )
                        notice_text = notice_element.text
                        self.browser.switch_to(-1)
                        self.browser.wait(1, 3)
                        if "Network switch" in notice_text:
                            task_log(self.task_id, "Switch network")
                            self.metamask.add_and_switch_network()
                            self.browser.wait(3, 5)
                        else:
                            task_log(self.task_id, "Send from wallet")
                            self.metamask.confirm()
                            self.browser.wait(3, 5)
                            break
            except:
                task_log(self.task_id, "Can not find button,try later again")
                self.browser.wait(3, 5)
                self.browser.switch_to()

        task_log(self.task_id, "Wait for swap")
        wait_count = 0
        while wait_count < 10:
            try:
                self.browser.switch_to()
                swap_complated_element = self.browser.find_element_and_wait(
                    ".text-lg.font-bold.text-white.leading-6.text-center"
                )
                if not swap_complated_element.text == "Swap completed":
                    raise Exception("Swap failed")
                break
            except:
                task_log(
                    self.task_id, "Can not find swap complated dom,try later again"
                )
                self.browser.wait(5, 10)
                wait_count += 1

        transfer_elements = self.browser.find_elements_and_wait(".text-white.text-lg")
        era_balance = float(transfer_elements[0].text.replace("ETH", "").strip())
        lite_balance = float(transfer_elements[1].text.replace("ETH", "").strip())
        respnse = {
            "era_balance": era_balance,
            "lite_balance": lite_balance,
            "fee": era_balance - lite_balance,
        }
        return respnse
