import os
from typing import Dict, List, Tuple

from rich.console import Console
from rich.table import Table
from rich.theme import Theme

from scripts.constants import NETWORKS
from scripts.utils import get_network_name

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


def scan_tokenlist_and_images(input_tokenlist: Dict) -> Tuple[List[str], Dict[str, List[str]], Dict[str, List[str]]]:
    token_map = input_tokenlist.get("tokenMap", {})
    networks = set()
    tokens_in_list = {}
    missing_tokens = {}

    # Process the input tokenlist
    for key, token in token_map.items():
        chain_id, address = key.split("_")
        network = get_network_from_chain_id(int(chain_id))
        network = get_network_name(NETWORKS[network].folder_name)
        networks.add(network)
        tokens_in_list.setdefault(network, []).append(address.lower())

    # Check for missing tokens
    for network in networks:
        missing_tokens[network] = []
        network_info = NETWORKS[network]
        network_path = os.path.join("images", network_info.folder_name)

        if os.path.exists(network_path):
            # Check for tokens in list but missing images
            for token_address in tokens_in_list[network]:
                image_path = os.path.join(network_path, f"{token_address}.png")
                if not os.path.exists(image_path):
                    missing_tokens[network].append(token_address)

            # Check for images not in tokenlist
            for file in os.listdir(network_path):
                if file.endswith(".png"):
                    token_address = os.path.splitext(file)[0].lower()
                    if token_address not in tokens_in_list[network]:
                        missing_tokens[network].append(f"{token_address}")
        else:
            console.print(f"[yellow]Network directory not found: {network_path}[/yellow]")

    return list(networks), tokens_in_list, missing_tokens


def scan_images_folder(input_tokenlist: Dict) -> Tuple[List[str], Dict[str, List[str]], Dict[str, List[str]]]:
    networks = []
    tokens_in_folder = {}
    tokens_to_add = {}

    images_dir = "images"
    if not os.path.exists(images_dir):
        console.print(f"[error]Images directory not found: {images_dir}[/error]")
        return networks, tokens_in_folder, tokens_to_add

    existing_tokens = get_existing_tokens(input_tokenlist)

    for item in os.listdir(images_dir):
        item_path = os.path.join(images_dir, item)
        if os.path.isdir(item_path):
            try:
                network, network_tokens, network_tokens_to_add = process_network_folder(
                    item, item_path, existing_tokens
                )
                networks.append(network)
                tokens_in_folder[network] = network_tokens
                tokens_to_add[network] = network_tokens_to_add

                print_network_summary(network, network_tokens, network_tokens_to_add)

            except ValueError as e:
                console.print(f"[yellow]Skipping unknown network folder: {item}. Error: {str(e)}[/yellow]")

    return networks, tokens_in_folder, tokens_to_add


def display_summary(networks: List[str], tokens_in_folder: Dict[str, List[str]], tokens_to_add: Dict[str, List[str]]):
    table = Table(title="Token List and Image Comparison Summary")
    table.add_column("Network", style="cyan")
    table.add_column("Tokens in Folder", style="green")
    table.add_column("Tokens to Add", style="yellow")

    for network in networks:
        table.add_row(network, str(len(tokens_in_folder[network])), str(len(tokens_to_add[network])))

    console.print(table)

    for network in networks:
        if tokens_to_add[network]:
            console.print(f"[yellow]Tokens to add for {network}:[/yellow]")
            for token in tokens_to_add[network]:
                console.print(f"[yellow]{token}[/yellow]")


def get_existing_tokens(tokenlist: Dict) -> Dict:
    return tokenlist.get("tokenMap", {})


def process_network_folder(item: str, item_path: str, existing_tokens: Dict) -> Tuple[str, List[str], List[str]]:
    network = get_network_name(item)
    tokens_in_folder = []
    tokens_to_add = []

    network_info = NETWORKS[network]
    chain_id = network_info.chain_id

    for file in os.listdir(item_path):
        if file.endswith(".png"):
            token_address = file[:-4].lower()  # Remove .png and convert to lowercase
            tokens_in_folder.append(token_address)

            # Check if token is not in the existing tokenlist
            if f"{chain_id}_{token_address}" not in existing_tokens:
                tokens_to_add.append(token_address)

    return network, tokens_in_folder, tokens_to_add


def print_network_summary(network: str, tokens_in_folder: List[str], tokens_to_add: List[str]):
    console.print(f"[green]Network: {network}[/green]")
    console.print(f"[green]Tokens in folder: {len(tokens_in_folder)}[/green]")
    console.print(f"[yellow]Tokens to add: {len(tokens_to_add)}[/yellow]")
