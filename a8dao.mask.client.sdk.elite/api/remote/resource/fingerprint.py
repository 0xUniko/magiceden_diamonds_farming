import requests
import api.remote.resource
import api

fingerprint_config = api.remote.resource.resource_config["fingerprint"]


def get_by_fingerprint_name(name: str) -> dict:
    response = requests.get(
        f'{api.remote.resource.host}{fingerprint_config["get_by_fingerprint_name"]}?name={name}',
        headers=api.headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()


def modify_browser_id(name: str, browser_id: str) -> dict:
    post_data = {
        "name": name,
        "browser_id": browser_id
    }
    response = requests.post(
        f'{api.remote.resource.host}{fingerprint_config["modify_browser_id"]}',
        json=post_data,
        headers=api.headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()
