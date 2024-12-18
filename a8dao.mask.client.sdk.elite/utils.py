import json
from typing import TypedDict
from datetime import datetime,timedelta
import httpx
from solana.rpc.api import Client
from solana.rpc.types import TokenAccountOpts
from solders.pubkey import Pubkey

from api import headers

web3_api_base_url = "http://127.0.0.1:8000"
solana_rpc = "https://rpc.ankr.com/solana/3486bba53323e16d8e12c5a3fffd2358fd7609399ef9f09113ef69ab45a11149"

def get_pub_key_from_mnemonic(mnemonic: str):
    retry_count = 0
    while True:
        res = httpx.get(
            url=web3_api_base_url + "/solana/get_pub_key_from_mnemonic",
            params={"mnemonic": mnemonic},
            headers=headers,
        )
        if res.status_code != 200 or res.json()["code"] != 0:
            if retry_count < 3:
                continue
            # return {"code": 1, "message": str(res)}
            raise Exception(str(res))
        else:
            return res.json()


def get_balance(pubkey: str):
    retry_count = 0
    while True:
        res = httpx.get(
            url=web3_api_base_url + "/solana/get_balance",
            params={"pubkey": pubkey},
            headers=headers,
        )
        if res.status_code != 200 or res.json()["code"] != 0:
            if retry_count < 3:
                continue
            # return {"code": 1, "message": str(res)}
            raise Exception(str(res))
        else:
            return res.json()


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
    role_label_data: role_label_data
    extend_information: dict
    twitter_data: twitter_data | None
    discord_data: discord_data | None
    email_data: email_data | None
    hd_wallet_id: str
    wallet_data: list[wallet_data]
    fingerprint_data: fingerprint_data


def get_wallet_by_id(id: int):
    return httpx.get(
        "http://api.fanershe.cn/wallet-api/wallet/get_by_id",
        params={"id": id},
        headers=headers,
    ).json()


def get_wallet_data_list_by_network(
    wallet_address_data_list: list[dict],
) -> list[wallet_data]:
    wallet_data_list: list[wallet_data] = []
    for wallet_address_data in wallet_address_data_list:
        response = get_wallet_by_id(wallet_address_data["id"])
        assert (
            response["code"] == 0
        ), f'Can not get the wallet data by id {wallet_address_data["id"]}: {response["message"]}'

        wallet = wallet_data(
            id=response["data"]["id"],
            address=response["data"]["address"],
            chain_id=response["data"]["chain_id"],
            metamask_password=response["data"]["metamask_password"],
            mnemonic=response["data"]["mnemonic"],
            private_key=response["data"]["private_key"],
            extend_information=json.loads(wallet_address_data["extend_information"]),
        )
        wallet_data_list.append(wallet)
    return wallet_data_list


# def get_role_by_id(role_id: int) -> role_data:
#     res = httpx.get(
#         "http://api.fanershe.cn/rpg-api/role/" + "get_role_by_id",
#         params={"id": role_id},
#         headers={"user_flow_token": user_flow_token},
#     ).json()
#     assert res["code"] == 0, f"failed to get role: {res['message']}"
#     role = res["data"]
#     role["wallet_data"] = get_wallet_data_list_by_network(
#         res["data"]["wallet_data"]["wallet_address_data"]
#     )
#     return role


# def get_sol_balance_by_role_id(role_id: int) -> float:
#     role = get_role_by_id(role_id)
#     mnemonic = role["wallet_data"][0]["mnemonic"]
#     pubkey = get_pub_key_from_mnemonic(mnemonic)["data"]
#     return get_balance(pubkey)["data"] / 10e8


magiceden_v2_authority = Pubkey.from_string(
    "1BWutmTvYPwDtmw9abTkS4Ssr8no61spGAvW1X6NDix"
)

client = Client(solana_rpc)


def is_listing(mint_address: str):
    res = client.get_token_accounts_by_owner_json_parsed(
        magiceden_v2_authority, TokenAccountOpts(mint=Pubkey.from_string(mint_address))
    )
    return len(json.loads(res.to_json())["result"]["value"]) > 0


def get_token_owner(mint_address: str) -> str:
    res = client.get_token_largest_accounts(Pubkey.from_string(mint_address))
    res = client.get_account_info_json_parsed(
        Pubkey.from_string(json.loads(res.to_json())["result"]["value"][0]["address"])
    )
    return json.loads(res.to_json())["result"]["value"]["data"]["parsed"]["info"][
        "owner"
    ]


