import json
from typing import List, Literal, Optional, Tuple, Type, TypeAlias, TypedDict

import api.local.wallet
import api.network.wallet
import api.remote.rpg.role
from config import config
from extensions.extension import Extension
from fingerprint.default_client import DefaultClient
from ads_client import AdsClient
from model import (
    BrowserInitType,
    ChainId,
    ScriptExecuteData,
    response_msg,
    role_data,
    wallet_data,
)


class ok_res(TypedDict):
    code: Literal[0]
    message: Literal["ok"]


browser_res: TypeAlias = Tuple[response_msg, None] | Tuple[ok_res, ScriptExecuteData]


def init_browser(
    task_id: str,
    fingerprint_name: str,
    country: str,
    check_url: Optional[str],
    browser_init_type: BrowserInitType,
    is_proxy: bool = True,
    proxy_provider_name: str = "Local",
) -> browser_res:
    assert browser_init_type == BrowserInitType.CREATE_OR_OPEN
    response = get_browser(
        task_id,
        fingerprint_name,
        country,
        check_url,
        is_proxy,
        proxy_provider_name,
    )
    if response[0]["code"] == 4:
        return create_and_get_browser(
            task_id,
            fingerprint_name,
            country,
            check_url,
            False,
            is_proxy,
            proxy_provider_name,
        )
    else:
        return response


def create_and_get_browser(
    task_id: str,
    fingerprint_name: str,
    country: str,
    check_url: Optional[str],
    is_clean_create: bool = True,
    is_proxy: bool = True,
    proxy_provider_name: str = "Local",
) -> browser_res:
    # browser_provider = BrowserClientFactory.get_browser_client(config, task_id)
    browser_provider = DefaultClient(task_id)
    browser_provider.update_proxy(proxy_provider_name)
    try:
        if not browser_provider.exists(fingerprint_name):
            user_proxy = None
            browser = browser_provider.create_and_start(fingerprint_name, user_proxy)
            if browser is None:
                browser_provider.stop(fingerprint_name)
                return {"code": 3, "message": "browser start failed"}, None
            else:
                script_execute_data = ScriptExecuteData(browser, browser_provider)
                script_execute_data.browser.wait(5, 10)
                script_execute_data.browser.clean_tabs_last()
                script_execute_data.browser.switch_to(0)
                return ({"code": 0, "message": "ok"}, script_execute_data)
        else:
            return {"code": 4, "message": "browser exists"}, None
    except Exception as e:
        return {"code": 5, "message": str(e)}, None


def get_browser(
    task_id: str,
    fingerprint_name: str,
    country: str,
    check_url: Optional[str],
    is_proxy: bool = True,
    proxy_provider_name: str = "Local",
) -> browser_res:
    # browser_provider = BrowserClientFactory.get_browser_client(config, task_id)
    browser_provider = DefaultClient(task_id)
    browser_provider.update_proxy(proxy_provider_name)
    try:
        if browser_provider.exists(fingerprint_name):
            user_proxy = None
            browser = browser_provider.start(fingerprint_name, user_proxy)
            if browser is None:
                browser_provider.stop(fingerprint_name)
                return {"code": 3, "message": "browser start failed"}, None
            else:
                script_execute_data = ScriptExecuteData(browser, browser_provider)
                script_execute_data.browser.wait(5, 10)
                script_execute_data.browser.clean_tabs_last()
                script_execute_data.browser.switch_to(0)
                return ({"code": 0, "message": "ok"}, script_execute_data)
        else:
            return {"code": 4, "message": "browser not exists"}, None
    except Exception as e:
        return {"code": 5, "message": str(e)}, None


def load_extensions(
    task_id: str,
    role: role_data,
    script_execute_data: ScriptExecuteData,
    extension_type: Type[Extension],
) -> Extension:
    extension = extension_type(script_execute_data.browser, task_id, None)
    extension.load(role)
    return extension


