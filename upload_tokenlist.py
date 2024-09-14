from rich.console import Console
from rich.theme import Theme

from scripts.upload import upload_to_github, verify_upload
from scripts.utils import load_json

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


def main():
    console.print("[info]Starting tokenlist upload...[/info]")

    try:
        # Load the locally saved tokenlist
        tokenlist = load_json("curve_tokenlist.json")

        # Upload the tokenlist to GitHub
        repo_name = "curve-tokenlist"  # Replace with your actual repo name
        file_path = "curve_tokenlist.json"
        commit_message = "Update tokenlist"

        raw_url = upload_to_github(tokenlist, repo_name, file_path, commit_message)

        if verify_upload(raw_url, tokenlist):
            console.print(f"[green]Tokenlist successfully uploaded and verified at: {raw_url}[/green]")
        else:
            console.print("[error]Failed to verify uploaded tokenlist[/error]")
            raise Exception("Tokenlist verification failed")

        console.print("[green]Tokenlist upload completed![/green]")
    except Exception as e:
        console.print(f"[error]An error occurred during upload: {str(e)}[/error]")
        raise


if __name__ == "__main__":
    main()
