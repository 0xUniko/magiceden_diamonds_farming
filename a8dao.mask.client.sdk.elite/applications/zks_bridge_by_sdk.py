from eth_account import Account
from eth_account.signers.local import LocalAccount
from web3 import Web3
from web3.middleware.geth_poa import geth_poa_middleware
from zksync2.core.types import Token
from zksync2.module.module_builder import ZkSyncBuilder
from zksync2.provider.eth_provider import EthereumProvider

from config import config


class ZksBridge:
    def __init__(self, task_id: str, private_key: str) -> None:
        self.task_id = task_id
        self.w3_eth = Web3(Web3.HTTPProvider(config["rpc_endpoint"]["mainnet"]))
        # self.w3_eth = Web3(Web3.HTTPProvider("https://rpc.ankr.com/eth_goerli"))
        self.w3_eth.middleware_onion.inject(geth_poa_middleware, layer=0)
        self.w3_zks = ZkSyncBuilder.build(config["rpc_endpoint"]["zksync_era"])
        # self.w3_zks = ZkSyncBuilder.build("https://zksync2-testnet.zksync.dev")
        self.account: LocalAccount = Account.from_key(private_key)
        self.eth_provider = EthereumProvider(
            self.w3_zks,
            self.w3_eth,
            self.account,
        )

    def deposit(self, amount: float):
        return self.eth_provider.deposit(
            Token.create_eth(),
            self.w3_eth.to_wei(amount, "ether"),
            self.account.address,
            # gas_price=30,
            # gas_limit=149210,
        )
