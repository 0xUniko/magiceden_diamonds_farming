from datetime import datetime
from enum import Enum
from typing import Optional

import requests as requests

import api.remote.flow.flow


def task_log(task_id: str, log_text: str) -> None:
    print(f"[{str(datetime.now())}]{task_id}:{log_text}", flush=True)
    try:
        api.remote.flow.flow.create_task_log(
            task_id, log_text, int(LogLevel.info.value)
        )
    except Exception as e:
        print(str(e))
    pass


class LogLevel(Enum):
    debug = 0
    info = 1
    warn = 2
    error = 3


class TaskLog:
    def __init__(self, task_id: str) -> None:
        self.task_id = task_id
        pass

    def debug(self, log_text: Optional[str]) -> None:
        # self.log(log_text, LogLevel.debug)
        pass

    def info(self, log_text: Optional[str]) -> None:
        self.log(log_text, LogLevel.info)
        pass

    def warn(self, log_text: Optional[str]) -> None:
        self.log(log_text, LogLevel.warn)
        pass

    def error(self, exception: Exception) -> None:
        self.log(str(exception), LogLevel.error)
        pass

    def log(self, log_text: str, log_level: LogLevel = LogLevel.info) -> None:
        print(f"[{log_level.name}]{log_text}", flush=True)
        try:
            api.remote.flow.flow.create_task_log(
                self.task_id, log_text, int(log_level.value)
            )
        except Exception as e:
            print(str(e))
        pass
