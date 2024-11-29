import os
from datetime import datetime, timezone
from functools import partial
from typing import Dict, List, Optional, Tuple

from rich.console import Console
from web3 import Web3

from scripts.constants import DRPC_KEY, DRPC_URL, NATIVE_TOKEN_ADDRESS, NETWORKS, TOKENLIST_LOGO_URI
from scripts.models import validate_token, validate_tokenlist
from scripts.utils import get_logo_uri, get_token_info_batch

console = Console()

PINATA_TOKEN = os.environ.get("PINATA_TOKEN")


def process_token(
    info: Dict, chain_id: int, network: str, existing_tokens: List[Dict], all_failed_tokens: Dict[str, List[str]]
) -> Optional[Dict]:
    existing_token = next(
        (t for t in existing_tokens if t["address"] == info["address"] and t["chainId"] == chain_id), {}
    )

    logo_uri = get_logo_uri(network, info["address"])

    token = {
        "chainId": chain_id,
        "address": info["address"],
        "name": info["name"] or existing_token.get("name"),
        "symbol": info["symbol"] or existing_token.get("symbol"),
        "decimals": info["decimals"] or existing_token.get("decimals"),
        "logoURI": logo_uri,
    }

    if not validate_token(token):
        all_failed_tokens.setdefault(network, []).append(info["address"])
        return None

    return token


def process_network(
    network_name: str, existing_tokenlist: Dict, all_failed_tokens: Dict[str, List[str]]
) -> Tuple[List[Dict], List[Dict]]:
    
    existing_tokens = existing_tokenlist.get("tokens", [])
    network_info = NETWORKS.get(network_name)
    if not network_info:
        console.print(f"[red]Network information not found for {network_name}[/red]")
        return [], []

    network_path = os.path.join("images", network_info.folder_name)
    if not os.path.isdir(network_path):
        console.print(f"[yellow]Network directory not found: {network_path}[/yellow]")
        return [], []

    console.print(f"[blue]Processing network: {network_name}[/blue]")

    if network_info.rpc_url:
        rpc_url = network_info.rpc_url
    else:
        rpc_url = DRPC_URL % (network_name, DRPC_KEY)

    w3 = Web3(Web3.HTTPProvider(rpc_url))

    addresses = [
        image[:-4]
        for image in os.listdir(network_path)
        if image.endswith(".png") and image[:-4].lower() != NATIVE_TOKEN_ADDRESS.lower()
    ]
    token_info_batch, failed_tokens, skipped_tokens = get_token_info_batch(w3, addresses, existing_tokens)

    if failed_tokens:
        all_failed_tokens[network_name] = failed_tokens
        console.print(f"[yellow]Failed to fetch data for {len(failed_tokens)} tokens on {network_name}[/yellow]")

    chain_id = network_info.chain_id
    process_token_partial = partial(
        process_token,
        chain_id=chain_id,
        network=network_name,
        existing_tokens=existing_tokens,
        all_failed_tokens=all_failed_tokens,
    )

    processed_tokens = list(filter(None, map(process_token_partial, token_info_batch)))
    return processed_tokens, skipped_tokens


def update_tokenlist(new_tokens: List[Dict], existing_tokenlist: Dict) -> Dict:
    current_timestamp = datetime.now(timezone.utc).isoformat()

    # Merge new tokens with existing tokens
    existing_tokens = existing_tokenlist.get("tokens", [])
    all_tokens = existing_tokens + new_tokens

    # Remove duplicates based on chainId and address
    unique_tokens = {f"{token['chainId']}_{token['address'].lower()}": token for token in all_tokens}
    all_tokens = list(unique_tokens.values())

    # Update token map
    token_map = {f"{token['chainId']}_{token['address'].lower()}": token for token in all_tokens}

    updated_tokenlist = {
        "name": existing_tokenlist.get("name", "Curve Token List"),
        "logoURI": TOKENLIST_LOGO_URI,  # Use the constant for the main logo
        "keywords": existing_tokenlist.get("keywords", ["curve", "defi"]),
        "tags": existing_tokenlist.get("tags", {}),
        "timestamp": current_timestamp,
        "tokens": all_tokens,
        "tokenMap": token_map,
        "version": existing_tokenlist.get("version", {"major": 1, "minor": 0, "patch": 0}),
    }

    if not validate_tokenlist(updated_tokenlist):
        console.print("[red]Token list validation failed[/red]")

    return updated_tokenlist
