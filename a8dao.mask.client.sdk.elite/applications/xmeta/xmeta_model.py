from enum import Enum
from typing import List, TypedDict
from model import ChainId


"""
账户类型
"""


class AccountType(Enum):
    CAPITAL = "capital"
    TRADING = "trading"


"""
Gas类型
"""


class GasType(Enum):
    CEX_TO_CAPITAL = "cex_to_capital"
    CAPITAL_TO_CEX = "capital_to_cex"
    CAPITAL_TO_TRADING = "capital_to_trading"
    TRADING_TO_CAPITAL = "trading_to_capital"
    LISTING_DELEGATE = "list_delegate"
    APPROVE = "approve"
    PLACE_ORDER = "place_order"
    TRANSFER_TO_OWNER = "transfer_to_owner"


"""
Nft外部采购单
"""


class NftExternalPurchaseOrder(TypedDict):
    contract_address: str
    collection_id: int
    product_id: int
    token_id: int
    price: float
    seller_address: str
    trading_account_role_id: str
    liquidity_seller_id: int
    purchase_address: str
    created_time: int


"""
Nft销售单
"""


class NftSaleOrder(TypedDict):
    contract_address: str
    collection_id: int
    product_id: int
    token_id: int
    price: float
    address: str
    has_permission: bool
    has_deposit: int
    liquidity_user_id: int
    trading_account_role_id: str
    created_time: int


"""
Gas消耗记录
"""


class Gas(TypedDict):
    chain_id: ChainId
    gas_type: GasType
    gas: int
    from_address: str
    to_address: str
    value: int
    tx_hash: str
    group_name: str
    created_time: int


"""
交易账户合约许可
"""


class TradingAccountContractPermission(TypedDict):
    contract_address: str
    address: str
    is_approved: bool
    is_delegated: bool


"""
分组
"""


class Group(TypedDict):
    name: str
    contract_address: str
    created_time: int
    is_active: bool
    loop_limit: int
    group_liquidity_user_limit: int
    cex_withdraw_amount_range: List[float]


"""
分组流动性用户
"""


class GroupLiquidityUser(TypedDict):
    contract_address: str
    group_name: str
    liquidity_user_id: int


"""
流动性用户
"""


class LiquidityUser(TypedDict):
    captial_role_id: int
    trading_role_id: int
    round: int


"""
账户
"""


class Account(TypedDict):
    role_id: int
    address: str
    account_type: AccountType


"""
集合
"""


class Collection(TypedDict):
    collection_id: int
    total: int
    name: str
    contract_address: str


"""
NFT资产
"""


class NftAsset(TypedDict):
    product_id: int
    collection_id: int
    token_id: int
    name: str


"""
NFT网站价格
"""


class NftWebPrice(TypedDict):
    id: int
    floor_price: str
    trade_price: str
    trade_time: int
    net_image_url: str
    series_id: int
    token_id: int
    name: str


"""
NFT网站挂单
"""


class NftWebSellOrder(TypedDict):
    id: int
    product_id: int
    price: float
    address: str
