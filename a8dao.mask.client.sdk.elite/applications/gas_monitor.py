import requests
from web3 import Web3

from config import config


class GasMonitor:
    def __init__(self):
        self.w3_list: dict[str, Web3] = {}
        for endpoint in config["rpc_endpoint"]:
            self.w3_list[endpoint] = Web3(
                Web3.HTTPProvider(config["rpc_endpoint"][endpoint])
            )

    def get_gas_price(self, chain_name: str):
        return self.w3_list[chain_name].eth.gas_price

    def get_max_priority_fee(self, chain_name: str):
        return self.w3_list[chain_name].eth.max_priority_fee
