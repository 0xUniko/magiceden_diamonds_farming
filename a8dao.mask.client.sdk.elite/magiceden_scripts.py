import logging
import traceback
from typing import TypedDict

import httpx

from api.local.web3.solana import get_pub_key_from_mnemonic
from applications.magiceden import MagicEden
from extensions.okx_web3 import OkxWeb3
from model import ChainId, role_data
from script_base import *
from tools.logger import task_log

logger = logging.getLogger(__name__)
response: response_msg = {"code": 0, "message": "ok"}
browser_init_type = BrowserInitType.CREATE_OR_OPEN
task_id = "111"


def magiceden_buy(role_id: int, mint_address: str, magiceden_token_name: str):
    logging.info(
        f"buy mint_address: {mint_address}, magiceden token name: {magiceden_token_name}",
    )

    role = httpx.get(
        "http://127.0.0.1:8452/get_role",
        params={"role_id": role_id},
    ).json()

    get_browser_result = init_browser(
        task_id,
        role["fingerprint_data"]["name"],
        "id",
        "https://www.google.com",
        browser_init_type,
    )

    if get_browser_result[0]["code"] != 0:
        return get_browser_result[0]

    script_execute_data = get_browser_result[1]

    assert script_execute_data is not None

    wallet = [
        w for w in role["wallet_data"] if w["chain_id"] == ChainId.ETH_ETHEREUM.value
    ][0]

    pubkey_res = get_pub_key_from_mnemonic(wallet["mnemonic"])

    assert pubkey_res["code"] == 0, f'get pubkey failed: {pubkey_res["message"]}'

    try:
        okxweb3: OkxWeb3 = load_extensions(task_id, role, script_execute_data, OkxWeb3)  # type: ignore

        browser = script_execute_data.browser

        magiceden = MagicEden(task_id, browser, okxweb3)

        magiceden.auth()

        magiceden.buy(
            mint_address,
            magiceden_token_name,
            pubkey_res["data"],
        )

        # magiceden.get_reward_data(

        #     int(role["id"] if "id" in role else role["role_id"]), pubkey_res["data"]

        # )

        return response

    except Exception as e:
        print(traceback.format_exc())

        return {"code": 3, "message": str(e)}

    finally:
        script_execute_data.browser_provider.stop(role["fingerprint_data"]["name"])


def magiceden_list(
    role_id: int,
    mint_address: str,
    magiceden_token_name: str,
    price: float,
):
    logging.info(
        f"list mint_address: {mint_address}, magiceden token name: {magiceden_token_name}, for price: {price} sol",
    )
    role = httpx.get(
        "http://127.0.0.1:8452/get_role",
        params={"role_id": role_id},
    ).json()

    get_browser_result = init_browser(
        task_id,
        role["fingerprint_data"]["name"],
        "id",
        "https://www.google.com",
        browser_init_type,
    )

    if get_browser_result[0]["code"] != 0:
        # return get_browser_result[0]
        return {"code": 3, "message": "get browser failed"}

    script_execute_data = get_browser_result[1]

    assert script_execute_data is not None

    wallet = [
        w for w in role["wallet_data"] if w["chain_id"] == ChainId.ETH_ETHEREUM.value
    ][0]

    pubkey_res = get_pub_key_from_mnemonic(wallet["mnemonic"])

    assert pubkey_res["code"] == 0, f'get pubkey failed: {pubkey_res["message"]}'

    try:
        okxweb3: OkxWeb3 = load_extensions(task_id, role, script_execute_data, OkxWeb3)  # type: ignore

        browser = script_execute_data.browser

        magiceden = MagicEden(task_id, browser, okxweb3)

        magiceden.auth()

        magiceden.list(
            mint_address,
            magiceden_token_name,
            price,
            pubkey_res["data"],
        )

        return response

    except Exception as e:
        print(traceback.format_exc())

        return {"code": 3, "message": str(e)}

    finally:
        script_execute_data.browser_provider.stop(role["fingerprint_data"]["name"])
