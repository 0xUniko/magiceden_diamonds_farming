import json
from typing import Generic, Optional, TypedDict, TypeVar

from fastapi import FastAPI
from mnemonic import Mnemonic
from pydantic import BaseModel
from solana.rpc.async_api import AsyncClient
from solana.rpc.types import TokenAccountOpts
from solders.keypair import Keypair
from solders.pubkey import Pubkey

app = FastAPI()
# we use post 8452
# uvicorn main:app --port=8452
# uvicorn main:app --port=8000


class SplBalance(TypedDict):
    amount: int
    decimals: int
    uiAmountString: str


async def get_solana_client():
    provider_endpoint = ""
    client = AsyncClient(provider_endpoint)
    await client.is_connected()
    return client


async def get_spl_balance111(mint_address: str, owner: str):
    client = await get_solana_client()

    res = await client.get_account_info_json_parsed(Pubkey.from_string(mint_address))
    token_info = json.loads(res.to_json())["result"]["value"]

    opts = TokenAccountOpts(program_id=Pubkey.from_string(token_info["owner"]))
    token_accounts = await client.get_token_accounts_by_owner_json_parsed(
        Pubkey.from_string(owner), opts
    )
    for account in json.loads(token_accounts.to_json())["result"]["value"]:
        info = account["account"]["data"]["parsed"]["info"]
        if info["mint"] == mint_address:
            return SplBalance(
                amount=int(info["tokenAmount"]["amount"]),
                decimals=info["tokenAmount"]["decimals"],
                uiAmountString=info["tokenAmount"]["uiAmountString"],
            )
    return SplBalance(amount=0, decimals=0, uiAmountString="0")


def get_pub_key_from_mnemonic111(mnemonic: str):
    seed = Mnemonic().to_seed(mnemonic, "")
    return str(Keypair.from_seed_and_derivation_path(seed, "m/44/501/0/0").pubkey())


async def get_balance111(pubkey: str):
    client = await get_solana_client()
    return (await client.get_balance(Pubkey.from_string(pubkey))).value


T = TypeVar("T")


class Response(BaseModel, Generic[T]):
    code: int = 0
    message: str = "Ok"
    data: Optional[T] = None


@app.get("/solana/get_spl_balance")
async def get_spl_balance(mint_address: str, owner: str) -> Response[SplBalance]:
    balance = await get_spl_balance111(mint_address, owner)
    return Response[SplBalance](data=balance)


@app.get("/solana/get_pub_key_from_mnemonic")
def get_pub_key_from_mnemonic(mnemonic: str) -> Response[str]:
    pub_key = get_pub_key_from_mnemonic111(mnemonic)
    return Response[str](data=pub_key)


@app.get("/solana/get_balance")
async def get_balance(pubkey: str) -> Response[int]:
    return Response[int](data=await get_balance111(pubkey))
