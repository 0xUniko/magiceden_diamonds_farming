import requests
from api.remote.resource import *
from api import headers
from api.remote import *

proxy_config = resource_config["proxy"]


def take_line(line_type: int,
              country: str,
              social_media_sensitive: bool = True,
              expiry: int = 3600) -> dict:
    response = requests.post(
        f'{host}{proxy_config["take_line"]}',
        json={
            "line_type": line_type,
            "social_media_sensitive": social_media_sensitive,
            "country": country,
            "expiry": expiry
        },
        headers=headers,
    )
    if response.status_code != 200:
        return {"code": 1, "message": response.reason}
    return response.json()
