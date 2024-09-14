import json
from typing import Any, Dict, List, Tuple

from eth_abi import decode
from hexbytes import HexBytes
from rich.console import Console
from web3 import Web3
from web3.exceptions import ContractLogicError, InvalidAddress

from scripts.constants import ERC20_ABI, JSDELIVR_BASE_URL, MULTICALL_ABI, NATIVE_TOKEN_ADDRESS, NETWORKS

console = Console()


def get_network_name(folder_name: str) -> str:
    for network, info in NETWORKS.items():
        if info.folder_name == folder_name:
            return network
    raise ValueError(f"No network found for folder name: {folder_name}")


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

    def process_batch(batch_calls):
        aggregate_calls = [
            (contract.address, contract.encodeABI(fn_name=fn_name, args=args))
            for contract, fn_name, args in batch_calls
        ]

        try:
            result = multicall_contract.functions.aggregate(aggregate_calls).call(block_identifier=block_identifier)
            return result, None
        except ContractLogicError as e:
            if len(batch_calls) == 1:
                contract, fn_name, _ = batch_calls[0]
                console.print(f"[red]ContractLogicError for {contract.address}.{fn_name}: {str(e)}[/red]")
                return None, batch_calls[0]

            mid = len(batch_calls) // 2
            console.print(f"[yellow]Splitting batch of size {len(batch_calls)} due to ContractLogicError[/yellow]")
            left_result, left_failed = process_batch(batch_calls[:mid])
            right_result, right_failed = process_batch(batch_calls[mid:])

            if left_failed:
                failed_calls.append(left_failed)
            if right_failed:
                failed_calls.append(right_failed)

            combined_result = [None, []]
            if left_result:
                combined_result[0] = left_result[0]
                combined_result[1].extend(left_result[1])
            if right_result:
                combined_result[0] = right_result[0]
                combined_result[1].extend(right_result[1])

            return combined_result, None

    for i in range(0, len(calls), batch_size):
        batch_calls = calls[i : i + batch_size]  # noqa: E203
        console.print(f"[cyan]Processing batch {i // batch_size + 1} of {len(calls) // batch_size + 1}[/cyan]")
        result, _ = process_batch(batch_calls)

        if result:
            for j, call in enumerate(batch_calls):
                contract, fn_name, _ = call
                function = contract.get_function_by_name(fn_name)
                output_types = [output["type"] for output in function.abi["outputs"]]
                try:
                    all_decoded_results.append(decode(output_types, result[1][j]))
                except Exception as e:
                    console.print(f"[red]Error decoding result for {contract.address}.{fn_name}: {str(e)}[/red]")
                    failed_calls.append((contract.address, fn_name, str(e)))
                    all_decoded_results.append(None)
        else:
            all_decoded_results.extend([None] * len(batch_calls))

    if failed_calls:
        console.print(f"[yellow]Total failed calls: {len(failed_calls)}[/yellow]")
        for address, fn_name, error in failed_calls[:10]:  # Show first 10 failed calls
            console.print(f"[red]Failed: {address}.{fn_name} - {error}[/red]")
        if len(failed_calls) > 10:
            console.print(f"[yellow]... and {len(failed_calls) - 10} more failed calls[/yellow]")

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
                continue

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

    console.print(f"[cyan]Preparing to call {len(calls)} functions for {len(valid_addresses)} tokens[/cyan]")
    results, failed_calls = multicall(w3, calls)

    token_info = []
    result_index = 0
    for address in valid_addresses:
        name = results[result_index]
        symbol = results[result_index + 1]
        decimals = results[result_index + 2]
        if name is None or symbol is None or decimals is None:
            failed_tokens.append(address)
            console.print(f"[red]Failed to fetch complete token info for address: {address}[/red]")
        else:
            token_info.append(
                {
                    "address": address,
                    "name": name[0] if isinstance(name, tuple) else name,
                    "symbol": symbol[0] if isinstance(symbol, tuple) else symbol,
                    "decimals": decimals[0] if isinstance(decimals, tuple) else decimals,
                }
            )
        result_index += 3

    console.print(f"[green]Successfully fetched info for {len(token_info)} tokens[/green]")
    console.print(f"[yellow]Skipped {len(skipped_tokens)} existing tokens[/yellow]")
    console.print(f"[red]Failed to fetch info for {len(failed_tokens)} tokens[/red]")

    return token_info, failed_tokens, skipped_tokens


def get_logo_uri(network_name: str, address: str) -> str:
    network_info = NETWORKS.get(network_name)
    if not network_info:
        raise ValueError(f"Network information not found for {network_name}")

    return f"{JSDELIVR_BASE_URL}/{network_info.folder_name}/{address}.png"