def get_role_by_id(role_id: int) -> role_data:
    role = api.remote.rpg.role.get_role_by_id(str(role_id))["data"]
    if role["fingerprint_data"]["extend_information"] == "":
        role["fingerprint_data"]["extend_information"] = {}
    else:
        role["fingerprint_data"]["extend_information"] = json.loads(
            role["fingerprint_data"]["extend_information"]
        )

    if role["extend_information"] == "" or role["extend_information"] is None:
        role["extend_information"] = {}
    else:
        try:
            role["extend_information"] = json.loads(role["extend_information"])
        except:
            role["extend_information"] = role["extend_information"]
    if config["client"]["wallet_provider"] == "local":
        role["wallet_data"] = get_wallet_data_list_by_role_id(role_id)
    else:
        role["wallet_data"] = get_wallet_data_list(
            role["wallet_data"]["wallet_address_data"]
        )
    return role


def get_wallet_data_list_by_role_id(role_id: int):
    response = api.local.wallet.get_by_role_id(role_id)
    assert (
        response["code"] == 0
    ), f'Can not get the wallet data by id {role_id}: {response["message"]}'
    return response["data"]


def get_wallet_by_role_data(
    chain_id: ChainId, role: role_data
) -> Optional[wallet_data]:
    return next(
        (w for w in role["wallet_data"] if w["chain_id"] == chain_id.value), None
    )


def get_wallet(chain_id: ChainId, role_id: int) -> Optional[wallet_data]:
    role = get_role_by_id(role_id)
    return next(
        (w for w in role["wallet_data"] if w["chain_id"] == chain_id.value), None
    )


def get_wallet_data_list_by_local(
    wallet_address_data_list: List[dict],
) -> List[wallet_data]:
    wallet_data_list: List[wallet_data] = []
    for wallet_address_data in wallet_address_data_list:
        response = api.local.wallet.get_by_id(wallet_address_data["id"])
        assert (
            response["code"] == 0
        ), f'Can not get the wallet data by id {wallet_address_data["id"]}'

        wallet = wallet_data()
        wallet["id"] = wallet_address_data["id"]
        wallet["address"] = response["data"]["address"]
        wallet["chain_id"] = response["data"]["chain_id"]
        wallet["metamask_password"] = response["data"]["password"]
        wallet["mnemonic"] = response["data"]["mnemonic"]
        wallet["private_key"] = response["data"]["private_key"]
        wallet["extend_information"] = response["data"]["extend_information"]
        wallet_data_list.append(wallet)
    return wallet_data_list


def get_wallet_data_list_by_network(
    wallet_address_data_list: List[dict],
) -> List[wallet_data]:
    wallet_data_list: List[wallet_data] = []
    for wallet_address_data in wallet_address_data_list:
        response = api.network.wallet.get_by_id(wallet_address_data["id"])
        assert (
            response["code"] == 0
        ), f'Can not get the wallet data by id {wallet_address_data["id"]}'

        wallet = wallet_data()
        wallet["id"] = wallet_address_data["id"]
        wallet["address"] = wallet_address_data["address"]
        wallet["chain_id"] = wallet_address_data["chain_id"]
        wallet["metamask_password"] = response["data"]["metamask_password"]
        wallet["mnemonic"] = response["data"]["mnemonic"]
        wallet["private_key"] = response["data"]["private_key"]
        wallet["extend_information"] = json.loads(
            wallet_address_data["extend_information"]
        )
        wallet_data_list.append(wallet)
    return wallet_data_list


def get_wallet_data_list(wallet_address_data_list: List[dict]) -> List[wallet_data]:
    if config["client"]["wallet_provider"] == "local":
        return get_wallet_data_list_by_local(wallet_address_data_list)
    else:
        return get_wallet_data_list_by_network(wallet_address_data_list)


def assert_user_parameter(key_list: list, user_parameter: TypedDict) -> None:
    for key in key_list:
        assert key in user_parameter, f"{key} is required."
