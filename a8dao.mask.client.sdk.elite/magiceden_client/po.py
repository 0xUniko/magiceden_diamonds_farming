from dataclasses import dataclass
import decimal
from typing import Any, List

from solana.transaction import Transaction
from solders.hash import Hash

from magiceden.magiceden_client.types import (
    from_dict,
    from_float,
    from_int,
    from_list,
    from_str,
)

import logging

from mnemonic import Mnemonic
from solders.keypair import Keypair
from solders.pubkey import Pubkey
from spl.token.constants import ASSOCIATED_TOKEN_PROGRAM_ID, TOKEN_PROGRAM_ID

logger = logging.getLogger(__name__)

LAMPORTS_CURRENCY = 10e8


class Account:
    keypair: Keypair

    def __init__(self, keypair: Keypair):
        self.keypair = keypair

    @property
    def pubkey(self):
        return self.keypair.pubkey()

    @staticmethod
    def from_private_key(private_key: str):
        return Account(Keypair.from_base58_string(private_key))

    @staticmethod
    def from_mnemonic(mnemonic: str, passphrase: str = ""):
        seed = Mnemonic().to_seed(mnemonic, passphrase)
        return Account(Keypair.from_seed_and_derivation_path(seed, "m/44/501/0/0"))

    def get_token_ata(self, token_mint: str):
        """
        get token associated account address

        :param token_mint:
        :return:
        """
        return self.pubkey.find_program_address(
            [
                bytes(self.pubkey),
                bytes(TOKEN_PROGRAM_ID),
                bytes(Pubkey.from_string(token_mint)),
            ],
            ASSOCIATED_TOKEN_PROGRAM_ID,
        )[0]

    def sign_message(self, message: bytes):
        return self.keypair.sign_message(message)

    def __str__(self):
        return str(self.pubkey)


@dataclass
class NftTokenInfo:
    mint_address: str
    owner: str
    price: float | None
    name: str | None
    collection: str
    supply: int | None
    collection_name: str
    token_address: str | None

    @staticmethod
    def from_dict(obj: dict) -> "NftTokenInfo":
        return NftTokenInfo(
            mint_address=from_str(obj.get("mintAddress")),
            owner=from_str(obj.get("owner")),
            supply=obj.get("supply"),
            price=obj.get("price"),
            collection=from_str(obj.get("collection")),
            collection_name=from_str(obj.get("collectionName")),
            name=obj.get("name"),
            token_address=obj.get("tokenAddress"),
        )


@dataclass
class NftInstruction:
    type: str
    data: bytes
    recent_blockhash: Hash | None

    @staticmethod
    def from_dict(obj: dict) -> "NftInstruction":
        tx = obj.get("txSigned")
        assert isinstance(tx, dict)

        bh = obj.get("blockhashData")
        if bh is not None:
            blockhash = from_str(bh.get("blockhash"))
            return NftInstruction(
                type=from_str(tx.get("type")),
                data=bytes(from_list(from_int, tx.get("data"))),
                recent_blockhash=Hash.from_string(blockhash),
            )
        return NftInstruction(
            type=from_str(tx.get("type")),
            data=bytes(from_list(from_int, tx.get("data"))),
            recent_blockhash=None,
        )

    def to_transaction(self):
        return Transaction.deserialize(self.data)


@dataclass
class NftListingInfo:
    pda_address: str
    auction_house: str
    token_address: str
    token_mint: str
    seller: str
    seller_referral: str | None
    token_size: int
    price: float
    token_info: NftTokenInfo

    @staticmethod
    def from_dict(obj: dict) -> "NftListingInfo":
        return NftListingInfo(
            pda_address=from_str(obj.get("pdaAddress")),
            auction_house=from_str(obj.get("auctionHouse")),
            token_address=from_str(obj.get("tokenAddress")),
            token_mint=from_str(obj.get("tokenMint")),
            seller=from_str(obj.get("seller")),
            seller_referral=obj.get("sellerReferral"),
            token_size=from_int(obj.get("tokenSize")),
            price=from_float(obj.get("price")),
            token_info=NftTokenInfo.from_dict(from_dict(obj.get("token"))),
        )


@dataclass
class TokenActivity:
    signature: str
    type: str
    source: str
    token_mint: str
    collection_symbol: str
    slot: int
    block_time: int
    buyer: str | None
    buyer_referral: str
    seller: str | None
    seller_referral: str
    price: float

    @staticmethod
    def from_dict(obj: Any) -> "TokenActivity":
        assert isinstance(obj, dict)
        return TokenActivity(
            signature=from_str(obj.get("signature")),
            type=from_str(obj.get("type")),
            source=from_str(obj.get("source")),
            token_mint=from_str(obj.get("tokenMint")),
            collection_symbol=from_str(obj.get("collectionSymbol")),
            slot=from_int(obj.get("slot")),
            block_time=from_int(obj.get("blockTime")),
            buyer=obj.get("buyer"),
            buyer_referral=from_str(obj.get("buyerReferral")),
            seller=obj.get("seller"),
            seller_referral=from_str(obj.get("sellerReferral")),
            price=from_float(obj.get("price")),
        )


@dataclass
class CollectionInfo:
    symbol: str
    floor_price: float
    avg_price24_hr: float | None
    volume_all: float
    listed_count: int | None

    @staticmethod
    def from_dict(obj: Any) -> "CollectionInfo":
        assert isinstance(obj, dict)
        floor_lamports = decimal.Decimal(
            str(from_float(obj.get("floorPrice")))
        ) / decimal.Decimal(LAMPORTS_CURRENCY)
        return CollectionInfo(
            symbol=from_str(obj.get("symbol")),
            floor_price=float(floor_lamports),
            listed_count=obj.get("listedCount"),
            avg_price24_hr=obj.get("avgPrice24hr"),
            volume_all=from_float(obj.get("volumeAll")),
        )


@dataclass
class TradeAccount:
    sol_account: Account
    balance: float
    tokens: List[NftTokenInfo]
