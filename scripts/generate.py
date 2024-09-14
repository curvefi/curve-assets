import os
from typing import Dict, List, Optional

from rich.console import Console
from rich.theme import Theme

from scripts.constants import NATIVE_TOKEN_ADDRESS, NETWORKS, get_native_token_info
from scripts.process import process_network, update_tokenlist
from scripts.scan import display_summary, scan_images_folder
from scripts.utils import save_json

# Create a custom theme for our logs
custom_theme = Theme(
    {
        "info": "cyan",
        "warning": "yellow",
        "error": "bold red",
        "success": "bold green",
    }
)

# Initialize Rich console with our custom theme
console = Console(theme=custom_theme)


def ensure_native_token_in_list(tokenlist, network_name):
    """
    Ensure the native token is present and up-to-date in the tokenlist for the given network,
    but only if its image file exists and 0xeee is in the network folder.
    """
    network = NETWORKS[network_name]
    native_token_info = get_native_token_info(network)

    # Check if the native token image exists and 0xeee is in the folder
    image_path = f"images/{network.folder_name}/{NATIVE_TOKEN_ADDRESS.lower()}.png"
    if not os.path.exists(image_path):
        return  # Skip if conditions are not met

    # Remove any existing entry for the native token
    tokenlist[:] = [
        token
        for token in tokenlist
        if not (token["chainId"] == network.chain_id and token["address"].lower() == NATIVE_TOKEN_ADDRESS.lower())
    ]

    # Add the up-to-date native token info
    tokenlist.append(native_token_info)


def generate_tokenlist(
    existing_tokenlist: Dict,
    networks_to_include: Optional[List[str]] = None,
    networks_to_ignore: Optional[List[str]] = None,
) -> Dict:
    console.print("[info]Starting token list generation...[/info]")

    # Use the input tokenlist for scanning
    networks, tokens_in_folder, tokens_to_add = scan_images_folder(existing_tokenlist)

    if networks_to_include:
        networks = [net for net in networks if net in networks_to_include]
    elif networks_to_ignore:
        networks = [net for net in networks if net not in networks_to_ignore]

    display_summary(networks, tokens_in_folder, tokens_to_add)

    all_failed_tokens = {}
    processed_tokens = []

    for network in networks:
        processed_tokens, _ = process_network(network, existing_tokenlist, all_failed_tokens)
        ensure_native_token_in_list(processed_tokens, network)

        processed_tokens.extend(processed_tokens)

    # Update the tokenlist after processing all networks
    updated_tokenlist = update_tokenlist(processed_tokens, existing_tokenlist)

    # Check if there are any failed tokens
    if all_failed_tokens:
        console.print(
            "[yellow]Some tokens failed to return data or validate. "
            "Check failed_tokens_report.json for details.[/yellow]"
        )
        save_json(all_failed_tokens, "failed_tokens_report.json")
    else:
        console.print("[green]All tokens processed successfully![/green]")

    console.print("[green]Token list generation completed![/green]")

    return updated_tokenlist
