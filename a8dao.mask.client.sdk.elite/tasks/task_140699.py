import traceback
from typing import TypedDict

from api.local.web3.solana import get_pub_key_from_mnemonic
from applications.magiceden import MagicEden
from extensions.okx_web3 import OkxWeb3
from model import ChainId, role_data
from script_base import *
from tools.logger import task_log


class UserParameter(TypedDict):
    mint_address: str

    magiceden_token_name: str

    price: float


def run(task_id: str, role: role_data, user_parameter: UserParameter) -> response_msg:
    assert user_parameter != {}, "user_parameter must be provided"

    task_log(
        task_id,
        f"list mint_address: {user_parameter['mint_address']}, magiceden token name: {user_parameter['magiceden_token_name']}, for price: {user_parameter['price']} sol",
    )

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
            user_parameter["mint_address"],
            user_parameter["magiceden_token_name"],
            user_parameter["price"],
            pubkey_res["data"],
        )

        return response

    except Exception as e:
        print(traceback.format_exc())

        return {"code": 3, "message": str(e)}

    finally:
        script_execute_data.browser_provider.stop(role["fingerprint_data"]["name"])
