import os
from typing import List, Optional

from rich.console import Console
from rich.theme import Theme

from process import process_network, update_tokenlist
from utils import load_json, save_json

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


def main(networks_to_process: Optional[List[str]] = None, networks_to_ignore: Optional[List[str]] = None) -> None:
    console.print("[info]Starting token list generation...[/info]")

    try:
        existing_tokenlist = load_json("curve_tokenlist.json")
        existing_tokens = existing_tokenlist.get("tokens", [])

        networks = networks_to_process or os.listdir("images")
        if networks_to_ignore:
            networks = [net for net in networks if net not in networks_to_ignore]

        all_failed_tokens = {}
        processed_tokens = []
        all_skipped_tokens = []

        for network in networks:
            network_tokens, skipped_tokens = process_network(network, existing_tokens, all_failed_tokens)
            processed_tokens.extend(network_tokens)
            all_skipped_tokens.extend(skipped_tokens)

            # Update and save the tokenlist after each network to preserve progress
            updated_tokenlist = update_tokenlist(processed_tokens, all_skipped_tokens, existing_tokenlist)
            save_json(updated_tokenlist, "curve_tokenlist.json")

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
    main(networks_to_ignore=["harmony"])
