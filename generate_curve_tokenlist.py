import asyncio
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


async def main():
    tokens = []
    token_map = {}

    # Load existing tokenlist if it exists
    try:
        with open("curve_tokenlist.json", "r") as f:
            existing_tokenlist = json.load(f)
        existing_token_map = existing_tokenlist.get("tokenMap", {})
        logger.info("[green]Loaded existing token list[/green]")
    except FileNotFoundError:
        existing_token_map = {}
        logger.info("[yellow]No existing token list found. Creating new one.[/yellow]")

    for network in os.listdir("images"):
        network_path = os.path.join("images", network)
        if os.path.isdir(network_path):
            logger.info(f"[blue]Processing network: {network}[/blue]")
            rpc_url = DRPC_URL % (network, DRPC_KEY)
            w3 = Web3(Web3.HTTPProvider(rpc_url))

            addresses = [image[:-4] for image in os.listdir(network_path) if image.endswith(".png")]

            token_info_batch = await get_token_info_batch(w3, addresses)

            for info in token_info_batch:
                token_key = f"{network}_{info['address']}"
                existing_token = existing_token_map.get(token_key, {})

                logo_path = f"images/{network}/{info['address']}.png"
                if existing_token.get("logoURI", "").startswith("ipfs://"):
                    logo_uri = existing_token["logoURI"]
                    logger.info(f"[cyan]Using existing IPFS hash for {info['symbol']}[/cyan]")
                else:
                    logo_uri = pin_to_ipfs(logo_path, PINATA_TOKEN)
                    logger.info(f"[green]Pinned new logo for {info['symbol']}[/green]")

                token = {
                    "chainId": NETWORKS.get(network, network),
                    "address": info["address"],
                    "name": info["name"],
                    "symbol": info["symbol"],
                    "decimals": info["decimals"],
                    "logoURI": logo_uri,
                }
                tokens.append(token)
                token_map[token_key] = token

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
    asyncio.run(main())
