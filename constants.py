import os
from dataclasses import dataclass
from typing import Dict

NATIVE_TOKEN_ADDRESS = "0xEeeeeEeeeEeEeeEeEeEeeEEEeeeeEeeeeeeeEEeE"


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


# Network: chain_id mapping
@dataclass(frozen=True)
class Network:
    chain_id: int
    multicall_address: str
    rpc_url: str = ""  # Add this field for custom RPC URLs


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
    "kava": Network(2222, "0x30A62aA52Fa099C4B227869EB6aeaDEda054d121"),
    "moonbeam": Network(1284, "0x0769fd68dFb93167989C6f7254cd0D766Fb2841F"),
    "bsc": Network(56, "0x1Ee38d535d541c55C9dae27B12edf090C608E6Fb"),
    "fraxtal": Network(252, "0xcA11bde05977b3631167028862bE2a173976CA11"),
    "mantle": Network(5000, "0xcA11bde05977b3631167028862bE2a173976CA11"),
    "aurora": Network(1313161554, "0xcA11bde05977b3631167028862bE2a173976CA11"),
    "x-layer": Network(1261120, "0x0769fd68dFb93167989C6f7254cd0D766Fb2841F", "https://xlayerrpc.okx.com"),
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
