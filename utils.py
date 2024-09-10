import json
from typing import Any, Dict, List, Tuple

import requests
from eth_abi import decode
from hexbytes import HexBytes
from rich.console import Console
from web3 import Web3
from web3.exceptions import BadFunctionCallOutput, InvalidAddress

from constants import ERC20_ABI, MULTICALL_ABI, NATIVE_TOKEN_ADDRESS, NETWORKS

console = Console()


def load_json(file_path: str) -> Dict:
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        console.print(f"[yellow]File not found: {file_path}. Returning empty dict.[/yellow]")
        return {}


def save_json(data: Dict, file_path: str) -> None:
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    console.print(f"[green]Saved data to {file_path}[/green]")


def multicall(
    w3: Web3, calls: list, block_identifier: int = "latest", batch_size: int = 1000
) -> Tuple[List[Any], List[Tuple[str, str, str]]]:
    network_name = next((name for name, net in NETWORKS.items() if net.chain_id == w3.eth.chain_id), None)
    if not network_name:
        console.print(f"[red]Unsupported chain ID: {w3.eth.chain_id}[/red]")
        raise ValueError(f"Unsupported chain ID: {w3.eth.chain_id}")

    network = NETWORKS[network_name]
    multicall_address = network.multicall_address
    if not multicall_address:
        console.print(f"[red]Multicall address not found for network: {network_name}[/red]")
        raise ValueError(f"Multicall address not found for network: {network_name}")

    multicall_contract = w3.eth.contract(address=multicall_address, abi=MULTICALL_ABI)

    all_decoded_results = []
    failed_calls = []
    for i in range(0, len(calls), batch_size):
        batch_calls = calls[i : i + batch_size]  # noqa: E203

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
            try:
                all_decoded_results.append(decode(output_types, result[1][j]))
            except BadFunctionCallOutput as e:
                failed_calls.append((contract.address, fn_name, str(e)))
                all_decoded_results.append(None)
            except Exception as e:
                console.print(f"[red]Unexpected error decoding result for {contract.address}.{fn_name}: {str(e)}[/red]")
                failed_calls.append((contract.address, fn_name, str(e)))
                all_decoded_results.append(None)

    return all_decoded_results, failed_calls


def is_valid_address(address: str) -> bool:
    try:
        return len(HexBytes(address)) == 20
    except ValueError:
        return False


def get_token_info_batch(w3, addresses, existing_tokens):
    console.print("[cyan]Fetching token info in batch...[/cyan]")
    calls = []
    valid_addresses = []
    skipped_tokens = []
    failed_tokens = []
    for address in addresses:
        if not is_valid_address(address):
            failed_tokens.append(address)
            console.print(f"[red]Invalid address format: {address}[/red]")
            continue

        if address.lower() != NATIVE_TOKEN_ADDRESS.lower():
            existing_token = next(
                (
                    t
                    for t in existing_tokens
                    if t["address"].lower() == address.lower() and t["chainId"] == w3.eth.chain_id
                ),
                None,
            )
            if existing_token and all(existing_token.get(key) for key in ["name", "symbol", "decimals"]):
                skipped_tokens.append(existing_token)
                continue  # Skip this token as it's already in the list with all required info

            try:
                contract = w3.eth.contract(address=Web3.to_checksum_address(address), abi=ERC20_ABI)
                calls.extend([(contract, "name", []), (contract, "symbol", []), (contract, "decimals", [])])
                valid_addresses.append(address)
            except InvalidAddress:
                failed_tokens.append(address)
                console.print(f"[red]Failed to instantiate contract for address: {address}[/red]")
            except Exception as e:
                failed_tokens.append(address)
                console.print(f"[red]Unexpected error instantiating contract for address {address}: {str(e)}[/red]")

    results, failed_calls = multicall(w3, calls)

    token_info = []
    result_index = 0
    for address in valid_addresses:
        name = results[result_index]
        symbol = results[result_index + 1]
        decimals = results[result_index + 2]
        if name is None or symbol is None or decimals is None:
            failed_tokens.append(address)
            console.print(f"[red]Failed to fetch token info for address: {address}[/red]")
        else:
            token_info.append(
                {
                    "address": address,
                    "name": name[0],
                    "symbol": symbol[0],
                    "decimals": decimals[0],
                }
            )
        result_index += 3

    return token_info, failed_tokens, skipped_tokens


def pin_to_ipfs(file_path: str, pinata_token: str):
    console.print(f"[cyan]Pinning {file_path} to IPFS...[/cyan]")
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
        console.print(f"[green]Pinned {file_path} to ipfs:{ipfs_hash}[/green]")
        return f"ipfs://{ipfs_hash}"
    except Exception:
        console.print(f"[red]POST to IPFS failed: {response.status_code}[/red]", style="bold")
        raise
