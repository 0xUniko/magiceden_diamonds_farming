import os
import sys
from pathlib import Path
import shutil
import json
import random
import subprocess
from typing import Optional


class V2ray:
    v2ray_path = r"C:\v2ray"
    v2ray_work_path = r"C:\work\v2ray"

    def __init__(self, task_id: str, port: Optional[int] = None):
        self.v2ray = None
        self.task_id = task_id
        self.new_v2ray_path = os.path.join(self.v2ray_work_path, task_id)
        self.port = int(port) if port is not None else self.get_port()

    def create(self, proxy_address: str, proxy_port: str, proxy_user: str, proxy_password: str):
        if not os.path.exists(self.v2ray_work_path):
            os.makedirs(self.v2ray_work_path)
        if not os.path.exists(self.new_v2ray_path):
            shutil.copytree(self.v2ray_path, self.new_v2ray_path)

        config_path = os.path.join(self.new_v2ray_path, 'config.json')
        with open(config_path, 'r') as f:
            config = json.load(f)

        config["inbounds"][0]["port"] = self.port
        config["inbounds"][0]["protocol"] = "http"

        config["outbounds"][0]["protocol"] = "http"
        config["outbounds"][0]["settings"]["servers"][0]["port"] = proxy_port
        config["outbounds"][0]["settings"]["servers"][0]["address"] = proxy_address
        config["outbounds"][0]["settings"]["servers"][0]["users"][0]["user"] = proxy_user
        config["outbounds"][0]["settings"]["servers"][0]["users"][0]["pass"] = proxy_password

        with open(config_path, "w") as f:
            json.dump(config, f)

        self.v2ray = subprocess.Popen([os.path.join(self.new_v2ray_path, 'v2ray.exe'), 'run'])

        return self.port

    def get_port(self):
        port = 0
        for i in range(10000, 60000):
            cmd = f'netstat -aon|findstr ":{i}"'
            with os.popen(cmd, "r") as f:
                if "" != f.read():
                    continue
                else:
                    port = i
                    break
        if port == 0:
            print(f"task_{self.task_id}:端口全部被占用")
        print(f"task_{self.task_id}:端口{port}")
        return port

    def exit(self):
        self.v2ray.kill()
        self.v2ray.wait()
        shutil.rmtree(self.new_v2ray_path)
