import json
import os
from typing import Dict

import requests
from github import Github


def upload_to_github(content: Dict, repo_name: str, file_path: str, commit_message: str) -> str:
    """
    Upload content to a GitHub repository and return the raw content URL.
    """
    github_token = os.environ.get("GITHUB_TOKEN")
    if not github_token:
        raise ValueError("GITHUB_TOKEN environment variable is not set")

    g = Github(github_token)
    repo = g.get_user().get_repo(repo_name)

    try:
        # Try to get the file to update it
        file = repo.get_contents(file_path)
        repo.update_file(file_path, commit_message, json.dumps(content, indent=2), file.sha)
    except:  # noqa: E722
        # If the file doesn't exist, create it
        repo.create_file(file_path, commit_message, json.dumps(content, indent=2))

    # Get the raw content URL
    raw_url = f"https://raw.githubusercontent.com/{repo.full_name}/main/{file_path}"
    return raw_url


def verify_upload(url: str, expected_content: Dict) -> bool:
    """
    Verify that the uploaded content matches the expected content.
    """
    response = requests.get(url)
    if response.status_code == 200:
        uploaded_content = response.json()
        return uploaded_content == expected_content
    return False
