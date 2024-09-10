import json
import os

import requests


def upload_tokenlist():
    # Load the tokenlist
    with open("curve_tokenlist.json", "r") as f:
        tokenlist = json.load(f)

    # Get the upload URL from environment variable
    upload_url = os.environ.get("TOKENLIST_UPLOAD_URL")
    if not upload_url:
        raise ValueError("TOKENLIST_UPLOAD_URL environment variable is not set")

    # Upload the tokenlist
    response = requests.post(upload_url, json=tokenlist)
    response.raise_for_status()

    print(f"Tokenlist uploaded successfully to {upload_url}")


if __name__ == "__main__":
    upload_tokenlist()
