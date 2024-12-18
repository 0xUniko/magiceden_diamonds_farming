import traceback
from typing import TypedDict

from api.local.web3.solana import get_pub_key_from_mnemonic
from applications.magiceden import MagicEden
from extensions.okx_web3 import OkxWeb3
from model import ChainId, role_data
from script_base import *
from tools.logger import task_log

# script_id: 205


def run(task_id: str, role: role_data, user_parameter) -> response_msg:
    task_log(task_id, role["fingerprint_data"]["name"])
    response: response_msg = {"code": 0, "message": "ok"}
    browser_init_type = BrowserInitType.CREATE_OR_OPEN
    if "browser_init_type" in user_parameter:
        browser_init_type = BrowserInitType(user_parameter["browser_init_type"])

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
        magiceden.get_reward_data(
            int(role["id"] if "id" in role else role["role_id"]), pubkey_res["data"]
        )

        return response
    except Exception as e:
        print(traceback.format_exc())
        return {"code": 3, "message": str(e)}
    finally:
        script_execute_data.browser_provider.stop(role["fingerprint_data"]["name"])
