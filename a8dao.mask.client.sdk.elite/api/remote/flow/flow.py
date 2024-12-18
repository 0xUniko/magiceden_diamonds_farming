import json
from datetime import datetime
from typing import List, Literal, TypedDict

import requests

from api import headers
from api.remote import *
from api.remote.flow import _flow_config

flow_config = _flow_config["flow"]


def get_one_wait_task() -> dict:
    response = requests.get(
        f'{host}{flow_config["get_one_wait_task"]}', headers=headers
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def create_task_log(task_id: str, log_text: str, log_level=1) -> dict:
    response = requests.post(
        f'{host}{flow_config["create_task_log"]}',
        json={"id": task_id, "log_text": log_text, "log_level": log_level},
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def get_task_list(flow_id: str, page_size: int) -> dict:
    response = requests.get(
        f'{host}{flow_config["get_task_list"]}', params={"flow_id": flow_id, "page_size": page_size}, headers=headers
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def save_task_biz_status(
    task_id: str, task_biz_status: str, task_biz_extend_information: dict
) -> dict:
    response = requests.post(
        f'{host}{flow_config["save_task_biz_status"]}',
        json={
            "task_id": task_id,
            "task_biz_status": task_biz_status,
            "task_biz_extend_information": json.dumps(task_biz_extend_information),
        },
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def complete_task(task_id: str) -> dict:
    response = requests.post(
        f'{host}{flow_config["complete_task"]}',
        json={"task_id": task_id},
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def task_message(task_id: str, task_message: str) -> dict:
    response = requests.post(
        f'{host}{flow_config["task_message"]}',
        json={"task_id": task_id, "task_message": task_message},
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def get_task_message(task_id: str) -> dict:
    response = requests.get(
        f'{host}{flow_config["get_task_message"]}',
        params={"task_id": task_id},
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


class CreateFlowRequest(TypedDict):
    flow_name: str
    flow_description: str
    plan_start_time: datetime
    plan_end_time: datetime
    plan_complate_count: str
    use_aliyun_count: str
    run_amount: str
    script_id: str
    role_id_list: List[str]
    user_parameter: str
    task_type_code: Literal[1] | Literal[2]


def create_flow(request: CreateFlowRequest):
    response = requests.post(
        f'{host}{flow_config["create_flow"]}',
        json={
            **request,
            "plan_start_time": request["plan_start_time"].strftime("%Y-%m-%d %H:%M:%S"),
            "plan_end_time": request["plan_end_time"].strftime("%Y-%m-%d %H:%M:%S"),
        },
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def delete_flow(id: str):
    response = requests.post(
        f'{host}{flow_config["delete_flow"]}',
        json={"id": id},
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


if __name__ == "__main__":
    for id in range(14296, 14304 + 1):
        res = delete_flow(str(id))
        print(f"id: {id}, res: {res}")
