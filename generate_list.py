import json
import os

from scripts.generate import generate_tokenlist

if __name__ == "__main__":

    if os.path.exists("curve_tokenlist.json"):
        with open("curve_tokenlist.json", "r") as file:
            existing_tokenlist = json.load(file)
    else:
        existing_tokenlist = {}

    new_tokenlist = generate_tokenlist(
        existing_tokenlist, networks_to_include=["mantle"], networks_to_ignore=["assets-harmony"]
    )

    with open("curve_tokenlist.json", "w") as file:
        json.dump(new_tokenlist, file, indent=4)
