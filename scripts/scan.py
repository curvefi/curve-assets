import os
from typing import Dict, List, Tuple

from rich.console import Console
from rich.table import Table
from rich.theme import Theme

from scripts.constants import NETWORKS
from scripts.utils import get_network_name, load_json

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


def get_network_from_chain_id(chain_id: int) -> str:
    for network, info in NETWORKS.items():
        if info.chain_id == chain_id:
            return network
    return f"unknown_{chain_id}"


def get_directory_from_network(network: str) -> str:
    if network == "ethereum":
        return "assets"  # Changed from "ethereum" to "assets"
    elif network == "gnosis":
        return "assets-xdai"
    else:
        return f"assets-{network}"


def scan_tokenlist_and_images() -> Tuple[List[str], Dict[str, List[str]], Dict[str, List[str]]]:
    tokenlist = load_json("curve_tokenlist.json")
    networks = set()
    tokens_in_list = {}
    missing_tokens = {}

    # First, process the tokenlist
    for token in tokenlist.get("tokens", []):
        network = get_network_from_chain_id(token["chainId"])
        network = get_network_name(f"assets-{network}")  # Handle special cases like 'xdai' and 'ethereum'
        networks.add(network)
        tokens_in_list.setdefault(network, []).append(token["address"].lower())

    # Now check for missing tokens (either in images or in tokenlist)
    for network in networks:
        missing_tokens[network] = []
        network_dir = get_directory_from_network(network)
        network_path = os.path.join("images", network_dir)

        if os.path.exists(network_path):
            # Check for tokens in list but missing images
            for token_address in tokens_in_list[network]:
                image_path = os.path.join(network_path, f"{token_address}.png")
                if not os.path.exists(image_path):
                    missing_tokens[network].append(f"{token_address} (no image)")

            # Check for images not in tokenlist
            for file in os.listdir(network_path):
                if file.endswith(".png"):
                    token_address = os.path.splitext(file)[0].lower()
                    if token_address not in tokens_in_list[network]:
                        missing_tokens[network].append(f"{token_address}")
        else:
            console.print(f"[yellow]Network directory not found: {network_path}[/yellow]")

    return list(networks), tokens_in_list, missing_tokens


def display_summary(networks: List[str], tokens_in_list: Dict[str, List[str]], missing_tokens: Dict[str, List[str]]):
    table = Table(title="Token List and Image Comparison Summary")
    table.add_column("Network", style="cyan")
    table.add_column("Tokens in List", style="green")
    table.add_column("Missing Tokens", style="red")

    for network in networks:
        table.add_row(network, str(len(tokens_in_list[network])), str(len(missing_tokens[network])))

    console.print(table)


if __name__ == "__main__":
    networks, tokens_in_list, missing_tokens = scan_tokenlist_and_images()
    display_summary(networks, tokens_in_list, missing_tokens)
