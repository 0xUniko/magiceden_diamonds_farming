# -*- coding: utf-8 -*-

import importlib
import inspect
import json
import os
import random
import time
import traceback
from typing import Optional

import chardet
import httpx

import api.network.script
import api.network.script_workspace
import api.network.wallet
import api.remote.flow.flow
from api.remote.flow.flow import get_one_wait_task
from config import config
from model import Script, role_data
from script_base import get_wallet_data_list
from tools.logger import TaskLog


class Client:
    def __init__(self) -> None:
        pass

    def run(self):
        while True:
            print("get_task", flush=True)
            if not self.get_task():
                sleep_sec = random.randint(10, 30)
                print(f"没有任务等待{sleep_sec}秒", flush=True)
                time.sleep(sleep_sec)
                continue
            try:
                self.log("get_task done")
                script = self.get_script(self.task["script_id"])
                if script is None:
                    self.log("script is None")
                    continue
                self.store_script(script)
                self.log("store_script done")
                self.run_script(self.role, self.user_parameter)
                self.log("run_script done")
            except Exception as e:
                self.log(str(e))
            finally:
                self.complate_task(script)

    def get_task(self) -> bool:
        task_response = get_one_wait_task()
        if task_response["data"] is None:
            print("No task", flush=True)
            return False
        self.task = task_response["data"]
        self.task_id = str(task_response["data"]["task_id"])
        self.task_log = TaskLog(self.task_id)
        self.log = self.task_log.log
        self.role = httpx.get(
            "http://127.0.0.1:8452/get_role",
            params={
                "role_id": json.loads(task_response["data"]["user_parameter"])["role_id"]
            },
        ).json()
        if (
            task_response["data"]["extend_information"] == ""
            or task_response["data"]["extend_information"] == None
        ):
            self.role["extend_information"] = {}
        else:
            self.role["extend_information"] = json.loads(
                task_response["data"]["extend_information"]
            )

        if task_response["data"]["fingerprint_data"]["extend_information"] == "":
            self.role["fingerprint_data"]["extend_information"] = {}
        else:
            self.role["fingerprint_data"]["extend_information"] = json.loads(
                task_response["data"]["fingerprint_data"]["extend_information"]
            )

        self.user_parameter = task_response["data"]["user_parameter"]

        self.log("get task successfully")
        return True

    def get_script(self, script_id: str) -> Optional[Script]:
        response = api.network.script.get_by_id(script_id)
        if response["code"] > 0:
            self.log("Can not get the script")
            self.log(response["message"])
            return None
        script_download_path = [
            path
            for path in response["data"]["script_path_list"]
            if str(path).endswith(".py")
        ][0]
        self.log(f"script_download_path:{script_download_path}")
        script_content_bytes = api.network.script_workspace.download_script(
            script_download_path
        )
        script_content_encoding = chardet.detect(script_content_bytes)["encoding"]
        assert script_content_encoding is not None
        script_content = script_content_bytes.decode(script_content_encoding)
        self.log("script download done")
        store_base_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            config["client"]["script_store_directory"],
        )

        script = Script(
            id=script_id,
            script_download_path=script_download_path,
            script_content=script_content,
            script_store_path=os.path.join(store_base_path, f"task_{self.task_id}.py"),
            store_base_path=store_base_path,
        )
        return script

    def store_script(self, script: Script) -> None:
        self.log(f"store_script:{self.task_id}")

        if not os.path.exists(script.store_base_path):
            os.makedirs(script.store_base_path)

        if not os.path.exists(script.script_store_path):
            with open(
                script.script_store_path,
                "w",
                encoding="utf-8",
            ) as f:
                f.write(script.script_content)
        pass

    def run_script(self, role: dict, user_parameter: str) -> Optional[dict]:
        self.log(f"run_script:{self.task_id}")
        try:
            module_name = f"task_{self.task_id}"
            module_path = f'{config["client"]["script_store_directory"]}.{module_name}'
            module = importlib.import_module(module_path)
            self.log(f"load module:{module}")
            run_func = getattr(module, "run")
            self.log("execute run method")
            user_parameter_dict = {}
            try:
                user_parameter_dict: dict = json.loads(user_parameter)
            except:
                self.log("user_parameter is not json")
            self.log(role["fingerprint_data"]["name"])
            result = {}
            signature = inspect.signature(run_func)
            if "task_id" in signature.parameters:
                result = run_func(self.task_id, role, user_parameter_dict)
            else:
                result = run_func(role, user_parameter_dict, self.task_log)

            task_extend_information = {"message": result["message"]}
            api.remote.flow.flow.save_task_biz_status(
                self.task_id, str(result["code"]), task_extend_information
            )
            self.log("run complete")
        except Exception as e:
            error_string = traceback.format_exc()
            self.log(error_string)
        return None

    def complate_task(self, script: Script):
        api.remote.flow.flow.complete_task(self.task_id)
        try:
            os.remove(script.script_store_path)
        except Exception:
            self.log("Can not remove script file")

if __name__ == "__main__":
    Client().run()