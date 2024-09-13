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


@dataclass(frozen=True)
class Network:
    chain_id: int
    multicall_address: str
    rpc_url: str = ""
    folder_name: str = ""  # New field for the folder name


MULTICALL_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"

NETWORKS: Dict[str, Network] = {
    "ethereum": Network(1, MULTICALL_ADDRESS, folder_name="assets"),
    "polygon": Network(137, MULTICALL_ADDRESS, folder_name="assets-polygon"),
    "arbitrum": Network(42161, MULTICALL_ADDRESS, folder_name="assets-arbitrum"),
    "optimism": Network(10, MULTICALL_ADDRESS, folder_name="assets-optimism"),
    "base": Network(8453, MULTICALL_ADDRESS, folder_name="assets-base"),
    "gnosis": Network(100, MULTICALL_ADDRESS, folder_name="assets-xdai"),
    "avalanche": Network(43114, MULTICALL_ADDRESS, folder_name="assets-avalanche"),
    "fantom": Network(250, MULTICALL_ADDRESS, folder_name="assets-fantom"),
    "celo": Network(42220, MULTICALL_ADDRESS, folder_name="assets-celo"),
    "kava": Network(2222, MULTICALL_ADDRESS, folder_name="assets-kava"),
    "moonbeam": Network(1284, MULTICALL_ADDRESS, folder_name="assets-moonbeam"),
    "bsc": Network(56, MULTICALL_ADDRESS, folder_name="assets-bsc"),
    "fraxtal": Network(252, MULTICALL_ADDRESS, folder_name="assets-fraxtal"),
    "mantle": Network(5000, MULTICALL_ADDRESS, folder_name="assets-mantle"),
    "aurora": Network(1313161554, MULTICALL_ADDRESS, folder_name="assets-aurora"),
    "x-layer": Network(196, MULTICALL_ADDRESS, "https://xlayerrpc.okx.com", folder_name="assets-x-layer"),
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

# Constants for logo URIs
JSDELIVR_BASE_URL = "https://cdn.jsdelivr.net/gh/curvefi/curve-assets"
TOKENLIST_LOGO_URI = f"{JSDELIVR_BASE_URL}/branding/logo.png"
