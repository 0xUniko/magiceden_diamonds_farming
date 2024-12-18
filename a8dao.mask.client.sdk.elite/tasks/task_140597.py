import random
import traceback

from config import config
from extensions.okx_web3 import OkxWeb3
from model import ChainId, role_data
from script_base import *
from tools.logger import task_log


def run(task_id: str, role: role_data, user_parameter: dict) -> response_msg:
    # print(role)
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
    try:
        okxweb3: OkxWeb3 = load_extensions(
            task_id, role, script_execute_data, OkxWeb3
        )  # type: ignore

        return response
    except Exception as e:
        print(traceback.format_exc())
        return {"code": 3, "message": str(e)}
    finally:
        script_execute_data.browser_provider.stop(role["fingerprint_data"]["name"])
