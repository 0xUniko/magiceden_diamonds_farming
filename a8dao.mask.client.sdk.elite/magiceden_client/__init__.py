import logging
from enum import Enum
from config import magiceden_api_key

import httpx

from magiceden.magiceden_client.po import (
    CollectionInfo,
    NftInstruction,
    NftListingInfo,
    NftTokenInfo,
    TokenActivity,
)

logger = logging.getLogger(__name__)

AUCTION_HOUSE_ADDRESS = "E8cU1WiRWjanGxmn96ewBgk9vPTcL6AEZ1t6F6fkgUWe"


class TimeRange(Enum):
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    ONE_WEEK = "7d"
    ONE_MONTH = "30d"


class MagicEdenApiClient:
    __client: httpx.Client

    def __init__(
        self,
        base_url: str = "https://api-mainnet.magiceden.dev/v2",
        api_key: str = magiceden_api_key,
    ):
        self.__client = httpx.Client(
            base_url=base_url,
            headers={"Authorization": f"Bearer {api_key}"},
        )

    def list_tokens(self, wallet_address: str):
        """
        list all token owned by wallet

        :param wallet_address:
        :return:
        """
        r = self.__client.get(f"/wallets/{wallet_address}/tokens")
        logger.debug("list_tokens raw response {}".format(r.text))
        return list(map(lambda x: NftTokenInfo.from_dict(x), r.json()))

    def get_token_detail(self, token_mint: str):
        r = self.__client.get(f"/tokens/{token_mint}")
        logger.debug("get_token_detail raw response {}".format(r.text))
        return NftTokenInfo.from_dict(r.json())

    def get_listings_for_token(self, token_mint: str):
        r = self.__client.get(f"/tokens/{token_mint}/listings")
        logger.debug("get_listings_for_token raw response {}".format(r.text))
        return list(map(lambda v: NftListingInfo.from_dict(v), r.json()))

    def create_sell_instruction(
        self,
        seller: str,
        token_mint: str,
        token_account: str,
        price: float,
        priority_fee: int,
    ):
        r = self.__client.get(
            "/instructions/sell",
            params={
                "price": price,
                "seller": seller,
                "tokenMint": token_mint,
                "tokenAccount": token_account,
                "auctionHouseAddress": AUCTION_HOUSE_ADDRESS,
                "priorityFee": priority_fee,
            },
        )
        logger.debug("create_sell_instruction raw response {}".format(r.text))
        return NftInstruction.from_dict(r.json())

    def create_buy_now_instruction(
        self,
        buyer: str,
        seller: str,
        token_mint: str,
        token_ata: str,
        price: float,
        priority_fee: int,
    ):
        r = self.__client.get(
            "/instructions/buy_now",
            params={
                "price": price,
                "buyer": buyer,
                "seller": seller,
                "tokenMint": token_mint,
                "tokenATA": token_ata,
                "auctionHouseAddress": AUCTION_HOUSE_ADDRESS,
                "priorityFee": priority_fee,
            },
        )
        logger.debug("create_buy_now_instruction raw response {}".format(r.text))
        return NftInstruction.from_dict(r.json())

    def create_buy_instruction(
        self,
        buyer: str,
        token_mint: str,
        price: float,
        priority_fee: int,
    ):
        r = self.__client.get(
            "/instructions/buy",
            params={
                "price": price,
                "buyer": buyer,
                "tokenMint": token_mint,
                "auctionHouseAddress": AUCTION_HOUSE_ADDRESS,
                "buyerExpiry": 0,
                "sellerExpiry": -1,
                "priorityFee": priority_fee,
            },
        )
        logger.debug("create_buy_instruction raw response {}".format(r.text))
        return NftInstruction.from_dict(r.json())

    def get_token_activities(self, token_mint: str):
        r = self.__client.get(f"/tokens/{token_mint}/activities")
        logger.debug("get_token_activities raw response {}".format(r.text))
        return list(map(lambda v: TokenActivity.from_dict(v), r.json()))

    def get_top_collections(self, time_range: TimeRange):
        r = self.__client.get(
            "/marketplace/popular_collections", params={"timeRange": time_range.value}
        )
        logger.debug("get_top_collections raw response {}".format(r.text))
        return list(map(lambda v: CollectionInfo.from_dict(v), r.json()))

    def get_collections(self, offset: int = 0, limit: int = 200):
        r = self.__client.get("/collections", params={"offset": offset, "limit": limit})
        logger.debug("get_collections raw response {}".format(r.text))
        return list(map(lambda v: CollectionInfo.from_dict(v), r.json()))

    def get_collection_info(self, symbol: str):
        r = self.__client.get(f"/collections/{symbol}/stats")
        logger.debug("get_collection_info raw response {}".format(r.text))
        return CollectionInfo.from_dict(r.json())

    def get_listings_of_collection(self, symbol: str):
        r = self.__client.get(f"/collections/{symbol}/listings")
        logger.debug("get_listings_of_collection raw response {}".format(r.text))
        return list(map(lambda v: NftListingInfo.from_dict(v), r.json()))
