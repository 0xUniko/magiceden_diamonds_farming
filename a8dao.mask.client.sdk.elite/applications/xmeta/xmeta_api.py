from typing import List, Optional
import requests

from applications.xmeta.xmeta_model import NftWebPrice, NftWebSellOrder


class XMetaApi:
    def __init__(self, api_host: str) -> None:
        self.api_host = api_host
        pass

    def get_floor_price(self, collection_id: int) -> Optional[float]:
        url = f"{self.api_host}/api/collection/product-list"
        params = {
            "id": collection_id,
            "sort": 2,
            "filter_net": [],
            "filter_type": [],
            "filter_status": [1],
            "per_page": 10,
            "page": 1
        }
        response = requests.post(url=url,
                                 json=params,
                                 headers={"Content-Type": "application/json"}
                                 )
        if response.status_code != 200:
            return None
        nft_list = response.json()["data"]["data"]
        if len(nft_list) == 0:
            return None
        return nft_list[0]["floor_price"]

    def get_collection_items(self, collection_id: int, is_listed: bool = False, page_size: int = 100, page: int = 1) -> List[NftWebPrice]:
        url = f"{self.api_host}/api/collection/product-list"
        params = {
            "id": collection_id,
            "sort": 2,
            "filter_net": [],
            "filter_type": [],
            "per_page": page_size,
            "page": page
        }
        if is_listed:
            params["filter_status"] = [1]
        response = requests.post(url=url,
                                 json=params,
                                 headers={"Content-Type": "application/json"}
                                 )
        if response.status_code != 200:
            return []
        response = response.json()
        return [NftWebPrice(**item) for item in response['data']['data']]

    def get_sell_order(self, product_id: int) -> Optional[NftWebSellOrder]:
        url = f"{self.api_host}/api/product/sell-order"
        params = {
            "id": product_id,
            "page": 1
        }
        response = requests.post(url=url,
                                 json=params,
                                 headers={"Content-Type": "application/json"}
                                 )
        if response.status_code != 200:
            return []
        sell_order_list = response.json()["data"]["data"]
        for sell_order in sell_order_list:
            return NftWebSellOrder({
                "address": sell_order["address"],
                "price": float(sell_order["price"]),
                "id": sell_order["id"],
                "product_id": sell_order["product_id"],
            })
        return None
