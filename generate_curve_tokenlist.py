# flake8: noqa: E402
import os
import sys

# Add the project root directory to the Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from typing import List, Optional

from rich.console import Console
from rich.theme import Theme

from scripts.process import process_network, update_tokenlist
from scripts.scan import display_summary, scan_images_folder
from scripts.utils import load_json, save_json

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

        networks, tokens_to_append, errors = scan_images_folder()
        if networks_to_ignore:
            networks = [net for net in networks if net not in networks_to_ignore]

        display_summary(networks, tokens_to_append, errors)

        all_failed_tokens = {}
        processed_tokens = []
        all_skipped_tokens = []

        for network in networks:
            network_tokens, skipped_tokens = process_network(network, existing_tokens, all_failed_tokens)
            processed_tokens.extend(network_tokens)
            all_skipped_tokens.extend(skipped_tokens)

            # Update the tokenlist after each network
            updated_tokenlist = update_tokenlist(processed_tokens, all_skipped_tokens, existing_tokenlist)
            save_json(updated_tokenlist, "curve_tokenlist.json")

            # Update existing_tokenlist for the next iteration
            existing_tokenlist = updated_tokenlist
            existing_tokens = existing_tokenlist.get("tokens", [])

        if all_failed_tokens:
            save_json(all_failed_tokens, "failed_tokens_report.json")
            console.print(
                "[red]Some tokens failed to return data or validate. Check failed_tokens_report.json for details.[/red]"
            )

        console.print("[green]Token list generation completed![/green]")
    except Exception as e:
        console.print(f"[error]An error occurred: {str(e)}[/error]")
        raise


if __name__ == "__main__":
    main(networks_to_ignore=["assets-harmony"])
