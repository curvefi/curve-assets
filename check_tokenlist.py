from rich.console import Console
from rich.table import Table

from scripts.scan import scan_tokenlist_and_images


def check_tokenlist():

    console = Console()

    networks, tokens_in_list, missing_tokens = scan_tokenlist_and_images()

    table = Table(title="Tokenlist and Image Check Summary", show_lines=True)
    table.add_column("Network", style="cyan")
    table.add_column("In Tokenlist", style="green", justify="right")
    table.add_column("Missing", style="red", justify="right")
    table.add_column("Address of Tokens missing in Tokenlist", style="yellow", max_width=50)

    total_in_tokenlist = 0
    total_missing_tokens = 0
    all_zero_missing = True

    for network in networks:
        in_tokenlist = len(tokens_in_list[network])
        missing = len(missing_tokens[network])

        if missing > 0:
            all_zero_missing = False

        total_in_tokenlist += in_tokenlist
        total_missing_tokens += missing

        missing_tokens_str = "\n".join(missing_tokens[network])

        table.add_row(network, str(in_tokenlist), str(missing), missing_tokens_str)

    table.add_row("Total", str(total_in_tokenlist), str(total_missing_tokens), "", style="bold")

    console.print(table)

    if not all_zero_missing:
        error_message = "Tokenlist check failed. There are missing tokens or images."
        console.print(f"[bold red]{error_message}[/bold red]")
        with open("tokenlist_check_results.txt", "w") as f:
            f.write(error_message + "\n\n")
            console = Console(file=f, width=100)
            console.print(table)

    return all_zero_missing


if __name__ == "__main__":
    all_zero_missing = check_tokenlist()
    exit(0 if all_zero_missing else 1)
