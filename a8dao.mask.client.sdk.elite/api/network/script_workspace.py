import requests
from api.network import *
from api import headers

script_workspace_config = network_config["script_workspace"]


def download_script(path: str):
    response = requests.get(
        url=f'{host}{script_workspace_config["download_script"]}{path}',
        headers=headers,
    )
    return response.content


def download_requirements(path: str):
    response = requests.get(
        url=f'{host}{script_workspace_config["download_requirements"]}{path}',
        headers=headers,
    )
    return response.content
