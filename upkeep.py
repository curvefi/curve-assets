import argparse

from rich.console import Console
from rich.theme import Theme

from scripts.constants import NETWORKS
from scripts.generate import generate_tokenlist
from scripts.pages import load_gh_pages_tokenlist, upload_to_github_pages

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


def main(network: str):

    console.print("[info]Starting tokenlist generation and upload process...[/info]")

    repo_name = "curvefi/curve-assets"
    file_path = f"{network}.json"
    networks_to_ignore = ["assets-harmony"]

    # Determine file path based on networks
    if network == "all_networks":
        networks_to_include = [net for net in NETWORKS.keys() if net != "assets-harmony"]
    else:
        assert network in NETWORKS, f"Network '{network}' not found in NETWORKS."
        networks_to_include = [network]

    # Load existing tokenlist from GitHub Pages
    console.print("[info]Loading existing tokenlist from GitHub Pages...[/info]")
    existing_tokenlist = load_gh_pages_tokenlist(repo_name, file_path)

    # Generate the new tokenlist
    console.print("[info]Generating new tokenlist...[/info]")
    new_tokenlist = generate_tokenlist(
        existing_tokenlist=existing_tokenlist,
        networks_to_include=networks_to_include,
        networks_to_ignore=networks_to_ignore,
    )
    console.print("[green]Tokenlist generated successfully.[/green]")

    # Upload the tokenlist to GitHub Pages
    console.print("[info]Uploading tokenlist to GitHub Pages...[/info]")
    github_pages_url = upload_to_github_pages(new_tokenlist, repo_name, file_path)

    console.print("[green]Tokenlist successfully uploaded to GitHub Pages[/green]")
    console.print(f"[green]GitHub Pages URL: {github_pages_url}[/green]")
    console.print("[green]Tokenlist generation and upload completed![/green]")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and upload tokenlist for specified networks.")
    parser.add_argument("networks", help="Network to process, or 'all_networks' for all networks (except harmony)")
    args = parser.parse_args()

    main(args.networks)
