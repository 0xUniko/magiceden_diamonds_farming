import os

config = {
    "client": {
        "script_store_directory": "tasks",
        "wallet_provider": "network",
        "fingerprint_provider": "default",
        "proxy_provider": "Local",
    },
    "thread_delay": 60,
    "fingerprint_service_url_base": "http://localhost:5001",
    "fingerprint_proxy": {
        "protocol": "http",
        "host": "127.0.0.1",
        "port": 7890,
        "userName": None,
        "password": None,
    },
    "api": {
        "local": {
            "fingerprint": {
                "default": {"port": 5001},
                "adspower": {"port": 50325, "application_id": 3857},
                "hubstudio": {
                    "port": 6873,
                    "login": "/login",
                    "start": "/api/v1/browser/start",
                    "status": "/api/v1/browser/all-browser-status",
                    "stop": "/api/v1/browser/stop",
                    "create": "/api/v1/env/create",
                    "delete": "/api/v1/env/del",
                    "list": "/api/v1/env/list",
                    "update_proxy": "/api/v1/env/proxy/update",
                },
            },
            "wallet": {
                "port": 5000,
                "get_by_id": "/Bank/GetWalletById",
                "get_by_role_id": "/Bank/GetWalletByRoleId",
            },
            "web3": {
                "host": "https://web3-api.fanershe.cn",
                "port": 443,
                "starknet": {
                    "wallet_deploy": "/starknet/wallet_deploy",
                    "wallet_generate": "/starknet/wallet_generate",
                    "get_nonce": "/starknet/get_nonce",
                    "get_token_balance": "/starknet/get_token_balance",
                    "get_latest_transaction": "/starknet/get_latest_transaction",
                    "invoke": "/starknet/invoke",
                    "call": "/starknet/call",
                    "multicall": "/starknet/multicall",
                    "multi_raw_call": "/starknet/multi_raw_call",
                },
                "eth_defi": {
                    "swap": "/eth/defi/swap",
                    "get_token_list": "/eth/defi/get_token_list",
                },
                "eth": {
                    "send_transaction": "/eth/send_transaction",
                    "send_raw_transaction": "/eth/send_raw_transaction",
                    "get_erc721_transfer_events": "/eth/get_erc721_transfer_events",
                    "get_gas_price": "/eth/get_gas_price",
                    "get_token_balance": "/eth/get_token_balance",
                    "get_transactions": "/eth/get_transactions",
                    "get_latest_transaction": "/eth/get_latest_transaction",
                    "get_nonce": "/eth/get_nonce",
                    "send_raw_transaction_with_data": "/eth/send_raw_transaction_with_data",
                },
                "eth_erc721": {
                    "balance_of": "/eth/erc721/balance_of",
                    "token_of_owner_by_index": "/eth/erc721/token_of_owner_by_index",
                    "owner_of": "/eth/erc721/owner_of",
                    "get_transfer_events": "/eth/erc721/get_transfer_events",
                    "safe_transfer_from": "/eth/erc721/safe_transfer_from",
                    "set_approval_for_all": "/eth/erc721/set_approval_for_all",
                    "safe_mint": "/eth/erc721/safe_mint",
                },
                "eth_erc20": {
                    "send_transaction": "/eth/erc20/send_transaction",
                    "build_transaction": "/eth/erc20/build_transaction",
                    "send_raw_transaction": "/eth/erc20/send_raw_transaction",
                    "get_gas_price": "/eth/erc20/get_gas_price",
                    "get_transactions": "/eth/erc20/get_transactions",
                    "get_latest_transaction": "/eth/erc20/get_latest_transaction",
                    "get_nonce": "/eth/erc20/get_nonce",
                    "send_raw_transaction_with_data": "/eth/erc20/send_raw_transaction_with_data",
                    "transfer": "/eth/erc20/transfer",
                    "balance_of": "/eth/erc20/balance_of",
                    "get_transaction_by_hash": "/eth/erc20/get_transaction_by_hash",
                    "get_wallet_assets_statistics": "/eth/erc20/get_wallet_assets_statistics",
                    "get_internal_transactions_by_hash": "/eth/erc20/get_internal_transactions_by_hash",
                    "signature": "/eth/erc20/signature",
                    "call_function": "/eth/erc20/call_function",
                    "signature_text": "/eth/erc20/signature_text",
                    "to_checksum_address": "/eth/erc20/to_checksum_address",
                    "raw_call": "/eth/erc20/raw_call",
                },
                "solana": {
                    "get_spl_balance": "/solana/get_spl_balance",
                    "get_pub_key_from_mnemonic": "/solana/get_pub_key_from_mnemonic",
                    "get_balance": "/solana/get_balance",
                },
            },
            "host": "http://127.0.0.1",
        },
        "network": {
            "script_workspace": {"download_script": "/", "download_requirements": "/"},
            "script": {"get_by_id": "/script-api/script/get_by_id"},
            "wallet": {
                "get_by_id": "/wallet-api/wallet/get_by_id",
                "create": "/wallet-api//wallet/create",
            },
            "host": "http://api.fanershe.cn",
        },
        "remote": {
            "flow": {
                "flow": {
                    "get_one_wait_task": "/flow-api/flow/get_one_wait_task",
                    "complete_task": "/flow-api/flow/complete_task",
                    "create_task_log": "/flow-api/flow/create_task_log",
                    "get_task_message": "/flow-api/flow/get_task_message",
                    "get_task_list": "/flow-api/flow/get_task_list",
                    "task_message": "/flow-api/flow/task_message",
                    "create_flow": "/flow-api/flow/create_flow",
                    "delete_flow": "/flow-api/flow/delete_flow",
                    "save_task_biz_status": "/flow-api/flow/save_task_biz_status",
                }
            },
            "rpg": {
                "role": {
                    "batch_create_empty_role": "/rpg-api/role/batch_create_empty_role",
                    "empty_role_bind_resource": "/rpg-api/role/empty_role_bind_resource",
                    "modify_extend_information": "/rpg-api/role/modify_extend_information",
                    "get_empty_role_list": "/rpg-api/role/get_empty_role_list",
                    "get_role_list": "/rpg-api/role/get_role_list",
                    "get_role_by_id": "/rpg-api/role/get_role_by_id",
                }
            },
            "resource": {
                "sms": {
                    "get_number": "/resource-api/sms/get_number",
                    "release_number": "/resource-api/sms/release_number",
                    "get_code": "/resource-api/sms/get_code",
                },
                "fingerprint": {
                    "get_by_fingerprint_name": "/resource-api/fingerprint/get_by_fingerprint_name",
                    "modify_browser_id": "/resource-api/fingerprint/modify_browser_id",
                },
                "fingerprint_browser": {
                    "get_key_list": "/resource-api/fingerprint_browser/get_key_list"
                },
                "proxy": {"take_line": "/resource-api/proxy/take_line"},
                "discord": {"add": "/resource-api/discord/add"},
                "twitter": {"add": "/resource-api/twitter/add"},
                "email": {"add": "/resource-api/email/add"},
                "aigc": {
                    "ask": "/resource-api/aigc/ask",
                    "extract_verification_code": "/resource-api/aigc/extract_verification_code",
                    "image": "/resource-api/aigc/image",
                },
                "exchange": {
                    "get_one_recharge_address": "/resource-api/exchange/get_one_recharge_address",
                    "recharge_complete": "/resource-api/exchange/recharge_complete",
                    "withdraw": "/resource-api/exchange/withdraw",
                    "get_withdraw_by_id": "/resource-api/exchange/get_withdraw_by_id",
                    "get_balance": "/resource-api/exchange/get_balance",
                },
                "wallet": {
                    "save_wallet_address_chain": "/resource-api/wallet/save_wallet_address_chain",
                    "batch_import": "/resource-api/wallet/batch_import",
                    "wallet_append_wallet_address": "/resource-api/wallet/wallet_append_wallet_address",
                    "save_extend_information": "/resource-api/wallet/modify_wallet_address_extend_information",
                },
                "resource": {
                    "save_extend_information": "/resource-api/resource/save_extend_information",
                    "hubstudio_api_passport": "/resource-api/resource/hubstudio_api_passport",
                    "assets_update_asset": "/resource-api/resource/assets_update_asset",
                },
                "broker": {
                    "get_one_recharge_address": "/resource-api/broker/get_one_recharge_address",
                    "recharge_complete": "/resource-api/broker/recharge_complete",
                    "withdraw": "/resource-api/broker/withdraw",
                    "get_withdraw_by_id": "/resource-api/broker/get_withdraw_by_id",
                    "get_balance": "/resource-api/broker/get_balance",
                },
            },
            "web3": {
                "starknet": {
                    "wallet_deploy": "/starknet/wallet_deploy",
                    "wallet_generate": "/starknet/wallet_generate",
                    "get_nonce": "/starknet/get_nonce",
                    "get_token_balance": "/starknet/get_token_balance",
                    "get_latest_transaction": "/starknet/get_latest_transaction",
                    "invoke": "/starknet/invoke",
                    "call": "/starknet/call",
                    "multicall": "/starknet/multicall",
                    "multi_raw_call": "/starknet/multi_raw_call",
                },
                "eth_defi": {
                    "swap": "/eth/defi/swap",
                    "get_token_list": "/eth/defi/get_token_list",
                },
                "eth": {
                    "send_transaction": "/eth/send_transaction",
                    "send_raw_transaction": "/eth/send_raw_transaction",
                    "get_erc721_transfer_events": "/eth/get_erc721_transfer_events",
                    "get_gas_price": "/eth/get_gas_price",
                    "get_token_balance": "/eth/get_token_balance",
                    "get_transactions": "/eth/get_transactions",
                    "get_latest_transaction": "/eth/get_latest_transaction",
                    "get_nonce": "/eth/get_nonce",
                    "send_raw_transaction_with_data": "/eth/send_raw_transaction_with_data",
                },
                "eth_erc721": {
                    "balance_of": "/eth/erc721/balance_of",
                    "token_of_owner_by_index": "/eth/erc721/token_of_owner_by_index",
                    "owner_of": "/eth/erc721/owner_of",
                    "get_transfer_events": "/eth/erc721/get_transfer_events",
                    "safe_transfer_from": "/eth/erc721/safe_transfer_from",
                    "set_approval_for_all": "/eth/erc721/set_approval_for_all",
                    "safe_mint": "/eth/erc721/safe_mint",
                },
                "eth_erc20": {
                    "send_transaction": "/eth/erc20/send_transaction",
                    "send_raw_transaction": "/eth/erc20/send_raw_transaction",
                    "get_gas_price": "/eth/erc20/get_gas_price",
                    "get_transactions": "/eth/erc20/get_transactions",
                    "get_latest_transaction": "/eth/erc20/get_latest_transaction",
                    "get_nonce": "/eth/erc20/get_nonce",
                    "send_raw_transaction_with_data": "/eth/erc20/send_raw_transaction_with_data",
                    "transfer": "/eth/erc20/transfer",
                    "balance_of": "/eth/erc20/balance_of",
                    "get_transaction_by_hash": "/eth/erc20/get_transaction_by_hash",
                    "get_wallet_assets_statistics": "/eth/erc20/get_wallet_assets_statistics",
                    "get_internal_transactions_by_hash": "/eth/erc20/get_internal_transactions_by_hash",
                    "signature": "/eth/erc20/signature",
                },
            },
            "host": "http://api.fanershe.cn",
        },
        "user_flow_token": "user_flow_token",
    },
    "contract": {
        "starknet": {
            "eth": "0x049d36570d4e46f48e99674bd3fcc84644ddd6b96f7c741b1562b82f9e004dc7",
            "usdc": "0x053c91253bc9682c04929ca02ed00b3e423f6710d2ee7e0d5ebb06f3ecf368a8",
        }
    },
    "rpc_endpoint": {
        "mainnet": "https://eth-mainnet.g.alchemy.com/v2/N8MPLAIZ9XFia6IsYdIaHB_yttsBAzVC",
        "zksync_era": "https://mainnet.era.zksync.io",
        "starknet": "https://starknet-mainnet.g.alchemy.com/v2/MU3Gye7KNwfqZTEQCmR2jrgmQYLIJl_D",
        "arbitrum": "https://arbitrum.llamarpc.com",
    },
    "eth_endpoint": {
        "eth-erc20": "https://eth-mainnet.g.alchemy.com/v2/N8MPLAIZ9XFia6IsYdIaHB_yttsBAzVC",
        "eth-zks": "https://mainnet.era.zksync.io",
        "eth-arb": "https://arbitrum.llamarpc.com",
    },
    "block_explorer": {
        "eth-erc20": "https://api.etherscan.io/api?apikey=UV8G1TBMHR7CNQRGMESYPT81D7FJP6RZ6Q"
    },
    "explorer_api_keys": {
        "eth-erc20": "G88JSC46FCSJPDF2YB9NTRWPXBN7TQHIUS",
        "eth-arb": "Z6RU3UH1639ZMH3VZUIPPFYEIJ9G912C1B",
        "eth-op": "M6KHJWG7U4P8IYQTD4SYVM4P3VY2XHVD7G",
    },
    "chain_params": {
        "eth-erc20": {
            "chainId": "0x1",
            "chainName": "Ethereum Mainnet",
            "rpcUrls": ["https://mainnet.infura.io/v3/"],
            "nativeCurrency": {"name": "Ether", "symbol": "ETH", "decimals": 18},
            "blockExplorerUrls": ["https://etherscan.io"],
        },
        "eth-zks": {
            "chainId": "0x144",
            "chainName": "zkSync Era Mainnet",
            "rpcUrls": ["https://mainnet.era.zksync.io"],
            "nativeCurrency": {"name": "Ether", "symbol": "ETH", "decimals": 18},
            "blockExplorerUrls": ["https://explorer.zksync.io"],
        },
        "eth-arb": {
            "chainId": "0xa4b1",
            "chainName": "Arbitrum One",
            "rpcUrls": ["https://arb1.arbitrum.io/rpc"],
            "nativeCurrency": {"name": "Ether", "symbol": "ETH", "decimals": 18},
            "blockExplorerUrls": ["https://arbiscan.io"],
        },
        "eth-op": {
            "chainId": "0xa",
            "chainName": "OP Mainnet",
            "rpcUrls": ["https://mainnet.optimism.io"],
            "nativeCurrency": {"name": "Ether", "symbol": "ETH", "decimals": 18},
            "blockExplorerUrls": ["https://optimistic.etherscan.io"],
        },
        "matic-polygon": {
            "chainId": "0x89",
            "chainName": "OP Mainnet",
            "rpcUrls": ["https://rpc-mainnet.maticvigil.com"],
            "nativeCurrency": {
                "name": "MATIC Token",
                "symbol": "MATIC",
                "decimals": 18,
            },
            "blockExplorerUrls": ["https://polygonscan.com"],
        },
        "bnb": {
            "chainId": "0x38",
            "chainName": "BNB Chain",
            "rpcUrls": ["https://bsc-dataseed.bnbchain.org"],
            "nativeCurrency": {"name": "BNB", "symbol": "BNB", "decimals": 18},
            "blockExplorerUrls": ["https://bscscan.com"],
        },
    },
    "okx_dev_key": {
        "apiKey": "b179f6f2-6c61-4c49-a899-ecdf33423a9e",
        "secretKey": "A58B02470E1F56B57ADA0ADD9E15761E",
        "passphrase": "maskP@ssw0rd",
    },
}


def get_account_org_id(api_config: dict) -> str:
    org_path = "org.txt"
    if os.path.exists(org_path):
        with open(org_path, "r", encoding="UTF-8") as f:
            account_org_id = f.read().replace("\n", "")
    return account_org_id
