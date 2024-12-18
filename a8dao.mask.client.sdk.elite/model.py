from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional, TypedDict

from fingerprint.browser import Browser
from fingerprint.browser_client import BrowserClient


class BrowserInitType(Enum):
    NONE = 0  # 不需要
    OPEN = 1  # 仅打开，如果不存在就报错
    CREATE_AND_OPEN = 2  # 创建并打开，如果存在就报错
    RECREATE_AND_OPEN = 3  # 重建并打开
    CREATE_OR_OPEN = 4  # 如果存在就打开，不存在就创建并打开


@dataclass
class ScriptExecuteData:
    browser: Browser
    browser_provider: BrowserClient


@dataclass
class Script:
    id: str
    script_download_path: str
    script_store_path: str
    script_content: str
    store_base_path: str


class twitter_data(TypedDict):
    id: int
    resource_label: str  # 标签
    name: str  # 账号
    password: str
    token: str
    email: str
    status_code: int  # 状态code,正常=1,废弃=3
    status_text: str  # 状态code,正常=1,废弃=3
    modify_time: str  # 最后修改时间


class discord_data(TypedDict):
    id: int
    resource_label: str  # 标签
    email: str  # 账号/邮箱
    dc_password: str  # 账号密码
    email_password: str  # 邮箱密码
    token: str
    status_code: int  # 状态code,正常=1,废弃=3
    status_text: str  # 状态code,正常=1,废弃=3
    modify_time: str  # 最后修改时间


class email_data(TypedDict):
    id: int
    resource_label: str  # 标签
    email: str
    password: str
    recovery_email: str
    status_code: int  # 状态code,正常=1,废弃=3
    status_text: str  # 状态code,正常=1,废弃=3
    modify_time: str  # 最后修改时间


class wallet_data(TypedDict):
    id: int
    address: str
    chain_id: str
    metamask_password: str
    mnemonic: str
    private_key: str
    extend_information: dict


class role_label_data(TypedDict):
    id: int
    label: str  # 标签
    modify_time: str


class fingerprint_data(TypedDict):
    id: int
    name: str
    modify_time: str
    extend_information: dict


class role_data(TypedDict):
    role_id: int
    # id:str
    role_label_data: role_label_data
    extend_information: dict
    twitter_data: twitter_data | None
    discord_data: discord_data | None
    email_data: email_data | None
    hd_wallet_id: str
    wallet_data: list[wallet_data]
    fingerprint_data: fingerprint_data


class response_msg(TypedDict):
    code: int
    message: str


class ResourceType(Enum):
    discord = 1
    email = 2
    fingerprint = 3
    twitter = 4
    wallet = 5


class ChainId(Enum):
    ETH_ETHEREUM = "eth-erc20"
    ETH_ZKS_ERA = "eth-zks"
    ETH_ZKS_LITE = "eth-zkslite"
    ETH_OKTC = "eth-oktc"
    ETH_ARBITRUM = "eth-arb"
    ETH_OPTIMISM = "eth-op"
    MATIC_POLYGON = "matic-polygon"
    MATIC_ETHEREUM = "matic-erc20"
    ETH_STARK_ARGENTX = "eth-stark-argentx"
    ETH_STARK_BRAAVOS = "eth-stark-braavos"
    BNB_BSC = "bnb-bsc"
    BNB = "bnb"
    OPBNB = "opbnb"


is_evm_web3 = {
    "eth-erc20": True,
    "eth-zks": True,
    "eth-zkslite": True,
    "eth-oktc": True,
    "eth-arb": True,
    "eth-op": True,
    "matic-polygon": True,
    "matic-erc20": True,
    "eth-stark-argentx": False,
    "eth-stark-braavos": False,
}

chain_name_to_chain_id = {"eth-arb": 42161}
chain_id_to_chain_name = {value: key for key, value in chain_name_to_chain_id.items()}
