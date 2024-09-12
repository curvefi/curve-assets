import json
import sys

from eth_utils import to_checksum_address

from scripts.constants import NETWORKS, TOKEN_ABI
from scripts.process import get_w3


def load_tokenlist(file_path):
    with open(file_path, "r") as f:
        return json.load(f)


def get_new_tokens(current_list, cached_list):
    current_tokens = {token["address"]: token for token in current_list["tokens"]}
    cached_tokens = {token["address"]: token for token in cached_list["tokens"]}
    return [token for address, token in current_tokens.items() if address not in cached_tokens]


def check_token_onchain(w3, token):
    address = to_checksum_address(token["address"])
    contract = w3.eth.contract(address=address, abi=TOKEN_ABI)

    try:
        onchain_name = contract.functions.name().call()
        onchain_symbol = contract.functions.symbol().call()
        onchain_decimals = contract.functions.decimals().call()

        return (
            onchain_name == token["name"]
            and onchain_symbol == token["symbol"]
            and onchain_decimals == token["decimals"]
        )
    except Exception as e:
        print(f"Error checking token {address}: {str(e)}")
        return False


def main(cached_tokenlist_path):
    current_list = load_tokenlist("./curve_tokenlist.json")
    cached_list = load_tokenlist(cached_tokenlist_path)

    new_tokens = get_new_tokens(current_list, cached_list)

    all_valid = True
    for token in new_tokens:
        network = token["chainId"]
        w3 = get_w3(NETWORKS[network])
        if not check_token_onchain(w3, token):
            print(f"Token {token['address']} on {NETWORKS[network]} failed validation")
            all_valid = False

    if not all_valid:
        raise ValueError("Some tokens failed validation")

    print("All new tokens validated successfully")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python check_new_tokens.py <path_to_cached_tokenlist>")
        sys.exit(1)
    main(sys.argv[1])
