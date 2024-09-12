import json

from jsonschema import validate


def validate_tokenlist_schema():
    try:
        with open("curve_tokenlist.json", "r") as f:
            tokenlist = json.load(f)
        with open("tokenlist.schema.json", "r") as f:
            schema = json.load(f)

        validate(instance=tokenlist, schema=schema)
        print("JSON schema validation passed.")
        return True
    except Exception as e:
        print(f"JSON schema validation failed: {str(e)}")
        return False


if __name__ == "__main__":
    is_valid = validate_tokenlist_schema()
    exit(0 if is_valid else 1)
