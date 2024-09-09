import os
from dataclasses import dataclass
from typing import Dict

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
    "arbitrum": "0x842eC2c7D803033Edf55E478F461FC547Bc54EB2",
    "optimism": "0x2DC0E2aa608532Da689e89e237dF582B783E552C",
    "base": "0x091e99cb1C49331a94dD62755D168E941AbD0693",
    "gnosis": "0xcA11bde05977b3631167028862bE2a173976CA11",
    "avalanche": "0xcA11bde05977b3631167028862bE2a173976CA11",
    "fantom": "0xcA11bde05977b3631167028862bE2a173976CA11",
    "celo": "0xcA11bde05977b3631167028862bE2a173976CA11",
    "kava": "0x4E075eA4Cf2cB39Db4d67e2F9dA09f5E5dF3f9D9",
}


# Network: chain_id mapping
@dataclass(frozen=True)
class Network:
    chain_id: int
    multicall_address: str


NETWORKS: Dict[str, Network] = {
    "ethereum": Network(1, "0x5BA1e12693Dc8F9c48aAD8770482f4739bEeD696"),
    "polygon": Network(137, "0x275617327c958bD06b5D6b871E7f491D76113dd8"),
    "arbitrum": Network(42161, "0x842eC2c7D803033Edf55E478F461FC547Bc54EB2"),
    "optimism": Network(10, "0x2DC0E2aa608532Da689e89e237dF582B783E552C"),
    "base": Network(8453, "0x091e99cb1C49331a94dD62755D168E941AbD0693"),
    "gnosis": Network(100, "0xcA11bde05977b3631167028862bE2a173976CA11"),
    "avalanche": Network(43114, "0xcA11bde05977b3631167028862bE2a173976CA11"),
    "fantom": Network(250, "0xcA11bde05977b3631167028862bE2a173976CA11"),
    "celo": Network(42220, "0xcA11bde05977b3631167028862bE2a173976CA11"),
    "kava": Network(2222, "0x4E075eA4Cf2cB39Db4d67e2F9dA09f5E5dF3f9D9"),
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
