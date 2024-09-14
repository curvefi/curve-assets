import json
import os
from typing import Dict

import requests
from github import Github, InputGitTreeElement
from rich.console import Console
from rich.theme import Theme

from scripts.generate import generate_tokenlist

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


def load_gh_pages_tokenlist(repo_name: str, file_path: str) -> Dict:
    gh_pages_url = f"https://{repo_name.split('/')[0]}.github.io/{repo_name.split('/')[1]}/{file_path}"
    response = requests.get(gh_pages_url)
    response.raise_for_status()
    return response.json()


def upload_to_github_pages(content: Dict, repo_name: str, file_path: str):
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN is not set in environment variables")

    g = Github(github_token)
    repo = g.get_repo(repo_name)

    # Get the gh-pages branch
    try:
        branch = repo.get_branch("gh-pages")
    except:  # noqa: E722
        # If gh-pages branch doesn't exist, create it
        sb = repo.get_branch(repo.default_branch)
        repo.create_git_ref(ref="refs/heads/gh-pages", sha=sb.commit.sha)
        branch = repo.get_branch("gh-pages")

    # Create blob
    blob = repo.create_git_blob(json.dumps(content, indent=2), "utf-8")
    element = InputGitTreeElement(path=file_path, mode="100644", type="blob", sha=blob.sha)

    # Create tree and commit
    head_sha = branch.commit.sha
    base_tree = repo.get_git_tree(sha=head_sha)
    tree = repo.create_git_tree([element], base_tree)
    parent = repo.get_git_commit(sha=head_sha)
    commit = repo.create_git_commit("Update tokenlist", tree, [parent])
    branch_ref = repo.get_git_ref("heads/gh-pages")
    branch_ref.edit(sha=commit.sha)

    return f"https://{repo.owner.login}.github.io/{repo.name}/{file_path}"


def main():
    console.print("[info]Starting tokenlist generation and upload process...[/info]")

    try:
        repo_name = "curvefi/curve-assets"
        file_path = "curve_tokenlist.json"

        # Load existing tokenlist from GitHub Pages
        console.print("[info]Loading existing tokenlist from GitHub Pages...[/info]")
        existing_tokenlist = load_gh_pages_tokenlist(repo_name, file_path)

        # Generate the new tokenlist
        console.print("[info]Generating new tokenlist...[/info]")
        new_tokenlist = generate_tokenlist(
            existing_tokenlist=existing_tokenlist,
            networks_to_ignore=["assets-harmony"],
        )
        console.print("[green]Tokenlist generated successfully.[/green]")

        # Upload the tokenlist to GitHub Pages
        console.print("[info]Uploading tokenlist to GitHub Pages...[/info]")
        github_pages_url = upload_to_github_pages(new_tokenlist, repo_name, file_path)

        console.print("[green]Tokenlist successfully uploaded to GitHub Pages[/green]")
        console.print(f"[green]GitHub Pages URL: {github_pages_url}[/green]")
        console.print("[green]Tokenlist generation and upload completed![/green]")
    except Exception as e:
        console.print(f"[error]An error occurred during generation or upload: {str(e)}[/error]")
        raise


if __name__ == "__main__":
    main()
