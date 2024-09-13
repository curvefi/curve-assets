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
    folder_name: str = ""
    native_token_name: str = ""
    native_token_symbol: str = ""


MULTICALL_ADDRESS = "0xcA11bde05977b3631167028862bE2a173976CA11"

NETWORKS: Dict[str, Network] = {
    "ethereum": Network(
        1, MULTICALL_ADDRESS, folder_name="assets", native_token_name="Ether", native_token_symbol="ETH"
    ),
    "polygon": Network(
        137, MULTICALL_ADDRESS, folder_name="assets-polygon", native_token_name="Polygon", native_token_symbol="POL"
    ),
    "arbitrum": Network(
        42161, MULTICALL_ADDRESS, folder_name="assets-arbitrum", native_token_name="Ether", native_token_symbol="ETH"
    ),
    "optimism": Network(
        10, MULTICALL_ADDRESS, folder_name="assets-optimism", native_token_name="Ether", native_token_symbol="ETH"
    ),
    "base": Network(
        8453, MULTICALL_ADDRESS, folder_name="assets-base", native_token_name="Ether", native_token_symbol="ETH"
    ),
    "gnosis": Network(
        100, MULTICALL_ADDRESS, folder_name="assets-xdai", native_token_name="xDai", native_token_symbol="XDAI"
    ),
    "avalanche": Network(
        43114,
        MULTICALL_ADDRESS,
        folder_name="assets-avalanche",
        native_token_name="Avalanche",
        native_token_symbol="AVAX",
    ),
    "fantom": Network(
        250, MULTICALL_ADDRESS, folder_name="assets-fantom", native_token_name="Fantom", native_token_symbol="FTM"
    ),
    "celo": Network(
        42220, MULTICALL_ADDRESS, folder_name="assets-celo", native_token_name="Celo", native_token_symbol="CELO"
    ),
    "kava": Network(
        2222, MULTICALL_ADDRESS, folder_name="assets-kava", native_token_name="Kava", native_token_symbol="KAVA"
    ),
    "moonbeam": Network(
        1284, MULTICALL_ADDRESS, folder_name="assets-moonbeam", native_token_name="Moonbeam", native_token_symbol="GLMR"
    ),
    "bsc": Network(
        56, MULTICALL_ADDRESS, folder_name="assets-bsc", native_token_name="Build and Build", native_token_symbol="BNB"
    ),
    "fraxtal": Network(
        252,
        MULTICALL_ADDRESS,
        folder_name="assets-fraxtal",
        native_token_name="Frax Ether",
        native_token_symbol="frxETH",
    ),
    "mantle": Network(
        5000, MULTICALL_ADDRESS, folder_name="assets-mantle", native_token_name="Mantle", native_token_symbol="MNT"
    ),
    "aurora": Network(
        1313161554, MULTICALL_ADDRESS, folder_name="assets-aurora", native_token_name="Ether", native_token_symbol="ETH"
    ),
    "x-layer": Network(
        196,
        MULTICALL_ADDRESS,
        "https://xlayerrpc.okx.com",
        folder_name="assets-x-layer",
        native_token_name="OKB",
        native_token_symbol="OKB",
    ),
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


def get_native_token_info(network: Network):
    """Return native token information for a given network."""
    return {
        "chainId": network.chain_id,
        "address": NATIVE_TOKEN_ADDRESS.lower(),  # Ensure the address is lowercase
        "name": network.native_token_name,
        "symbol": network.native_token_symbol,
        "decimals": 18,
        "logoURI": f"{JSDELIVR_BASE_URL}/{network.folder_name}/{NATIVE_TOKEN_ADDRESS.lower()}.png",
    }
