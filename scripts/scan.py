import os
from typing import Dict, List, Tuple

from rich.console import Console
from rich.table import Table
from rich.theme import Theme

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


def scan_images_folder() -> Tuple[List[str], Dict[str, List[str]], Dict[str, List[str]]]:
    networks = []
    tokens_to_append = {}
    errors = {}

    for root, dirs, files in os.walk("images"):
        network = os.path.basename(root)
        if network not in networks and network != "images":
            networks.append(network)
            tokens_to_append[network] = []
            errors[network] = []

        for file in files:
            if file.endswith(".png"):
                token_address = os.path.splitext(file)[0]
                if network != "images":
                    tokens_to_append[network].append(token_address)
            elif file.endswith(".json"):
                # Potential error in JSON file
                if network != "images":
                    errors[network].append(file)

    return networks, tokens_to_append, errors


def display_summary(networks: List[str], tokens_to_append: Dict[str, List[str]], errors: Dict[str, List[str]]):
    table = Table(title="Token List Generation Summary")
    table.add_column("Network", style="cyan")
    table.add_column("Tokens to Append", style="green")
    table.add_column("Errors", style="red")

    for network in networks:
        table.add_row(network, str(len(tokens_to_append[network])), str(len(errors[network])))

    console.print(table)
