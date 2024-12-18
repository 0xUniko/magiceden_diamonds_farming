from dataclasses import dataclass
from typing import Optional
import requests
from api import Response, get_response
from api.remote.resource import *
from api import headers
from api.remote import *

exchange_config = resource_config["exchange"]


@dataclass
class WalletAddressDTO:
    id: str
    address: str
    exchange: str
    chain_id: str

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@dataclass
class RechargeDTO:
    address: str
    chain_id: str
    amount: str
    recharge_address: str
    recharge_tx_id: str
    currency: str
    exchange: str

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@dataclass
class WithdrawStatusDTO:
    id: str
    address: str
    amount: str
    chain_id: str
    currency: str
    exchange: str
    status: str
    tx_id: str
    remark: Optional[str] = None

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@dataclass
class WithdrawDTO:
    withdraw_address: str
    exchange: str
    chain_id: str
    amount: str
    currency: str
    fee: str

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@dataclass
class WithdrawResultDTO:
    id: str
    fee: str

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


@dataclass
class BalanceDTO:
    currency: str
    exchange: str = "okx"
    avail_balance: str = "0"
    balance: str = "0"
    frozen_balance: str = "0"

    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def get_one_recharge_address(chain_id: str, currency: str, exchange: str = "okx") -> Response[WalletAddressDTO]:
    response = requests.get(
        f'{host}{exchange_config["get_one_recharge_address"]}',
        params={"exchange": exchange,
                "chain_id": chain_id, "currency": currency},
        headers=headers,
    )
    return get_response(response, WalletAddressDTO)


def recharge_complete(recharge_dto: RechargeDTO) -> Response[None]:
    response = requests.post(
        f'{host}{exchange_config["recharge_complete"]}',
        json=recharge_dto.__dict__,
        headers=headers,
    )
    return get_response(response)


def withdraw(withdraw_dto: WithdrawDTO) -> Response[WithdrawResultDTO]:
    response = requests.post(
        f'{host}{exchange_config["withdraw"]}',
        json=withdraw_dto.__dict__,
        headers=headers,
    )
    return get_response(response, WithdrawResultDTO)


def get_withdraw_by_id(id: str) -> Response[WithdrawStatusDTO]:
    response = requests.get(
        f'{host}{exchange_config["get_withdraw_by_id"]}',
        params={"id": id},
        headers=headers,
    )
    return get_response(response, WithdrawStatusDTO)


def get_balance(currency: str) -> Response[BalanceDTO]:
    response = requests.get(
        f'{host}{exchange_config["get_balance"]}',
        params={"currency": currency},
        headers=headers,
    )
    return get_response(response, BalanceDTO)
