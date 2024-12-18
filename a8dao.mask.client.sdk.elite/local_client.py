import json
import logging
import random
import sys
import time
from datetime import datetime, timedelta
from typing import TypedDict

from magiceden_client import MagicEdenApiClient
from magiceden_scripts import magiceden_buy,magiceden_list
from utils import (
    # get_role_by_id,
    get_balance,
    get_token_owner,
    is_listing,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(module)s] %(levelname)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("magiceden/logs.txt"),
    ],
)


class Nft(TypedDict):
    mint_address: str
    name: str


client_amount = 1
nft_collection_name = "solana_monkey_business"
nft_list = [
    {
        "mint_address": "C9FRig43fCHrp7ktUzWp1tPyBURQrCVp52KL5D6WANaW",
        "name": "SMB #1594",
    },
    {
        "mint_address": "3F4bfZqo1jzWYiu6SxNbukjyGmjSqQ3Qi923zFt1U4sS",
        "name": "SMB #880",
    },
]
# client_amount=len(nft_list)
# role_id_list = [3110, 3109, 3108, 3107, 3106, 3105, 3104, 3103, 3102, 3101, 3100]
# role_list = [
#     {
#         "role_id": role_id,
#         "pubkey": get_pub_key_from_mnemonic(
#             get_role_by_id(role_id)["wallet_data"][0]["mnemonic"]
#         )["data"],
#     }
#     for role_id in role_id_list
# ]
role_list = [
    # {"role_id": 1, "pubkey": "8LndM3VYt9nMGyHNNbmMzMYdwkAzZZnhFJZkRCEUoFHC"},
    # {"role_id": 2, "pubkey": "BKHMtDqGq9uu91iGJ7w4zvArA6u7Pa6ZhuVWGAvYKvJc"},
    # {"role_id": 3, "pubkey": "DQLsjx18AzSoQCThhL8fpK2Eu34PGBayuf5SAhQ7rLuf"},
    {"role_id": 4, "pubkey": "DTY8UhBgqKB9YmAVFRpbh1qsMrhUCXHFqcfUckK1UeAc"},
    {"role_id": 5, "pubkey": "5m8fUo8yQtEpt5uWYdeBSRvwo9shcS8dFey96aARvc33"},
    {"role_id": 6, "pubkey": "2Aw8FYSgqGKzo4zwU3eYcHnxVhk7Pp9azWy3gJVXjeFn"},
    # {"role_id": 7, "pubkey": "97Kx9nk3oEZ2EG2sPDNJSfAtB6XJwXSAqYpdBhHiQo48"},
    {"role_id": 8, "pubkey": "6fD49FzoANDpEqDVEbRqNRAkwyZ4XJhs4hQXXyDanCpq"},
    # {"role_id": 9, "pubkey": "HTE1VsNVRJMKcGb8r4a2uji1KB1VGrHg8vXPNUSgnpgW"},
    # {"role_id": 10, "pubkey": "6EqR3QqnGtnZvR6CGuTTTBtdfxTic1d2bSZbkR7LyhHE"},
    # {"role_id": 11, "pubkey": "BCGrkNnjkP26zFmTDzXf9wH5UxdsGurDgCeMvhthbeyV"},
    # {"role_id": 12, "pubkey": "t4ECPhraV8VKRQTJibgnmzBarTJWJ5haxaffufi9gkk"},
    # {"role_id": 13, "pubkey": "2eZ4r1AGnUgoU3FwLZQfF424MB7YiuvPVZ2gKitZWHeq"},
    # {"role_id": 14, "pubkey": "6oLQptNB1ZXpS3h7j3tKLJvmMrMxFy596o5FmZWqW8bY"},
    # {"role_id": 15, "pubkey": "6JXxp43uUuxiCoqV2jfu9195Bj9o3xVpDVpt9eQXMSzm"},
]
get_reward_data_time_list = []


class Flow(TypedDict):
    flow_id: int
    nft_mint_address: str
    role_id: int


