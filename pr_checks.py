import os
import re
import sys


def check_file(file_path):
    errors = []

    # Exclude checks for specific files
    excluded_files = ["poetry.lock", "curve_tokenlist.json", "pyproject.toml"]
    if any(file_path.endswith(excluded) for excluded in excluded_files):
        return errors

    if not (file_path.startswith("images/") or file_path.startswith("platforms/")):
        errors.append(
            f"Error with `{file_path}`: Only additions of token icons (in the /images folder) "
            f"or platform logos (in the /platforms folder) are permitted"
        )

    if file_path.startswith("images/assets"):
        if not file_path.endswith(".png"):
            errors.append(f"Error with `{file_path}`: The new icon must be a PNG file")
        elif not re.match(r"^images/assets(-[a-z]+)*/[a-z0-9]+\.png$", file_path):
            errors.append(f"Error with `{file_path}`: The new icon's filename must be entirely lowercase")

    return errors


def main():
    all_changed_files = os.environ.get("ALL_CHANGED_FILES", "").split()
    all_errors = []

    for file in all_changed_files:
        errors = check_file(file)
        all_errors.extend(errors)

    if all_errors:
        for error in all_errors:
            print(f"::error::{error}")
        sys.exit(1)
    else:
        print("No errors found in PR checks.")
        sys.exit(0)


if __name__ == "__main__":
    main()
