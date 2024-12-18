from typing import TypedDict
import requests
from api import Response, get_response
from api.remote.resource import *
from api import headers
from api.remote import *

broker_config = resource_config["broker"]


class GetOneRechargeAddressResponse(TypedDict):
    id: int
    address: str
    exchange: str
    chain_id: str
    recharge_count: int


def get_one_recharge_address(
    chain_id: str, currency: str, role_label_id: str, exchange: str
) -> Response[GetOneRechargeAddressResponse]:
    response = requests.get(
        f'{host}{broker_config["get_one_recharge_address"]}',
        params={
            "exchange": exchange,
            "chain_id": chain_id,
            "role_label_id": role_label_id,
            "currency": currency,
        },
        headers=headers,
    )
    return get_response(response, GetOneRechargeAddressResponse)


class RechargeComplateRequest(TypedDict):
    address: str
    chain_id: str
    amount: float
    recharge_address: str
    recharge_tx_id: str
    currency: str
    role_label_id: int


def recharge_complete(
    recharge_complate_request: RechargeComplateRequest,
) -> Response[None]:
    response = requests.post(
        f'{host}{broker_config["recharge_complete"]}',
        json=recharge_complate_request,
        headers=headers,
    )
    return get_response(response)


class WithDrawRequest(TypedDict):
    withdraw_address: str
    chain_id: str
    amount: str
    currency: str
    role_label_id: int
    exchange: str


class WithDrawResponse(TypedDict):
    id: str
    fee: float


def withdraw(request_data: WithDrawRequest) -> Response[WithDrawResponse]:
    response = requests.post(
        f'{host}{broker_config["withdraw"]}',
        json=request_data,
        headers=headers,
    )
    return get_response(response, WithDrawResponse)


class ExchangeWithdrawResponse(TypedDict):
    status: int
    remark: str
    address: str
    exchange: str
    chain_id: str
    amount: float
    currency: str
    tx_id: str


def get_withdraw_by_id(id: str) -> Response[ExchangeWithdrawResponse]:
    response = requests.get(
        f'{host}{broker_config["get_withdraw_by_id"]}',
        params={"id": id},
        headers=headers,
    )
    return get_response(response, ExchangeWithdrawResponse)


class ExchangeBalanceResponse(TypedDict):
    currency: str
    exchange: str
    balance: float
    frozen_balance: float
    avail_balance: float


def get_balance(
    currency: str, role_label_id: int, exchange: str
) -> Response[ExchangeBalanceResponse]:
    response = requests.get(
        f'{host}{broker_config["get_balance"]}',
        params={
            "currency": currency,
            "role_label_id": role_label_id,
            "exchange": exchange,
        },
        headers=headers,
    )
    return get_response(response, ExchangeBalanceResponse)