flow_list: list[Flow] = []

# TODO: WARNING:get_flow_list is not stable! It will not fetch all flows!!!
assert client_amount <= 10

if __name__ == "__main__":
    # flow_list_res = get_flow_list()
    # assert (
    #     flow_list_res["code"] == 0
    # ), f'failed to get flow list: {flow_list_res["message"]}'
    # assert (
    #     flow_list_res["data"]["data"][0]["status_code"] != 1
    # ), "task list is not empty"

    get_reward_data_time_list = [
        t for t in get_reward_data_time_list if t > datetime.now()
    ]
    while True:
        if [t for t in get_reward_data_time_list if t <= datetime.now()]:
            logging.info("create get_reward_data flow")
            raise Exception("get_reward_data flow is not here")
            # for role in role_list:
            #     res = create_flow(
            #         CreateFlowRequest(
            #             flow_name="magiceden_get_reward_data",
            #             flow_description="",
            #             script_id="205",
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
            #     logging.info("create flow succeeded")
            # get_reward_data_time_list = [
            #     t for t in get_reward_data_time_list if t > datetime.now()
            # ]
        else:
            try:
                flow_list_res = get_flow_list()
                assert (
                    flow_list_res["code"] == 0
                ), f'failed to get flow list: {flow_list_res["message"]}'
                flow_list = [
                    flow
                    for flow in flow_list
                    if flow["flow_id"]
                    in [
                        flow_["id"]
                        for flow_ in flow_list_res["data"]["data"]  # type: ignore
                        if flow_["status_code"] == 1
                    ]
                ]
                logging.info(f"current flow list: {flow_list}")
                if len(flow_list) >= client_amount:
                    logging.info("all flows are running")
                else:
                    available_nft_list = [
                        nft
                        for nft in nft_list
                        if nft["mint_address"]
                        not in [flow["nft_mint_address"] for flow in flow_list]
                    ]
                    nft = random.choice(available_nft_list)
                    if is_listing(nft["mint_address"]):
                        listing_info = MagicEdenApiClient().get_listings_for_token(
                            nft["mint_address"]
                        )[0]
                        logging.info(f"nft: {nft} is listing: {listing_info}")
                        if not [
                            role["role_id"]
                            for role in role_list
                            if role["pubkey"] == listing_info.seller
                        ]:
                            logging.error(
                                f"the owner of the listing nft: {nft} is {listing_info.seller} which does not belong to us"
                            )
                            nft_list = [
                                nft_
                                for nft_ in nft_list
                                if nft_["mint_address"] != nft["mint_address"]
                            ]
                        else:
                            available_role_id_list = [
                                role["role_id"]
                                for role in role_list
                                if role["pubkey"] != listing_info.seller
                                and get_balance(role["pubkey"])["data"] / 10e8
                                > listing_info.price * 1.01
                                and (
                                    role["role_id"]
                                    not in [flow["role_id"] for flow in flow_list]
                                )
                            ]
                            assert available_role_id_list, "no available role_id_list"
                            role_id = random.choice(available_role_id_list)
                            logging.info(
                                f"creating magiceden_buy for nft: {nft} and role_id: {role_id}"
                            )
                            res = magiceden_buy(
                                role_id, nft["mint_address"], nft["name"]
                            )
                            # res = create_flow(
                            #     CreateFlowRequest(
                            #         flow_name="magiceden_buy",
                            #         flow_description="",
                            #         script_id="204",
                            #         role_id_list=["3110"],
                            #         plan_start_time=datetime.now(),
                            #         plan_end_time=(datetime.now() + timedelta(days=1)),
                            #         run_amount="1",
                            #         plan_complate_count="1",
                            #         use_aliyun_count="1",
                            #         user_parameter=json.dumps(
                            #             {
                            #                 "role_id": role_id,
                            #                 "mint_address": nft["mint_address"],
                            #                 "magiceden_token_name": nft["name"],
                            #             }
                            #         ),
                            #         task_type_code=TaskTypeCode.UI,
                            #     )
                            # )
                            assert (
                                res["code"] == 0
                            ), f"failed to create flow: {res['message']}"
                            logging.info("create magiceden_buy flow successfully")
                            # store["flow_id_list"].append(res["data"])
                            flow_list_res = get_flow_list()
                            assert (
                                flow_list_res["code"] == 0
                            ), f'failed to get flow list: {flow_list_res["message"]}'
                            flow_list.append(
                                {
                                    "flow_id": flow_list_res["data"]["data"][0]["id"],
                                    "nft_mint_address": nft["mint_address"],
                                    "role_id": role_id,
                                }
                            )
                    else:
                        owner = get_token_owner(nft["mint_address"])
                        owner_role_id_ = [
                            role["role_id"]
                            for role in role_list
                            if role["pubkey"] == owner
                        ]
                        if not owner_role_id_:
                            logging.error(
                                f"the owner of the nft: {nft} is {owner} which does not belong to us"
                            )
                            nft_list = [
                                nft_
                                for nft_ in nft_list
                                if nft_["mint_address"] != nft["mint_address"]
                            ]
                        elif owner_role_id_flow := [
                            flow
                            for flow in flow_list
                            if flow["role_id"] == owner_role_id_[0]
                        ]:
                            logging.error(
                                f"the owner of the nft: {nft} is occupied in flow: {owner_role_id_flow}"
                            )
                        else:
                            floor_price = (
                                MagicEdenApiClient()
                                .get_collection_info(nft_collection_name)
                                .floor_price
                            )
                            listing_price = round(
                                floor_price * random.uniform(1.01, 1.03), 2
                            )
                            logging.info(
                                f"create magiceden_list for nft: {nft}, floor_price: {floor_price}, listing price: {listing_price}"
                            )
                            res=magiceden_list(owner_role_id_[0], nft["mint_address"], nft["name"], listing_price)
                            # res = create_flow(
                            #     CreateFlowRequest(
                            #         flow_name="magiceden_list",
                            #         flow_description="",
                            #         script_id="203",
                            #         role_id_list=["3110"],
                            #         plan_start_time=datetime.now(),
                            #         plan_end_time=(datetime.now() + timedelta(days=1)),
                            #         run_amount="1",
                            #         plan_complate_count="1",
                            #         use_aliyun_count="1",
                            #         user_parameter=json.dumps(
                            #             {
                            #                 "role_id": owner_role_id_[0],
                            #                 "mint_address": nft["mint_address"],
                            #                 "magiceden_token_name": nft["name"],
                            #                 "price": listing_price,
                            #             }
                            #         ),
                            #         task_type_code=TaskTypeCode.UI,
                            #     )
                            # )
                            assert (
                                res["code"] == 0
                            ), f"failed to create flow: {res['message']}"
                            logging.info("create magiceden_list flow successfully")
                            flow_list_res = get_flow_list()
                            assert (
                                flow_list_res["code"] == 0
                            ), f'failed to get flow list: {flow_list_res["message"]}'
                            flow_list.append(
                                {
                                    "flow_id": flow_list_res["data"]["data"][0]["id"],
                                    "nft_mint_address": nft["mint_address"],
                                    "role_id": owner_role_id_[0],
                                }
                            )
            except Exception as e:
                logging.error(str(type(e)) + ": " + str(e))
                if str(e)[:25] == "failed to get flow list":
                    logging.info(f"waiting {client_amount*5} minutes")
                    time.sleep(client_amount * 5 * 60)
                    flow_list_res = get_flow_list()
                    assert (
                        flow_list_res["code"] == 0
                    ), f'failed to get flow list: {flow_list_res["message"]}'
                    assert (
                        flow_list_res["data"]["data"][0]["status_code"] != 1
                    ), "task list is not empty"

                    get_reward_data_time_list = [
                        t for t in get_reward_data_time_list if t > datetime.now()
                    ]
            time.sleep(300)
