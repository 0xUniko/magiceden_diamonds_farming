import csv
from datetime import datetime
import random
import time
from typing import Dict, List, Optional, Tuple
from tinydb import Query, TinyDB
from api.local.web3 import SuccessRes
from applications.xmeta.xmeta_model import *
from applications.xmeta.xmeta_api import XMetaApi
import api.local.web3.eth_erc721 as eth_erc721
import api.local.web3.eth_erc20 as eth_erc20
import scripts.xMeta.xMeta_buy as buy_script
import scripts.xMeta.xMeta_sell as sell_script
import script_base
import tools.exchange as cex


class XMetaLiquidity:
    def __init__(
        self, chain_id: ChainId, role_label_id: int, database_path: str
    ) -> None:
        self.chain_id = chain_id
        self.role_label_id = role_label_id
        self.xmeta_api = XMetaApi("https://api.x-meta.hk")
        self.trading_contract_address = (
            "0x7710Dd3e8cf3a3f6dcC3b2c4C891Df6a2A5c1aA8".lower()
        )
        self.database_path = database_path
        database = TinyDB(f"{self.database_path}/xmeta_liquidity.json")
        self.nft_asset_table = database.table("nft_asset")
        self.collection_table = database.table("collection")
        self.account_table = database.table("account")
        self.liquidity_user_table = database.table("liquidity_user")
        self.group_liquidity_user_table = database.table("group_liquidity_user")
        self.group_table = database.table("group")
        self.trading_account_contract_permission_table = database.table(
            "trading_account_contract_permission"
        )
        self.gas_table = database.table("gas")
        self.nft_sale_order_table = database.table("nft_sale_order")
        self.nft_external_purchase_order_table = database.table(
            "nft_external_purchase_order"
        )
        pass

    """
    创建合集
    """

    def create_collection(self, id: int, name: str, contract_address: str, total: int):
        nft_list = self.xmeta_api.get_collection_items(id, False, page_size=total)
        assert len(nft_list) > 0, f"no nft for collection {name}"

        nft_asset_list = [
            NftAsset(
                {
                    "collection_id": n["series_id"],
                    "name": name,
                    "product_id": n["id"],
                    "token_id": n["token_id"],
                }
            )
            for n in nft_list
        ]

        self.nft_asset_table.insert_multiple(nft_asset_list)
        collection = Collection(
            {
                "collection_id": id,
                "name": name,
                "total": total,
                "contract_address": contract_address.lower(),
            }
        )
        self.collection_table.insert(collection)
        pass

    """
    加载合集
    """

    def load_collection(self, contract_address: str) -> None:
        self.collection = Collection(
            **self.collection_table.get(
                Query().contract_address == contract_address.lower()
            )
        )
        assert self.collection is not None, f"no collection for {contract_address}"
        self.nft_asset_list = [
            NftAsset(**n)
            for n in self.nft_asset_table.search(
                Query().collection_id == self.collection["collection_id"]
            )
        ]
        assert (
            len(self.nft_asset_list) > 0
        ), f"no nft asset for {self.collection['name']}"
        pass

    """
    创建分组流动性用户
    """

    def create_group_liquidity_user_list(
        self,
        group_name: str,
        contract_address: str,
        asset_group_liquidity_user_limit: int,
        group_liquidity_user_limit: int,
    ) -> None:
        self.load_collection(contract_address.lower())
        liquidity_user_list = self.liquidity_user_table.all()
        group_liquidity_user_list: List[GroupLiquidityUser] = []
        group_liquidity_user_count = 0
        for liquidity_user in liquidity_user_list:
            if group_liquidity_user_count < asset_group_liquidity_user_limit:
                token_id_list = self.get_token_id_list(liquidity_user, contract_address)
                if len(token_id_list) > 0:
                    group_liquidity_user = {
                        "contract_address": contract_address.lower(),
                        "group_name": group_name,
                        "liquidity_user_id": liquidity_user.doc_id,
                    }
                    group_liquidity_user_list.append(group_liquidity_user)
                    group_liquidity_user_count += 1
                    print(f"Create group liquidity user {liquidity_user}")

        if len(group_liquidity_user_list) < group_liquidity_user_limit:
            group_liquidity_user_id_list = [
                g["liquidity_user_id"] for g in group_liquidity_user_list
            ]
            unselected_liquidity_user_id_list = [
                l
                for l in liquidity_user_list
                if l.doc_id not in group_liquidity_user_id_list
            ]
            unselected_liquidity_user_list = random.sample(
                unselected_liquidity_user_id_list,
                group_liquidity_user_limit - len(group_liquidity_user_list),
            )
            for unselected_liquidity_user in unselected_liquidity_user_list:
                group_liquidity_user = {
                    "contract_address": contract_address.lower(),
                    "group_name": group_name,
                    "liquidity_user_id": unselected_liquidity_user.doc_id,
                }
                group_liquidity_user_list.append(group_liquidity_user)
        self.group_liquidity_user_table.insert_multiple(group_liquidity_user_list)
        pass

    """
    创建分组
    """

    def create_group_by_liquidity_users(
        self,
        name: str,
        contract_address: str,
        loop_limit: int,
        cex_withdraw_amount_range: List[float],
        liquidity_user_id_list: List[int],
    ) -> None:
        print(f"Start to create group {name}")
        assert (
            len(self.group_table.search(Query().name == name)) == 0
        ), f"group {name} already exists"
        group = Group(
            {
                "name": name,
                "contract_address": contract_address.lower(),
                "created_time": int(datetime.now().timestamp()),
                "is_active": True,
                "loop_limit": loop_limit,
                "group_liquidity_user_limit": len(liquidity_user_id_list),
                "cex_withdraw_amount_range": cex_withdraw_amount_range,
            }
        )
        self.group_table.insert(group)
        self.load_collection(contract_address.lower())
        group_liquidity_user_list = []
        for id in liquidity_user_id_list:
            group_liquidity_user = {
                "contract_address": contract_address.lower(),
                "group_name": name,
                "liquidity_user_id": id,
            }
            group_liquidity_user_list.append(group_liquidity_user)
        self.group_liquidity_user_table.insert_multiple(group_liquidity_user_list)
        print(f"End to create group {name}")
        pass

    def create_group(
        self,
        name: str,
        contract_address: str,
        loop_limit: int,
        cex_withdraw_amount_range: List[float],
        asset_group_liquidity_user_limit: int,
        group_liquidity_user_limit: int,
        is_create_liquidity_user: bool = True,
    ) -> None:
        print(f"Start to create group {name}")
        assert (
            len(self.group_table.search(Query().name == name)) == 0
        ), f"group {name} already exists"
        group = Group(
            {
                "name": name,
                "contract_address": contract_address.lower(),
                "created_time": int(datetime.now().timestamp()),
                "is_active": True,
                "loop_limit": loop_limit,
                "group_liquidity_user_limit": group_liquidity_user_limit,
                "cex_withdraw_amount_range": cex_withdraw_amount_range,
            }
        )
        self.group_table.insert(group)
        if is_create_liquidity_user:
            self.create_group_liquidity_user_list(
                name,
                contract_address.lower(),
                asset_group_liquidity_user_limit,
                group_liquidity_user_limit,
            )
        print(f"End to create group {name}")
        pass

    """
    加载分组
    """

    def load_group(self, name: str):
        print(f"Start load group for {name}")
        self.group = Group(
            **self.group_table.get((Query().name == name) & (Query().is_active == True))
        )
        assert self.group is not None, f"no actived group for {name}"

        self.group_liquidity_user_list: List[GroupLiquidityUser] = []
        for g in self.group_liquidity_user_table.search(Query().group_name == name):
            self.group_liquidity_user_list.append(g)
        self.liquidity_user_list_in_group: List[LiquidityUser] = []
        for g in self.group_liquidity_user_list:
            liquidity_user = self.liquidity_user_table.get(
                doc_id=g["liquidity_user_id"]
            )
            if liquidity_user:
                self.liquidity_user_list_in_group.append(liquidity_user)

        self.current_loop_count = self.gas_table.count(
            (Query().gas_type == GasType.PLACE_ORDER.value)
            & (Query().group_name == self.group["name"])
        )

        self.load_collection(self.group["contract_address"])
        print(f"Finish load group for {name}")
        pass

    """
    分组提现
    """

    def withdraw_group(self):
        for group_liquidity_user in self.group_liquidity_user_list:
            liquidity_user: LiquidityUser = self.liquidity_user_table.get(
                doc_id=group_liquidity_user["liquidity_user_id"]
            )
            self.trading_withdraw_to_captial(liquidity_user)
            self.captial_withdraw_to_cex(liquidity_user)
        pass

    """
    保存Gas记录
    """

    def save_gas(
        self,
        gas_type: GasType,
        transaction: dict,
        group_name: str,
        gas_cost: Optional[int] = None,
    ) -> None:
        if not gas_cost:
            gas_cost = int(transaction["gasUsed"]) * int(transaction["gasPrice"])
        gas = Gas(
            {
                "chain_id": self.chain_id.value,
                "gas_type": gas_type.value,
                "gas": gas_cost,
                "tx_hash": transaction["hash"],
                "group_name": group_name,
                "created_time": int(datetime.now().timestamp()),
                "from_address": transaction["from"],
                "to_address": transaction["to"],
                "value": int(transaction["value"]) if "value" in transaction else 0,
            }
        )
        if not self.gas_table.get((Query().tx_hash == gas["tx_hash"])):
            self.gas_table.insert(gas)
            pass

    """
    获取流动性用户的token id列表
    """

    def get_token_id_list(
        self, liquidity_user: LiquidityUser, contract_address: str
    ) -> List[int]:
        token_id_list: List[int] = []
        seller_account: Account = self.account_table.get(
            Query().role_id == liquidity_user["trading_role_id"]
        )
        while True:
            try:
                balance = SuccessRes[int](
                    **eth_erc721.balance_of(
                        self.chain_id,
                        contract_address.lower(),
                        seller_account["address"],
                    )
                )["data"]
                if balance > 0:
                    for index in range(balance):
                        token_id = SuccessRes[int](
                            **eth_erc721.token_of_owner_by_index(
                                self.chain_id,
                                contract_address.lower(),
                                seller_account["address"],
                                index,
                            )
                        )["data"]
                        token_id_list.append(token_id)
                break
            except:
                time.sleep(1)
        return token_id_list

    """
    创建NFT销售单
    """

    def create_nft_sale_order(
        self,
        liquidity_user: LiquidityUser,
        nft_web_sell_order: NftWebSellOrder,
        has_permission: bool,
        deposit_result: int,
    ) -> NftSaleOrder:
        nft_sale_order = NftSaleOrder(
            {
                "address": Account(
                    **self.account_table.get(
                        Query().role_id == liquidity_user["trading_role_id"]
                    )
                )["address"],
                "collection_id": self.collection["collection_id"],
                "contract_address": self.group["contract_address"],
                "liquidity_user_id": liquidity_user.doc_id,
                "token_id": next(
                    (
                        n["token_id"]
                        for n in self.nft_asset_list
                        if n["product_id"] == nft_web_sell_order["product_id"]
                    )
                ),
                "created_time": int(datetime.now().timestamp()),
                "price": nft_web_sell_order["price"],
                "product_id": nft_web_sell_order["product_id"],
                "trading_account_role_id": liquidity_user["trading_role_id"],
                "has_permission": has_permission,
                "has_deposit": deposit_result,
            }
        )
        self.nft_sale_order_table.insert(nft_sale_order)
        return nft_sale_order

    """
    删除NFT销售单
    """

    def remove_nft_sale_order(self, token_id: int) -> None:
        nft_sale_order_id_list = self.nft_sale_order_table.remove(
            (Query().contract_address == self.group["contract_address"])
            & (Query().token_id == token_id)
        )
        if len(nft_sale_order_id_list) == 0:
            print(f"Remove nft sale order {token_id} failed")
        else:
            print(f"Remove nft sale order {nft_sale_order_id_list[0]}")
        pass

    """
    获取一个NFT销售单
    """

    def get_one_nft_sale_order(self) -> Optional[NftSaleOrder]:
        nft_sale_order_list: List[NftSaleOrder] = sorted(
            self.nft_sale_order_table.search(
                Query().contract_address == self.group["contract_address"]
            ),
            key=lambda x: x["created_time"],
        )
        for nft_sale_order in nft_sale_order_list:
            address = SuccessRes[str](
                **eth_erc721.owner_of(
                    self.chain_id,
                    nft_sale_order["contract_address"],
                    nft_sale_order["token_id"],
                )
            )["data"].lower()
            if address == nft_sale_order["address"]:
                print(f"Get nft sale order {nft_sale_order['token_id']}")
                return nft_sale_order
            else:
                print(
                    f"Token id {nft_sale_order['token_id']} has been purchased by outside buyer {address}"
                )
                if (
                    self.nft_sale_order_table.count(
                        (Query().token_id == nft_sale_order["token_id"])
                        & (Query().collection_id == nft_sale_order["collection_id"])
                    )
                    == 0
                ):
                    nft_external_purchase_order = NftExternalPurchaseOrder(
                        {
                            "collection_id": nft_sale_order["collection_id"],
                            "contract_address": nft_sale_order["contract_address"],
                            "liquidity_seller_id": nft_sale_order["liquidity_user_id"],
                            "product_id": nft_sale_order["product_id"],
                            "token_id": nft_sale_order["token_id"],
                            "price": nft_sale_order["price"],
                            "seller_address": nft_sale_order["address"],
                            "purchase_address": address,
                            "trading_account_role_id": nft_sale_order[
                                "trading_account_role_id"
                            ],
                            "created_time": nft_sale_order["created_time"],
                        }
                    )
                    self.nft_external_purchase_order_table.insert(
                        nft_external_purchase_order
                    )
                self.nft_sale_order_table.remove(doc_ids=[nft_sale_order.doc_id])
        return None

    """
    充值
    """

    def deposit(self, need_amount: int, liquidity_user: LiquidityUser) -> int:
        deposit_result = 0
        gas_estimated = int(0.001 * 10**18)
        captial_account: Account = self.account_table.get(
            Query().role_id == liquidity_user["captial_role_id"]
        )
        trading_account: Account = self.account_table.get(
            Query().role_id == liquidity_user["trading_role_id"]
        )
        trading_balance = SuccessRes[int](
            **eth_erc20.balance_of(self.chain_id, trading_account["address"])
        )["data"]
        captial_balance = SuccessRes[int](
            **eth_erc20.balance_of(self.chain_id, captial_account["address"])
        )["data"]
        if trading_balance < need_amount:
            print(
                "Trading account has not enough balance, deposit from captial account"
            )
            # 资金账户余额不够支持交易账户的许可费，从交易所提现
            if captial_balance < need_amount + gas_estimated:
                print("Captial account has not enough balance, withdraw from cex")
                amount = random.uniform(
                    self.group["cex_withdraw_amount_range"][0],
                    self.group["cex_withdraw_amount_range"][1],
                )
                while True:
                    try:
                        cex_to_captial_transaction = cex.withdraw(
                            "0",
                            captial_account["address"],
                            self.chain_id,
                            amount,
                            "ETH",
                            self.role_label_id,
                        )
                        assert (
                            cex_to_captial_transaction
                        ), f"no transaction for withdraw {amount} ETH from cex to {captial_account['address']}"
                        self.save_gas(
                            GasType.CEX_TO_CAPITAL,
                            cex_to_captial_transaction,
                            self.group["name"],
                            int(0.0001 * 10**18),
                        )
                        deposit_result = 2
                        break
                    except:
                        print("Withdraw from cex failed, retry")
            print("Deposit from captial account to trading account")
            captial_wallet = script_base.get_wallet(
                self.chain_id, captial_account["role_id"]
            )
            assert (
                captial_wallet
            ), f"no captial wallet for {captial_account['role_id']} in {self.chain_id}"
            captial_to_trading_transaction = SuccessRes[dict](
                **eth_erc20.transfer(
                    self.chain_id,
                    captial_wallet["private_key"],
                    trading_account["address"],
                    need_amount + gas_estimated,
                )
            )["data"]
            self.save_gas(
                GasType.CAPITAL_TO_TRADING,
                captial_to_trading_transaction,
                self.group["name"],
            )
            if deposit_result != 2:
                deposit_result = 1
            print(
                f"Deposit {need_amount} from captial account {captial_account['address']} to trading account {trading_account['address']}"
            )
        else:
            print("Trading account has enough balance")
        return deposit_result

    """
    资金账户提现到交易所
    """

    def captial_withdraw_to_cex(self, liquidity_user: LiquidityUser) -> bool:
        captial_account: Account = self.account_table.get(
            Query().role_id == liquidity_user["captial_role_id"]
        )
        captial_balance = SuccessRes[int](
            **eth_erc20.balance_of(self.chain_id, captial_account["address"])
        )["data"]
        if captial_balance == 0:
            return True
        captial_wallet = script_base.get_wallet(
            self.chain_id, captial_account["role_id"]
        )
        assert (
            captial_wallet
        ), f"no captial wallet for {captial_account['role_id']} in {self.chain_id}"
        captial_to_cex_transaction = cex.recharge(
            "0",
            self.chain_id,
            "ETH",
            self.role_label_id,
            captial_wallet["private_key"],
            captial_account["address"],
            captial_balance,
        )
        if not captial_to_cex_transaction:
            print(
                f"captial account {captial_account['address']} withdraw to cex failed"
            )
            return False
        self.save_gas(
            GasType.CAPITAL_TO_CEX, captial_to_cex_transaction, self.group["name"]
        )
        return True

    """
    交易账户提现到资金账户
    """

    def trading_withdraw_to_captial(self, liquidity_user: LiquidityUser) -> bool:
        captial_account: Account = self.account_table.get(
            Query().role_id == liquidity_user["captial_role_id"]
        )
        trading_wallet = script_base.get_wallet(
            self.chain_id, liquidity_user["trading_role_id"]
        )
        trading_balance = SuccessRes[int](
            **eth_erc20.balance_of(self.chain_id, trading_wallet["address"])
        )["data"]
        if trading_balance == 0:
            return True
        trading_to_captial_transaction_response = eth_erc20.transfer(
            self.chain_id,
            trading_wallet["private_key"],
            captial_account["address"],
            trading_balance,
        )
        if trading_to_captial_transaction_response["code"] > 0:
            print(
                f"trading account {trading_wallet['address']} withdraw to captial account {captial_account['address']} failed, {trading_to_captial_transaction_response['message']}"
            )
            return False
        trading_to_captial_transaction = SuccessRes[dict](
            **trading_to_captial_transaction_response
        )["data"]
        self.save_gas(
            GasType.TRADING_TO_CAPITAL,
            trading_to_captial_transaction,
            self.group["name"],
        )
        return True

    """
    检查交易账户合约许可
    """

    def check_trading_account_contract_permission(
        self, liquidity_user: LiquidityUser
    ) -> bool:
        trading_account: Account = self.account_table.get(
            Query().role_id == liquidity_user["trading_role_id"]
        )
        trading_account_contract_permission = (
            self.trading_account_contract_permission_table.get(
                (Query().contract_address == self.group["contract_address"])
                & (Query().address == trading_account["address"])
            )
        )
        if not trading_account_contract_permission:
            trading_account_contract_permission = TradingAccountContractPermission(
                {
                    "contract_address": self.group["contract_address"],
                    "address": trading_account["address"],
                    "is_approved": False,
                    "is_delegated": False,
                }
            )
            doc_id = self.trading_account_contract_permission_table.insert(
                trading_account_contract_permission
            )
            trading_account_contract_permission = (
                self.trading_account_contract_permission_table.get(doc_id=doc_id)
            )
        if (
            not trading_account_contract_permission["is_approved"]
            or not trading_account_contract_permission["is_delegated"]
        ):
            transactions = SuccessRes[list[dict]](
                **eth_erc20.get_transactions(
                    self.chain_id, trading_account["address"], offset=100
                )
            )["data"]
            delegate_transaction = next(
                (
                    t
                    for t in transactions
                    if t["methodId"] == "0xc8318547"
                    and str(t["to"]).lower() == self.trading_contract_address
                ),
                None,
            )
            if delegate_transaction:
                trading_account_contract_permission["is_delegated"] = True
                self.save_gas(
                    GasType.LISTING_DELEGATE, delegate_transaction, self.group["name"]
                )

            approve_transaction = next(
                (
                    t
                    for t in transactions
                    if t["methodId"] == "0xa22cb465"
                    and str(t["to"]).lower() == self.group["contract_address"]
                ),
                None,
            )
            if approve_transaction:
                trading_account_contract_permission["is_approved"] = True
                self.save_gas(GasType.APPROVE, approve_transaction, self.group["name"])

            self.trading_account_contract_permission_table.update(
                trading_account_contract_permission,
                doc_ids=[trading_account_contract_permission.doc_id],
            )
        return (
            trading_account_contract_permission["is_approved"]
            and trading_account_contract_permission["is_delegated"]
        )

    """
    获取卖家
    """

    def get_seller(
        self,
    ) -> Tuple[Optional[LiquidityUser], Optional[NftAsset], Optional[NftSaleOrder]]:
        except_list = []
        while True:
            unchecked_list = [
                g for g in self.group_liquidity_user_list if g not in except_list
            ]
            if len(unchecked_list) == 0:
                return None, []
            group_liquidity_user = random.sample(unchecked_list, 1)[0]
            liquidity_user: LiquidityUser = self.liquidity_user_table.get(
                doc_id=group_liquidity_user["liquidity_user_id"]
            )
            token_id_list = self.get_token_id_list(
                liquidity_user, group_liquidity_user["contract_address"]
            )
            if len(token_id_list) > 0:
                for token_id in token_id_list:
                    nft_asset = next(
                        (n for n in self.nft_asset_list if n["token_id"] == token_id)
                    )
                    nft_web_sale_order = self.xmeta_api.get_sell_order(
                        nft_asset["product_id"]
                    )
                    if nft_web_sale_order:
                        nft_sale_order = self.nft_sale_order_table.get(
                            (Query().collection_id == nft_asset["collection_id"])
                            & (Query().product_id == nft_asset["product_id"])
                        )
                        if not nft_sale_order:
                            nft_sale_order = NftSaleOrder(
                                {
                                    "address": nft_web_sale_order["address"],
                                    "collection_id": nft_asset["collection_id"],
                                    "contract_address": self.group[
                                        "contract_address"
                                    ].lower(),
                                    "created_time": datetime.now().timestamp(),
                                    "has_deposit": False,
                                    "has_permission": False,
                                    "liquidity_user_id": liquidity_user.doc_id,
                                    "price": nft_web_sale_order["price"],
                                    "product_id": nft_web_sale_order["product_id"],
                                    "token_id": nft_asset["token_id"],
                                    "trading_account_role_id": liquidity_user[
                                        "trading_role_id"
                                    ],
                                }
                            )
                            self.nft_sale_order_table.insert(nft_sale_order)
                        return (liquidity_user, nft_asset, nft_sale_order)
                    return (liquidity_user, nft_asset, None)
            except_list.append(group_liquidity_user)

    """
    上架
    """

    def listing(self) -> NftSaleOrder:
        while True:
            try:
                print(f"Start to list a nft")
                liquidity_seller, nft_asset, nft_sale_order = self.get_seller()
                assert liquidity_seller, f"no seller for {self.group['name']}"
                assert nft_asset
                if nft_sale_order:
                    print(
                        f"Find nft sale order in double check, token id:{nft_sale_order['token_id']}"
                    )
                    return nft_sale_order

                print(
                    f"Get seller {liquidity_seller.doc_id}, token id {nft_asset['token_id']} found"
                )
                role = script_base.get_role_by_id(liquidity_seller["trading_role_id"])
                floor_price = float(
                    self.xmeta_api.get_floor_price(self.collection["collection_id"])
                )
                floor_price = round(random.uniform(floor_price, floor_price * 1.05), 4)
                user_parameter = sell_script.UserParameter(
                    {
                        "collection_name": self.collection["name"],
                        "env": "production",
                        "contract_address": self.group["contract_address"],
                        "floor_price": floor_price,
                        "token_id": nft_asset["token_id"],
                    }
                )
                has_permission = True
                deposit_result = 0
                if not self.check_trading_account_contract_permission(liquidity_seller):
                    has_permission = False
                    print(
                        f"trading account {liquidity_seller['trading_role_id']} has no permission to list"
                    )
                    deposit_result = self.deposit(
                        int(0.0002 * 10**18), liquidity_seller
                    )

                sell_script.run("0", role, user_parameter)

                nft_web_sell_order = self.xmeta_api.get_sell_order(
                    nft_asset["product_id"]
                )
                assert (
                    nft_web_sell_order
                ), f"no listed sell order for {nft_asset['product_id']}"

                trading_account: Account = self.account_table.get(
                    Query().role_id == liquidity_seller["trading_role_id"]
                )
                assert (
                    nft_web_sell_order["address"] == trading_account["address"]
                ), f"listed address {nft_web_sell_order['address']} is not equal to trading account {trading_account['address']}"
                assert self.check_trading_account_contract_permission(
                    liquidity_seller
                ), f"trading account {trading_account['address']} has no permission to list"
                if not nft_sale_order:
                    nft_sale_order = self.create_nft_sale_order(
                        liquidity_seller,
                        nft_web_sell_order,
                        has_permission,
                        deposit_result,
                    )
                print(
                    f"List success, token id {nft_asset['token_id']}, price {nft_web_sell_order['price']}"
                )
                return nft_sale_order
            except Exception as e:
                print(str(e))

    """
    下单
    """

    def place_order(self, nft_sale_order: NftSaleOrder) -> bool:
        try:
            print(f"Start to place order for token id {nft_sale_order['token_id']}")
            nft_asset = next(
                (
                    n
                    for n in self.nft_asset_list
                    if n["token_id"] == nft_sale_order["token_id"]
                )
            )
            nft_web_sell_order = self.xmeta_api.get_sell_order(nft_asset["product_id"])
            if not nft_web_sell_order:
                self.remove_nft_sale_order(nft_sale_order["token_id"])
                print(f"no listed sell order for {nft_asset['product_id']}")
                return False

            print(f"Check sell order {nft_web_sell_order['product_id']} vaild")
            liquidity_seller: LiquidityUser = self.liquidity_user_table.get(
                Query().trading_role_id == nft_sale_order["trading_account_role_id"]
            )
            seller_account: Account = self.account_table.get(
                Query().role_id == liquidity_seller["trading_role_id"]
            )
            group_liquidity_buyer = random.sample(
                [
                    g
                    for g in self.group_liquidity_user_list
                    if g["liquidity_user_id"] != liquidity_seller.doc_id
                ],
                1,
            )[0]
            liquidity_buyer: LiquidityUser = self.liquidity_user_table.get(
                doc_id=group_liquidity_buyer["liquidity_user_id"]
            )
            buyer_account: Account = self.account_table.get(
                Query().role_id == liquidity_buyer["trading_role_id"]
            )
            price = int(nft_web_sell_order["price"] * 10**18)

            self.deposit(price, liquidity_buyer)

            buyer_trading_account_nonce_before = SuccessRes[int](
                **eth_erc20.get_nonce(self.chain_id, buyer_account["address"])
            )["data"]
            buyer_role = script_base.get_role_by_id(liquidity_buyer["trading_role_id"])
            user_parameter = buy_script.UserParameter(
                {
                    "env": "production",
                    "contract_address": self.group["contract_address"],
                    "product_id": nft_web_sell_order["product_id"],
                    "seller_address": seller_account["address"],
                }
            )
            print("Start to run buy script")
            buy_script.run("0", buyer_role, user_parameter)
            print("Finish to run buy script, check order")
            buyer_trading_account_nonce_after = SuccessRes[int](
                **eth_erc20.get_nonce(self.chain_id, buyer_account["address"])
            )["data"]
            assert (
                buyer_trading_account_nonce_after > buyer_trading_account_nonce_before
            ), f"buyer {buyer_account['address']} place order failed, nonce not increased"

            buyer_token_id_list = self.get_token_id_list(
                liquidity_buyer, group_liquidity_buyer["contract_address"]
            )
            assert (
                nft_sale_order["token_id"] in buyer_token_id_list
            ), f"buyer {buyer_account['address']} place order failed, token id {nft_sale_order['token_id']} not in buyer token id list"

            buyer_transaction = SuccessRes[dict](
                **eth_erc20.get_latest_transaction(
                    self.chain_id, buyer_account["address"]
                )
            )["data"]

            self.save_gas(GasType.PLACE_ORDER, buyer_transaction, self.group["name"])
            self.remove_nft_sale_order(nft_sale_order["token_id"])
            print(
                f"Check order success, buyer id {liquidity_buyer['trading_role_id']} get token id {nft_sale_order['token_id']}"
            )
            if not self.trading_withdraw_to_captial(liquidity_seller):
                print(
                    f"trading account {liquidity_seller['trading_role_id']} withdraw to captial account failed"
                )
            return True
        except Exception as e:
            print(str(e))
            print(f"Place order failed.")
            return False

    """
    运行
    """

    def trade(self, group_name: str):
        self.load_group(group_name)
        while self.current_loop_count < self.group["loop_limit"]:
            print(
                f"Start run group {self.group['name']} round {self.current_loop_count}"
            )
            nft_sale_order = self.get_one_nft_sale_order()
            if not nft_sale_order:
                nft_sale_order = self.listing()
            if self.place_order(nft_sale_order):
                self.current_loop_count += 1
        self.withdraw_group()
        pass

    # def list_direct(self, group_name: str, nft_sale_orders: List[NftSaleOrder]):
    #     self.load_group(group_name)
    #     for nft_sale_order in nft_sale_orders:
    #         print(f"Start to list token id {nft_sale_order['token_id']}")
    #         liquidity_user: LiquidityUser = self.liquidity_user_table.get(
    #             doc_id=nft_sale_order["liquidity_user_id"]
    #         )
    #         nft_asset: NftAsset = self.nft_asset_table.get(
    #             (Query().collection_id == nft_sale_order["collection_id"])
    #             & (Query().token_id == nft_sale_order["token_id"])
    #         )
    #         self.listing(nft_sale_order, liquidity_user, nft_asset)
    #     pass

    """
    只挂单
    """

    def list_only(self, group_name: str, list_amount: int):
        self.load_group(group_name)
        current_list_count = 0
        while current_list_count < list_amount:
            print(f"Start to list round {current_list_count}")
            nft_sale_order = self.listing()
            if nft_sale_order:
                current_list_count += 1

        pass

    """
    计算gas花费
    """

    def calculate_gas_cost(self) -> float:
        gas_cost_total = 0
        gas_total = self.gas_table.search((Query().group_name == self.group["name"]))
        for gas in gas_total:
            gas_cost_total += gas["gas"]
        return float(gas_cost_total / 10**18)

    def get_gas_statistics(self, group_name: str, date: str) -> None:
        gas_list = self.gas_table.search(Query().group_name == group_name)
        with open(
            f"{self.database_path}/liquidity_{date}.csv", "w", newline=""
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file, fieldnames=["from", "to", "type", "value", "gas", "hash"]
            )
            writer.writeheader()
            for row in gas_list:
                value = 0
                if row["gas_type"] == GasType.PLACE_ORDER.value:
                    internal_transactions = sorted(
                        SuccessRes[list](
                            **eth_erc20.get_internal_transactions_by_hash(
                                self.chain_id, row["tx_hash"]
                            )
                        )["data"],
                        key=lambda x: int(x["value"]),
                        reverse=True,
                    )
                    internal_transaction = internal_transactions[0]
                    value = int(row["value"]) - int(internal_transaction["value"])
                data = {
                    "from": row["from_address"],
                    "to": row["to_address"],
                    "type": row["gas_type"],
                    "value": value / 10**18,
                    "gas": int(row["gas"]) / 10**18,
                    "hash": row["tx_hash"],
                }
                writer.writerow(data)
        pass

    def get_sale_orders(self, collection_id_list: List[int], order_count: int) -> None:
        orders: List[NftSaleOrder] = []
        for collection_id in collection_id_list:
            orders.extend(
                self.nft_sale_order_table.search(Query().collection_id == collection_id)
            )
        orders = sorted(orders, key=lambda x: x["created_time"], reverse=True)
        sale_orders = [
            {
                "address": o["address"],
                "token_id": o["token_id"],
                "collection_id": o["collection_id"],
            }
            for o in orders[:order_count]
        ]
        with open(
            f"{self.database_path}/daily_listing_0909.csv", "w", newline=""
        ) as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=sale_orders[0].keys())
            writer.writeheader()
            for row in sale_orders:
                writer.writerow(row)

    def withdraw_by_trading_address_list(
        self, group_name: str, trading_address_list: List[str]
    ):
        account_id_list = [
            a["role_id"]
            for a in self.account_table.all()
            if a["address"] in trading_address_list
        ]
        liquidity_user_list: List[LiquidityUser] = [
            l
            for l in self.liquidity_user_table.all()
            if l["trading_role_id"] in account_id_list
        ]
        for liquidity_user in liquidity_user_list:
            self.captial_withdraw_to_cex(liquidity_user)
        pass

    def no_token_liquidity_user_withdraw(
        self,
        token_id_list: Optional[List[int]] = None,
        order_count: Optional[int] = None,
    ) -> None:
        liquidity_users: List[LiquidityUser] = []
        orders: List[NftSaleOrder] = sorted(
            self.nft_sale_order_table.all(),
            key=lambda x: x["created_time"],
            reverse=True,
        )
        if token_id_list:
            orders = [o for o in orders if o["token_id"] in token_id_list]
        elif order_count:
            orders = orders[:order_count]
        for order in orders:
            liquidity_user = self.liquidity_user_table.get(
                doc_id=order["liquidity_user_id"]
            )
            if (
                len(self.get_token_id_list(liquidity_user, order["contract_address"]))
                == 0
            ):
                if (
                    next(
                        (
                            l
                            for l in liquidity_users
                            if l.doc_id == liquidity_user.doc_id
                        ),
                        None,
                    )
                    is None
                ):
                    liquidity_users.append(liquidity_user)
            else:
                print(f"User {liquidity_user.doc_id} has token")
        for liquidity_user in liquidity_users:
            if self.trading_withdraw_to_captial(liquidity_user):
                print(f"User {liquidity_user.doc_id} withdraw to captial success")
            else:
                print(f"User {liquidity_user.doc_id} withdraw to captial failed")
            if self.captial_withdraw_to_cex(liquidity_user):
                print(f"User {liquidity_user.doc_id} withdraw to cex success")
            else:
                print(f"User {liquidity_user.doc_id} withdraw to cex failed")
        pass

    def sale_order_statistics(
        self,
        collection_id: int,
        date: str,
        token_id_list: Optional[List[int]] = None,
        order_count: Optional[int] = None,
    ):
        orders = sorted(
            self.nft_sale_order_table.search(Query().collection_id == collection_id),
            key=lambda x: x["created_time"],
            reverse=True,
        )
        sale_order_statistics_list = []
        if token_id_list:
            orders: List[NftSaleOrder] = [
                o for o in orders if o["token_id"] in token_id_list
            ]
        elif order_count:
            orders = orders[:order_count]
        order_dict = {}
        for order in orders:
            if order["address"] not in order_dict:
                order_dict[order["address"]] = []
            order_dict[order["address"]].append(order)

        for key in order_dict:
            wallet_assets_statistics = SuccessRes[list](
                **eth_erc20.get_wallet_assets_statistics(self.chain_id, key)
            )["data"]
            for transaction in wallet_assets_statistics["transactions"]:
                if not order_dict[key][0]["has_permission"]:
                    if transaction["methodId"] == "0xc8318547":
                        sale_order_statistics_list.append(
                            {
                                "address": key,
                                "collection_id": collection_id,
                                "token_id": 0,
                                "type": "listing_delegate",
                                "value": -float(
                                    int(transaction["gasUsed"])
                                    * int(transaction["gasPrice"])
                                    / 10**18
                                ),
                                "hash": transaction["hash"],
                            }
                        )
                    if transaction["methodId"] == "0xa22cb465":
                        sale_order_statistics_list.append(
                            {
                                "address": key,
                                "collection_id": collection_id,
                                "token_id": 0,
                                "type": "approve",
                                "value": -float(
                                    int(transaction["gasUsed"])
                                    * int(transaction["gasPrice"])
                                    / 10**18
                                ),
                                "hash": transaction["hash"],
                            }
                        )
                    if order_dict[key][0]["has_deposit"] > 0:
                        from_address = transaction["from"].lower()
                        if transaction["to"].lower() == key:
                            sale_order_statistics_list.append(
                                {
                                    "address": key,
                                    "collection_id": collection_id,
                                    "token_id": 0,
                                    "type": "captial_to_trading",
                                    "value": -float(
                                        int(transaction["gasUsed"])
                                        * int(transaction["gasPrice"])
                                        / 10**18
                                    ),
                                    "hash": transaction["hash"],
                                }
                            )
                        if order_dict[key][0]["has_deposit"] == 2:
                            from_address_last_transaction = SuccessRes[dict](
                                **eth_erc20.get_latest_transaction(
                                    self.chain_id, from_address
                                )
                            )["data"]
                            if (
                                from_address_last_transaction["to"].lower() == key
                                and int(transaction["blockNumber"])
                                - int(from_address_last_transaction["blockNumber"])
                                > 0
                                and int(transaction["blockNumber"])
                                - int(from_address_last_transaction["blockNumber"])
                                < 600
                            ):
                                sale_order_statistics_list.append(
                                    {
                                        "address": key,
                                        "collection_id": collection_id,
                                        "token_id": 0,
                                        "type": "cex_to_captial",
                                        "value": -0.0001,
                                        "hash": from_address_last_transaction["hash"],
                                    }
                                )

            internal_transactions = sorted(
                wallet_assets_statistics["internal_transactions"],
                key=lambda x: x["blockNumber"],
                reverse=True,
            )[: len(order_dict[key])]
            for i in range(len(internal_transactions)):
                if internal_transactions[i]["to"] == key:
                    sale_order_statistics_list.append(
                        {
                            "address": key,
                            "collection_id": collection_id,
                            "token_id": order_dict[key][i]["token_id"],
                            "type": "listing_selled",
                            "value": float(
                                int(internal_transactions[i]["value"]) / 10**18
                            ),
                            "hash": internal_transactions[i]["hash"],
                        }
                    )
            sale_order_statistics_list.append(
                {
                    "address": key,
                    "collection_id": collection_id,
                    "token_id": 0,
                    "type": "trading_to_captial",
                    "value": -0.00005,
                    "hash": "",
                }
            )
            sale_order_statistics_list.append(
                {
                    "address": key,
                    "collection_id": collection_id,
                    "token_id": 0,
                    "type": "captial_to_cex",
                    "value": -0.00005,
                    "hash": "",
                }
            )
        with open(
            f"{self.database_path}/daily_listing_statistics_{date}.csv", "w", newline=""
        ) as csv_file:
            writer = csv.DictWriter(
                csv_file, fieldnames=sale_order_statistics_list[0].keys()
            )
            writer.writeheader()
            for row in sale_order_statistics_list:
                writer.writerow(row)

    def get_token_statistics_by_contract_address(
        self, contract_address: str, date: str
    ):
        data: List[dict] = []
        liquidity_users = self.liquidity_user_table.all()
        for liquidity_user in liquidity_users:
            account = self.account_table.get(
                Query().role_id == liquidity_user["trading_role_id"]
            )
            tokens = self.get_token_id_list(liquidity_user, contract_address.lower())
            if len(tokens) == 0:
                print(f"no token for {account['address']}")
                continue
            else:
                for token in tokens:
                    print(f"get token {token} for {account['address']}")
                    data.append(
                        {
                            "address": account["address"],
                            "token_id": token,
                        }
                    )

        with open(
            f"{self.database_path}/{date}_token_statistics_{contract_address}.csv",
            "w",
            newline="",
        ) as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            writer.writeheader()
            for row in data:
                writer.writerow(row)
        pass

    def group_transfer_token(
        self, group_name: str, contract_address: str, target: Dict[str, int]
    ) -> List[str]:
        self.load_group(group_name)
        skip_list: List[int] = []
        used_address_list: List[str] = []
        for key in list(target.keys()):
            for _ in range(target[key]):
                skip_list, used_address_list = self.transfer_token(
                    contract_address, skip_list, key, used_address_list
                )
        return used_address_list

    def transfer_token(
        self,
        contract_address: str,
        skip_list: List[int],
        target_address: str,
        used_address_list: List[str],
    ) -> Tuple[List[int], List[str]]:
        liquidity_users: List[LiquidityUser] = [
            l for l in self.liquidity_user_table.all() if l.doc_id not in skip_list
        ]

        for liquidity_user in liquidity_users:
            tokens = self.get_token_id_list(liquidity_user, contract_address)
            if len(tokens) == 0:
                skip_list.append(liquidity_user.doc_id)
                print(f"liquidity user {liquidity_user.doc_id} has no token")
                continue
            print(f"liquidity user has {len(tokens)} tokens")
            trading_account: Account = self.account_table.get(
                Query().role_id == liquidity_user["trading_role_id"]
            )
            used_address_list.append(trading_account["address"])
            wallet = script_base.get_wallet(self.chain_id, trading_account["role_id"])
            assert wallet
            self.deposit(0.0001 * 10**18, liquidity_user)
            transaction = SuccessRes[dict](
                **eth_erc721.safe_transfer_from(
                    self.chain_id,
                    contract_address,
                    wallet["private_key"],
                    wallet["address"],
                    target_address,
                    tokens[0],
                )
            )["data"]
            self.save_gas(GasType.TRANSFER_TO_OWNER, transaction, self.group["name"])
            print(
                f"liquidity_user {liquidity_user.doc_id} transfer token id {tokens[0]} to {target_address}"
            )
            return skip_list, list(set(used_address_list))
