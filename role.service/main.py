import json
import os
import random
import string
from typing import TypedDict

import httpx
from fastapi import FastAPI
from mnemonic import Mnemonic
from pydantic import BaseModel
from solders.keypair import Keypair

app = FastAPI()
# we use post 8452
# uvicorn main:app --port=8452


class Wallet(TypedDict):
    address: str
    metamask_password: str
    mnemonic: str
    chain_id: str


class Fingerprint(TypedDict):
    name: str


class Role(TypedDict):
    role_id: int
    wallet_data: list[Wallet]
    fingerprint_data: Fingerprint


@app.post("/create_role")
def create_role():
    if not os.path.isfile("./accounts.json"):
        with open("./accounts.json", "w") as f:
            json.dump([], f)
    with open("./accounts.json", "r") as f:
        accounts: list[Role] = json.load(f)
    mnemonic = Mnemonic("english").generate(strength=128)
    seed = Mnemonic().to_seed(mnemonic, "")
    address = str(Keypair.from_seed_and_derivation_path(seed, "m/44/501/0/0").pubkey())
    characters = (
        (string.ascii_letters + string.digits + string.punctuation)
        .replace('"', "")
        .replace("'", "")
        .replace("\\", "")
    )
    password = "".join(random.choice(characters) for i in range(20))
    wallet = Wallet(
        address=address,
        metamask_password=password,
        mnemonic=mnemonic,
        chain_id="eth-erc20",
    )

    user_id = httpx.post(
        "http://localhost:50325" + "/api/v1/user/create",
        json={"group_id": "0", "user_proxy_config": {"proxy_soft": "no_proxy"}},
    ).json()["data"]["id"]

    accounts.append(
        Role(
            role_id=(accounts[-1]["role_id"] + 1) if accounts else 1,
            wallet_data=[wallet],
            fingerprint_data={"name": user_id},
        )
    )
    with open("./accounts.json", "w") as f:
        json.dump(accounts, f)
    return {"code": 0, "data": None, "message": "success"}


class Request(BaseModel):
    role_id_list: list[int]


@app.get("/get_role")
def read_item(role_id):
    with open("./accounts.json", "r") as f:
        accounts: list[Role] = json.load(f)
    return [role for role in accounts if role["role_id"] == int(role_id)][0]
