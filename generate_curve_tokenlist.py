# flake8: noqa: E402
import os
from typing import List, Optional

from rich.console import Console
from rich.theme import Theme

from scripts.constants import JSDELIVR_BASE_URL, NATIVE_TOKEN_ADDRESS, NETWORKS, get_native_token_info
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

        networks, tokens_in_folder, tokens_to_add = scan_images_folder()
        if networks_to_ignore:
            networks = [net for net in networks if net not in networks_to_ignore]

        display_summary(networks, tokens_in_folder, tokens_to_add)

        all_failed_tokens = {}
        processed_tokens = []
        all_skipped_tokens = []

        for network_name in NETWORKS:
            network_tokens, skipped_tokens = process_network(network_name, existing_tokens, all_failed_tokens)
            processed_tokens.extend(network_tokens)
            all_skipped_tokens.extend(skipped_tokens)

            # Ensure the native token is present in the list
            ensure_native_token_in_list(existing_tokenlist, network_name)

            # Update the tokenlist after each network
            updated_tokenlist = update_tokenlist(processed_tokens, all_skipped_tokens, existing_tokenlist)
            save_json(updated_tokenlist, "curve_tokenlist.json")

        # Check if there are any failed tokens
        if all_failed_tokens:
            console.print(
                "[yellow]Some tokens failed to return data or validate. Check failed_tokens_report.json for details.[/yellow]"
            )
            save_json(all_failed_tokens, "failed_tokens_report.json")
        else:
            console.print("[green]All tokens processed successfully![/green]")

        console.print("[green]Token list generation completed![/green]")
    except Exception as e:
        console.print(f"[error]An error occurred: {str(e)}[/error]")
        raise


def ensure_native_token_in_list(tokenlist, network_name):
    """
    Ensure the native token is present and up-to-date in the tokenlist for the given network,
    but only if its image file exists.
    """
    network = NETWORKS[network_name]
    native_token_info = get_native_token_info(network)

    # Check if the native token image exists
    image_path = f"images/{network.folder_name}/{NATIVE_TOKEN_ADDRESS.lower()}.png"
    if not os.path.exists(image_path):
        return  # Skip if the image doesn't exist

    # Remove any existing entry for the native token
    tokenlist["tokens"] = [
        token
        for token in tokenlist["tokens"]
        if not (token["chainId"] == network.chain_id and token["address"].lower() == NATIVE_TOKEN_ADDRESS.lower())
    ]

    # Add the up-to-date native token info
    tokenlist["tokens"].append(native_token_info)

    # Update the tokenMap as well
    token_key = f"{network.chain_id}_{NATIVE_TOKEN_ADDRESS.lower()}"
    tokenlist["tokenMap"][token_key] = native_token_info


if __name__ == "__main__":
    main(networks_to_ignore=["assets-harmony"])
