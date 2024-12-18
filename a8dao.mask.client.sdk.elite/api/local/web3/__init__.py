from typing import Generic, Literal, Optional, TypedDict, TypeVar

from api.local import local_config
from model import ChainId

web3_config = local_config["web3"]
host = web3_config["host"]
port = web3_config["port"]
# base_url = f"{host}:{port}"
base_url = "http://127.0.0.1:8000"


class FailedRes(TypedDict):
    code: Literal[1]
    # code: int
    message: str


T = TypeVar("T")


class SuccessRes(TypedDict, Generic[T]):
    code: Literal[0]
    message: Literal["OK"]
    data: T


class Response(TypedDict, Generic[T]):
    code: int
    message: Optional[str]
    data: Optional[T]
