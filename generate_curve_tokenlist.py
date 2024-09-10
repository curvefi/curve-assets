# flake8: noqa: E402
import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from typing import List, Optional

from rich.console import Console
from rich.theme import Theme

from scripts.constants import NETWORKS
from scripts.process import process_network, update_tokenlist
from scripts.scan import display_summary, scan_images_folder
from scripts.utils import get_network_name, load_json, save_json

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


def main(networks_to_ignore: Optional[List[str]] = None) -> None:
    console.print("[info]Starting token list generation...[/info]")

    try:
        existing_tokenlist = load_json("curve_tokenlist.json")
        existing_tokens = existing_tokenlist.get("tokens", [])

        # Remove the part that loads the failed_tokens_report.json

        networks, tokens_to_append, errors = scan_images_folder()
        if networks_to_ignore:
            networks = [net for net in networks if net not in networks_to_ignore]

        display_summary(networks, tokens_to_append, errors)

        all_failed_tokens = {}
        processed_tokens = []
        all_skipped_tokens = []

        for network in networks:
            network_name = get_network_name(network)
            network_tokens, skipped_tokens = process_network(network, existing_tokens, all_failed_tokens)
            processed_tokens.extend(network_tokens)
            all_skipped_tokens.extend(skipped_tokens)

            # Update the tokenlist after each network
            updated_tokenlist = update_tokenlist(processed_tokens, all_skipped_tokens, existing_tokenlist)
            save_json(updated_tokenlist, "curve_tokenlist.json")

        # Check if there are any failed tokens
        if os.path.exists("failed_tokens_report.txt") and os.path.getsize("failed_tokens_report.txt") > 0:
            console.print(
                "[yellow]Some tokens failed to return data or validate. Check failed_tokens_report.txt for details.[/yellow]"
            )
        else:
            console.print("[green]All tokens processed successfully![/green]")

        console.print("[green]Token list generation completed![/green]")
    except Exception as e:
        console.print(f"[error]An error occurred: {str(e)}[/error]")
        raise


if __name__ == "__main__":
    main(networks_to_ignore=["assets-harmony"])
