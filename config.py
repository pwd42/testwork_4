import json

L2PASS_CONTRACTS = {
    "Arbitrum": "0x0000049F63Ef0D60aBE49fdD8BEbfa5a68822222",
    "Optimism": "0x0000049F63Ef0D60aBE49fdD8BEbfa5a68822222",
    "Base": "0x0000049F63Ef0D60aBE49fdD8BEbfa5a68822222"
}

RPC_URLS = {
    "Arbitrum": "https://endpoints.omniatech.io/v1/arbitrum/one/public",
    "Optimism": "https://op-pokt.nodies.app",
    "Base": "https://base-pokt.nodies.app"
}

EXPLORERS_URL = {
    "Arbitrum": "https://arbiscan.io/",
    "Optimism": "https://optimistic.etherscan.io/",
    "Base": "https://basescan.org/"
}

# ABI общее для всех сетей
with open('L2_PASS_ABI.json') as file:
    L2_PASS_ABI = json.load(file)
