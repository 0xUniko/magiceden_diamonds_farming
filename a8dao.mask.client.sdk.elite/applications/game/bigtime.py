from datetime import datetime
import random
import time
from typing import Any, Dict, List, Optional
import json
import requests
from fingerprint.browser import Browser
from tools.logger import TaskLog


class BigTime:
    def __init__(
        self, task_log: TaskLog, browser: Browser, collector_url: str, api_url: str
    ) -> None:
        self.task_log = task_log
        self.browser = browser
        self.marketplace_base_url = "https://api.openloot.com/v2/market"
        self.collector_url = collector_url
        self.api_url = api_url
        self.headers = {"ContentType": "application/json"}
        pass

    def get_all_archetype_id(self) -> List[dict]:
        page = 1
        total_pages = 1
        item_metadata_list: List[dict] = []
        while True:
            url = f"{self.marketplace_base_url}/listings?gameId=56a149cf-f146-487a-8a1c-58dc9ff3a15c&onSale=true&page={page}&sort=name%3Aasc&pageSize=250"
            self.browser.get(url)
            pre_element = self.browser.find_element_and_wait("pre", timeout=3)
            result: dict = json.loads(pre_element.text)
            items = result.get("items", None)
            if items:
                for item in items:
                    item_metadata = {
                        "archetype_id": item["metadata"]["archetypeId"],
                        "name": item["metadata"]["name"],
                        "description": item["metadata"]["description"],
                        "tags": item["metadata"]["nftTags"],
                        "rarity": item["metadata"]["rarity"],
                        "max_issuance": item["metadata"]["maxIssuance"],
                    }
                    item_metadata_list.append(item_metadata)
            total_pages = result["totalPages"]
            page += 1
            if page > total_pages:
                break
        return item_metadata_list
        # response = requests.post(
        #     url=f"{self.collector_url}/MarketPlace/AddItemMetaDatas",
        #     headers=self.headers,
        #     json=item_metadata_list,
        # )
        # if response.status_code != 200:
        #     self.task_log.warn(response.reason)
        pass

    def _get_item_prices(self, archetype_id: str, pagesize: int = 1) -> dict:
        url = f"{self.marketplace_base_url}/listings/{archetype_id}/items?onSale=true&page=1&pageSize={pagesize}&sort=price:asc"
        self.browser.get(url, False)
        try:
            pre_element = self.browser.find_element_and_wait("pre", timeout=3)
            result: dict = json.loads(pre_element.text)
            return result
        except Exception as e:
            self.task_log.error(e)
        return []

    def get_item_prices(self) -> Optional[str]:
        task_url = f"{self.collector_url}/MarketPlace/GetTask"
        response = requests.get(url=task_url, headers=self.headers)
        if response.status_code != 200:
            self.task_log.warn(response.reason)
        elif not response.text:
            self.task_log.debug("No task")
        else:
            archetype_id = response.text
            response = self._get_item_prices(archetype_id)
            items = response.get("items", [])
            if len(items) > 0:
                tags = items[0]["item"]["metadata"]["nftTags"]
                rarity = items[0]["item"]["metadata"]["rarity"]
                post_data = {
                    "archetype_id": archetype_id,
                    "tags": tags,
                    "rarity": rarity,
                    "price": min([float(item["price"]) for item in items]),
                    "total": int(response["totalItems"]),
                }

                response = requests.post(
                    url=f"{self.collector_url}/MarketPlace/AddItems",
                    headers=self.headers,
                    json=post_data,
                )
                self.task_log.info(f"Finish archetype id: {archetype_id}")
                if response.status_code != 200:
                    self.task_log.warn(response.reason)
            return archetype_id

        return None

    def _get_transaction_offset(self, archetype_id: str) -> Optional[Dict[str, Any]]:
        url = f"{self.collector_url}/MarketPlace/GetTransactionOffset?archetypeId={archetype_id}"
        try:
            response = requests.get(url=url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            self.task_log.error(
                f"Failed to get transaction offset for archetype {archetype_id}: {e}"
            )
            return None

    def _fetch_transactions(
        self, archetype_id: str, page: int
    ) -> Optional[Dict[str, Any]]:
        url = f"{self.marketplace_base_url}/items/transaction/history?archetypeId={archetype_id}&page={page}"
        try:
            self.browser.get(url)
            pre_element = self.browser.find_element_and_wait("pre", timeout=3)
            return json.loads(pre_element.text)
        except Exception as e:
            self.task_log.error(
                f"Failed to fetch transactions for archetype {archetype_id} on page {page}: {e}"
            )
            return None

    def _send_transactions_to_collector(
        self, archetype_id: str, transactions: List[Dict[str, Any]]
    ) -> None:
        post_data = {"archetype_id": archetype_id, "transactions": transactions}
        url = f"{self.collector_url}/MarketPlace/AddItemTransactions"
        try:
            response = requests.post(url=url, headers=self.headers, json=post_data)
            response.raise_for_status()
            self.task_log.info(
                f"Successfully sent transactions for archetype {archetype_id}"
            )
        except requests.RequestException as e:
            self.task_log.warn(
                f"Failed to send transactions for archetype {archetype_id}: {e}"
            )

    def get_item_sale_orders(self, archetype_id: str) -> None:
        count = 0
        page = 1

        transaction_offset = self._get_transaction_offset(archetype_id)
        if transaction_offset is None:
            return

        first_timestamp, last_timestamp = 0, 0
        if transaction_offset.get("first") and transaction_offset.get("last"):
            first_timestamp = datetime.strptime(
                transaction_offset["first"]["createdTime"], "%Y-%m-%dT%H:%M:%S.%f%z"
            ).timestamp()
            last_timestamp = datetime.strptime(
                transaction_offset["last"]["createdTime"], "%Y-%m-%dT%H:%M:%S.%f%z"
            ).timestamp()
            self.task_log.info(
                f"Find transaction offset for archetype {archetype_id}: First offset: {first_timestamp}, Last offset: {last_timestamp}"
            )
        else:
            self.task_log.info(f"No transaction data for archetype {archetype_id}")

        while True:
            self.task_log.info(
                f"Start fetching transactions for archetype {archetype_id}, page {page}"
            )
            transactions_data = self._fetch_transactions(archetype_id, page)
            if transactions_data is None or transactions_data.get("totalItems", 0) == 0:
                break

            transactions = [
                {
                    "issued_id": item["issuedId"],
                    "from_user": item["fromUser"],
                    "to_user": item["toUser"],
                    "price": item["price"],
                    "created_time": item["date"],
                }
                for item in transactions_data.get("items", [])
                if item.get("price") > 0 and item.get("eventName") == "sale"
            ]

            if transactions:
                new_transactions = []
                for transaction in transactions:
                    transaction_timestamp = datetime.strptime(
                        transaction["created_time"], "%Y-%m-%dT%H:%M:%S.%fZ"
                    ).timestamp()

                    if (
                        first_timestamp > 0
                        and last_timestamp > 0
                        and transaction_timestamp <= first_timestamp
                    ):
                        self.task_log.info("Reached an existing transaction, stopping.")
                        break
                    new_transactions.append(transaction)

                if new_transactions:
                    count += len(new_transactions)
                    self._send_transactions_to_collector(archetype_id, new_transactions)
            page += 1
            self.task_log.info(f"{count} Transactions found.")
        pass