if __name__ == "__main__":
    from magiceden_client import MagicEdenApiClient

    nft_list = [
        {
            "mint_address": "3P8zD1aFTW6SpvWNdvLtNVF3zZvEX8U6PdWNetzSWWLJ",
            "name": "SMB #1523",
        },
        {
            "mint_address": "73dtmD3t9j1tQHPNK4bzbqWXmiavsQvvUzkgRhwYcP5L",
            "name": "SMB #467",
        },
    ]
    role_list = [
        {"role_id": 1, "pubkey": "8LndM3VYt9nMGyHNNbmMzMYdwkAzZZnhFJZkRCEUoFHC"},
        # {"role_id": 2, "pubkey": "BKHMtDqGq9uu91iGJ7w4zvArA6u7Pa6ZhuVWGAvYKvJc"},
        # {"role_id": 3, "pubkey": "DQLsjx18AzSoQCThhL8fpK2Eu34PGBayuf5SAhQ7rLuf"},
        # {"role_id": 4, "pubkey": "DTY8UhBgqKB9YmAVFRpbh1qsMrhUCXHFqcfUckK1UeAc"},
        # {"role_id": 5, "pubkey": "5m8fUo8yQtEpt5uWYdeBSRvwo9shcS8dFey96aARvc33"},
        # {"role_id": 6, "pubkey": "2Aw8FYSgqGKzo4zwU3eYcHnxVhk7Pp9azWy3gJVXjeFn"},
        # {"role_id": 7, "pubkey": "97Kx9nk3oEZ2EG2sPDNJSfAtB6XJwXSAqYpdBhHiQo48"},
        # {"role_id": 8, "pubkey": "6fD49FzoANDpEqDVEbRqNRAkwyZ4XJhs4hQXXyDanCpq"},
        # {"role_id": 9, "pubkey": "HTE1VsNVRJMKcGb8r4a2uji1KB1VGrHg8vXPNUSgnpgW"},
        # {"role_id": 10, "pubkey": "6EqR3QqnGtnZvR6CGuTTTBtdfxTic1d2bSZbkR7LyhHE"},
        # {"role_id": 11, "pubkey": "BCGrkNnjkP26zFmTDzXf9wH5UxdsGurDgCeMvhthbeyV"},
        # {"role_id": 12, "pubkey": "t4ECPhraV8VKRQTJibgnmzBarTJWJ5haxaffufi9gkk"},
        # {"role_id": 13, "pubkey": "2eZ4r1AGnUgoU3FwLZQfF424MB7YiuvPVZ2gKitZWHeq"},
        # {"role_id": 14, "pubkey": "6oLQptNB1ZXpS3h7j3tKLJvmMrMxFy596o5FmZWqW8bY"},
        # {"role_id": 15, "pubkey": "6JXxp43uUuxiCoqV2jfu9195Bj9o3xVpDVpt9eQXMSzm"},
    ]
    # for role in role_list:
    #     print(role['role_id'])
    #     res = create_flow(
    #         CreateFlowRequest(
    #             flow_name="okx_web3_initialization",
    #             flow_description="",
    #             script_id="155",
    #             role_id_list=['3110'],
    #             plan_start_time=datetime.now(),
    #             plan_end_time=(datetime.now() + timedelta(days=1)),
    #             run_amount="1",
    #             plan_complate_count=str(len(role_list)),
    #             use_aliyun_count="1",
    #             user_parameter=json.dumps({"role_id":role['role_id']}),
    #             task_type_code=TaskTypeCode.UI,
    #         )
    #     )
    #     assert res["code"] == 0, f"failed to create flow: {res['message']}"

    # for nft in nft_list:
    #     print(f'nft: {nft}')
    #     for role in role_list:
    #         print(role['role_id'])
    #         res = create_flow(
    #             CreateFlowRequest(
    #                 flow_name="magic_eden_buy",
    #                 flow_description="",
    #                 script_id="204",
    #                 role_id_list=['3110'],
    #                 plan_start_time=datetime.now(),
    #                 plan_end_time=(datetime.now() + timedelta(days=1)),
    #                 run_amount="1",
    #                 plan_complate_count=str(len(role_list)),
    #                 use_aliyun_count="1",
    #                 user_parameter=json.dumps({"role_id":role['role_id'],
    #                                         "mint_address": nft["mint_address"],
    #                                         "magiceden_token_name": nft["name"],}),
    #                 task_type_code=TaskTypeCode.UI,
    #             )
    #         )
    #         assert res["code"] == 0, f"failed to create flow: {res['message']}"

    # for nft in nft_list:
    #     print(f"nft: {nft}")
    #     nft_is_listing = is_listing(nft["mint_address"])
    #     if nft_is_listing:
    #         listing_info = MagicEdenApiClient().get_listings_for_token(
    #             nft["mint_address"]
    #         )[0]
    #         owner = listing_info.seller
    #     else:
    #         owner = get_token_owner(nft["mint_address"])
    #     print(
    #         f"is_listing: {nft_is_listing}, owner: {owner}, price: {listing_info.price if nft_is_listing else None}"
    #     )
        # for role in role_list:
        #     balance = get_balance(role["pubkey"])["data"] / 1e9
        #     print(f"role_id: {role['role_id']}, balance: {balance}")
