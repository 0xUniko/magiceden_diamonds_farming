from dataclasses import dataclass
from config import config, get_account_org_id
from typing import Optional, Type, TypeVar, Generic
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from model import ChainId

T = TypeVar("T")

retries = Retry(total=30,
                backoff_factor=1,
                status_forcelist=[500, 502, 503, 504])

adapter = HTTPAdapter(max_retries=retries)


headers = {
    "Content-Type": "application/json",
    "user_flow_token": config["api"]["user_flow_token"],
    "account_org_id": get_account_org_id(config["api"]),
}


@dataclass
class Response(Generic[T]):
    code: int = 0
    message: str = "Ok"
    data: Optional[T] = None


def get_requests() -> requests.Session:
    session = requests.Session()
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session


def _get_chain_name(chain_id: ChainId) -> str:
    chain_name = chain_id.value
    if chain_id == ChainId.ETH_ZKS_ERA:
        chain_name = "eth-zksync"
    if chain_id == ChainId.MATIC_POLYGON:
        chain_name = "eth-polygon"
    return chain_name


def get_response(
    http_response: requests.Response, response_type: Optional[Type[T]] = None
) -> Response[T]:
    response = Response[T]()
    if http_response.status_code != 200:
        response.code = http_response.status_code
        response.message = http_response.reason
    else:
        json_data = http_response.json()
        response.code = json_data["code"]
        if response.code != 0:
            response.message = json_data["message"]
        else:
            if response_type:
                try:
                    response.data = response_type(**json_data["data"]["data"])
                except:
                    try:
                        response.data = response_type(**json_data["data"])
                    except:
                        response.data = response_type(json_data["data"])
    return response
