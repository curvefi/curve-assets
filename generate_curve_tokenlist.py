import json
import logging
import os
from datetime import datetime, timezone

from rich.logging import RichHandler
from web3 import Web3

from constants import DRPC_KEY, DRPC_URL, NETWORKS
from utils import get_token_info_batch, pin_to_ipfs

logging.basicConfig(
    level="INFO",
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)],
)

logger = logging.getLogger("rich")

PINATA_TOKEN = os.environ.get("PINATA_TOKEN")


def main(networks_to_process=None):
    tokens = []
    token_map = {}
    all_failed_tokens = {}

    # Load existing tokenlist if it exists
    try:
        with open("curve_tokenlist.json", "r") as f:
            existing_tokenlist = json.load(f)
        existing_token_map = existing_tokenlist.get("tokenMap", {})
        logger.info("[green]Loaded existing token list[/green]")
    except FileNotFoundError:
        existing_token_map = {}
        logger.info("[yellow]No existing token list found. Creating new one.[/yellow]")

    networks = networks_to_process if networks_to_process else os.listdir("images")

    for network in networks:
        network_path = os.path.join("images", network)
        network_name = (
            "gnosis" if network == "assets-xdai" else (network[7:] if network.startswith("assets-") else "ethereum")
        )

        if os.path.isdir(network_path):
            logger.info(f"[blue]Processing network: {network_name}[/blue]")
            rpc_url = DRPC_URL % (network_name, DRPC_KEY)
            w3 = Web3(Web3.HTTPProvider(rpc_url))

            addresses = [image[:-4] for image in os.listdir(network_path) if image.endswith(".png")]

            token_info_batch, failed_tokens = get_token_info_batch(w3, addresses)

            if failed_tokens:
                all_failed_tokens[network_name] = failed_tokens
                logger.warning(
                    f"[yellow]Failed to fetch data for {len(failed_tokens)} tokens on {network_name}[/yellow]"
                )

            for info in token_info_batch:
                token_key = f"{network}_{info['address']}"
                existing_token = existing_token_map.get(token_key, {})

                logo_path = f"images/{network}/{info['address']}.png"
                if existing_token.get("logoURI", "").startswith("ipfs://"):
                    logo_uri = existing_token["logoURI"]
                    logger.info(f"[cyan]Using existing IPFS hash for {info['address']}[/cyan]")
                else:
                    logo_uri = pin_to_ipfs(logo_path, PINATA_TOKEN)
                    logger.info(f"[green]Pinned new logo for {info['address']}[/green]")

                token = {
                    "chainId": NETWORKS[network_name].chain_id,
                    "address": info["address"],
                    "name": info["name"] or existing_token.get("name"),
                    "symbol": info["symbol"] or existing_token.get("symbol"),
                    "decimals": info["decimals"] or existing_token.get("decimals"),
                    "logoURI": logo_uri,
                }
                tokens.append(token)
                token_map[token_key] = token

    # Generate failed tokens report with error messages
    if all_failed_tokens:
        with open("failed_tokens_report.json", "w") as f:
            json.dump(all_failed_tokens, f, indent=2)

        # Generate a more detailed error report
        with open("failed_tokens_error_report.txt", "w") as f:
            for network, tokens in all_failed_tokens.items():
                f.write(f"Network: {network}\n")
                for token, error in tokens:
                    f.write(f"  Token: {token}\n")

        logger.warning(
            "[red]Some tokens failed to return data. Check failed_tokens_report.json"
            "and failed_tokens_error_report.txt for details.[/red]"
        )

    current_timestamp = datetime.now(timezone.utc).isoformat()

    tokenlist = {
        "name": "Curve Token List",
        "logoURI": "",
        "keywords": ["curve", "defi"],
        "tags": {},
        "timestamp": current_timestamp,
        "tokens": tokens,
        "tokenMap": token_map,
        "version": {"major": 1, "minor": 0, "patch": 0},
    }

    with open("curve_tokenlist.json", "w") as f:
        json.dump(tokenlist, f, indent=2)

    logger.info("[green]Token list generated and saved successfully![/green]")


if __name__ == "__main__":
    main(["assets-arbitrum"])
