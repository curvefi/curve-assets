import logging

import requests
from eth_abi import decode
from rich.logging import RichHandler
from web3 import Web3

from constants import ERC20_ABI, MULTICALL_ABI, NETWORKS

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger("rich")


def multicall(w3: Web3, calls: list, block_identifier: int = "latest", batch_size: int = 1000):
    network = next((net for net in NETWORKS.values() if net.chain_id == w3.eth.chain_id), None)
    if not network:
        raise ValueError(f"Unsupported chain ID: {w3.eth.chain_id}")

    multicall_contract = w3.eth.contract(address=network.multicall_address, abi=MULTICALL_ABI)

    all_decoded_results = []
    for i in range(0, len(calls), batch_size):
        batch_calls = calls[i: i + batch_size]

        aggregate_calls = []
        for call in batch_calls:
            contract, fn_name, args = call
            call_data = contract.encodeABI(fn_name=fn_name, args=args)
            aggregate_calls.append((contract.address, call_data))

        result = multicall_contract.functions.aggregate(aggregate_calls).call(block_identifier=block_identifier)

        for j, call in enumerate(batch_calls):
            contract, fn_name, _ = call
            function = contract.get_function_by_name(fn_name)
            output_types = [output["type"] for output in function.abi["outputs"]]
            all_decoded_results.append(decode(output_types, result[1][j]))

    return all_decoded_results


def get_token_info_batch(w3, addresses):
    calls = []
    for address in addresses:
        contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=ERC20_ABI)
        calls.extend([(contract, "name", []), (contract, "symbol", []), (contract, "decimals", [])])

    results = multicall(w3, calls)

    token_info = []
    for i in range(0, len(results), 3):
        token_info.append(
            {
                "address": addresses[i // 3],
                "name": results[i][0],
                "symbol": results[i + 1][0],
                "decimals": results[i + 2][0],
            }
        )

    return token_info


def pin_to_ipfs(file_path: str, pinata_token: str):
    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "Authorization": f"Bearer {pinata_token}",
    }
    with open(file_path, "rb") as file:
        files = {"file": file}
        response = requests.post(url, headers=headers, files=files)

    try:
        assert 200 <= response.status_code < 400
        ipfs_hash = response.json()["IpfsHash"]
        logger.info(f"[green]Pinned {file_path} to ipfs:{ipfs_hash}[/green]")
        return f"ipfs://{ipfs_hash}"
    except Exception:
        logger.exception(f"[red]POST to IPFS failed: {response.status_code}[/red]")
        raise
