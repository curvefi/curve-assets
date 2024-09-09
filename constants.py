import os

# ABI for ERC20 token
ERC20_ABI = [
    {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "type": "function",
    },
]

# RPC endpoint format
DRPC_URL = "https://lb.drpc.org/ogrpc?network=%s&dkey=%s"
DRPC_KEY = os.environ.get("DRPC_KEY")

# Multicall contract addresses for different networks
MULTICALL_ADDRESSES = {
    "ethereum": "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696",
    "polygon": "0x275617327c958bD06b5D6b871E7f491D76113dd8",
    # Add more networks as needed
}

# Network: chain_id mapping
NETWORKS = {
    "ethereum": 1,
    "polygon": 137,
    "arbitrum": 42161,
    "optimism": 10,
    "base": 8453,
    "gnosis": 100,
    "avalanche": 43114,
    "fantom": 250,
    "celo": 42220,
    "kava": 2222,
}

# Multicall ABI
MULTICALL_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {"internalType": "address", "name": "target", "type": "address"},
                    {"internalType": "bytes", "name": "callData", "type": "bytes"},
                ],
                "internalType": "struct Multicall2.Call[]",
                "name": "calls",
                "type": "tuple[]",
            }
        ],
        "name": "aggregate",
        "outputs": [
            {"internalType": "uint256", "name": "blockNumber", "type": "uint256"},
            {"internalType": "bytes[]", "name": "returnData", "type": "bytes[]"},
        ],
        "stateMutability": "nonpayable",
        "type": "function",
    }
]
