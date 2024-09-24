# flake8: noqa: E501, F722

from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Set, Union

from pydantic import AnyUrl, BaseModel, Extra, Field, RootModel, conint, constr
from typing_extensions import Literal

# Define constrained types separately
ConstrainedKeyword = constr(pattern=r"^[\w ]+$", min_length=1, max_length=20)
ConstrainedTagIdentifier = constr(pattern=r"^[\w]+$", min_length=1, max_length=10)
ConstrainedExtensionIdentifier = constr(pattern=r"^[\w]+$", min_length=1, max_length=40)
ConstrainedName = constr(min_length=0, max_length=60)
ConstrainedName1 = constr(pattern=r"^[ \S+]+$", min_length=0, max_length=60)
ConstrainedSymbol = constr(min_length=0, max_length=20)
ConstrainedSymbol1 = constr(pattern=r"^\S+$", min_length=0, max_length=20)
ConstrainedAddress = constr(pattern=r"^0x[a-fA-F0-9]{40}$")
ConstrainedDescription = constr(pattern=r"^[ \w\.,:]+$", min_length=1, max_length=200)
ConstrainedTagName = constr(pattern=r"^[ \w]+$", min_length=1, max_length=20)
ConstrainedTokenListName = constr(pattern=r"^[\w ]+$", min_length=1, max_length=30)


class Keyword(RootModel):
    root: ConstrainedKeyword = Field(
        ...,
        description="A keyword to describe the contents of the list",
        examples=["compound", "lending", "personal tokens"],
    )


class Version(BaseModel):
    class Config:
        extra = Extra.forbid

    major: conint(ge=0) = Field(
        ...,
        description="The major version of the list. Must be incremented when tokens are removed from the list or token addresses are changed.",
        examples=[1, 2],
    )
    minor: conint(ge=0) = Field(
        ...,
        description="The minor version of the list. Must be incremented when tokens are added to the list.",
        examples=[0, 1],
    )
    patch: conint(ge=0) = Field(
        ...,
        description="The patch version of the list. Must be incremented for any changes to the list.",
        examples=[0, 1],
    )


class TagIdentifier(RootModel):
    root: ConstrainedTagIdentifier = Field(
        ..., description="The unique identifier of a tag", 
        examples=["compound", "stablecoin"],
        max_length=20,
    )


class ExtensionIdentifier(RootModel):
    root: ConstrainedExtensionIdentifier = Field(
        ..., description="The name of a token extension property", examples=["color", "is_fee_on_transfer", "aliases"]
    )


class ExtensionPrimitiveValue(RootModel):
    root: Optional[Union[constr(min_length=1, max_length=42), bool, float]]


class ExtensionValueInner1(RootModel):
    root: ExtensionPrimitiveValue


class TagDefinition(BaseModel):
    class Config:
        extra = Extra.forbid

    name: ConstrainedTagName = Field(..., description="The name of the tag")
    description: ConstrainedDescription = Field(..., description="A user-friendly description of the tag")


class Name(RootModel):
    root: Literal[""] = Field("", description="The name of the token", examples=["USD Coin"])


class Name1(RootModel):
    root: ConstrainedName1 = Field(..., description="The name of the token", examples=["USD Coin"])


class Symbol(RootModel):
    root: Literal[""] = Field("", description="The symbol for the token", examples=["USDC"])


class Symbol1(RootModel):
    root: ConstrainedSymbol1 = Field(..., description="The symbol for the token", examples=["USDC"])


class ExtensionValueInner0(RootModel):
    root: Union[ExtensionPrimitiveValue, Dict[str, ExtensionValueInner1]]


class ExtensionValue(RootModel):
    root: Union[ExtensionPrimitiveValue, Dict[str, ExtensionValueInner0]]


class ExtensionMap(RootModel):
    root: Optional[Dict[str, ExtensionValue]] = None


class TokenInfo(BaseModel):
    class Config:
        extra = Extra.forbid

    chainId: conint(ge=1) = Field(
        ..., description="The chain ID of the Ethereum network where this token is deployed", examples=[1, 42]
    )
    address: ConstrainedAddress = Field(
        ...,
        description="The checksummed address of the token on the specified chain ID",
        examples=["0xA0b86991c6218b36c1D1762F925BDADdC4201F984"],
    )
    decimals: conint(ge=0, le=255) = Field(
        ..., description="The number of decimals for the token balance", examples=[18]
    )
    name: Union[Name, Name1] = Field(..., description="The name of the token", examples=["USD Coin"])
    symbol: Union[Symbol, Symbol1] = Field(..., description="The symbol for the token", examples=["USDC"])
    logoURI: Optional[AnyUrl] = Field(
        None,
        description="A URI to the token logo asset; if not set, interface will attempt to find a logo based on the token address; suggest SVG or PNG of size 64x64",
        examples=["ipfs://QmXfzKRvjZz3u5JRgC4v5mGVbm9ahrUiB4DgzHBsnWbTMM"],
    )
    tags: Optional[List[TagIdentifier]] = Field(
        None,
        description="An array of tag identifiers associated with the token; tags are defined at the list level",
        examples=["stablecoin", "compound"],
        max_items=10,
    )
    extensions: Optional[ExtensionMap] = None


class UniswapTokenList(BaseModel):
    name: ConstrainedTokenListName = Field(..., description="The name of the token list", examples=["My Token List"])
    timestamp: datetime = Field(
        ..., description="The timestamp of this list version; i.e. when this immutable version of the list was created"
    )
    version: Version
    tokens: List[TokenInfo] = Field(
        ..., description="The list of tokens included in the list", max_items=10000, min_items=1
    )
    tokenMap: Optional[Dict[str, TokenInfo]] = Field(
        None,
        description="A mapping of key 'chainId_tokenAddress' to its corresponding token object",
        examples=[
            {
                "4_0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984": {
                    "name": "Uniswap",
                    "address": "0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984",
                    "symbol": "UNI",
                    "decimals": 18,
                    "chainId": 4,
                    "logoURI": "ipfs://QmXttGpZrECX5qCyXbBQiqgQNytVGeZW5Anewvh2jc4psg",
                }
            }
        ],
    )
    keywords: Optional[Set[Keyword]] = Field(
        None,
        description="Keywords associated with the contents of the list; may be used in list discoverability",
        max_items=20,
    )
    tags: Optional[Dict[str, TagDefinition]] = Field(
        None,
        description="A mapping of tag identifiers to their name and description",
        examples=[{"stablecoin": {"name": "Stablecoin", "description": "A token with value pegged to another asset"}}],
    )
    logoURI: Optional[AnyUrl] = Field(
        None,
        description="A URI for the logo of the token list; prefer SVG or PNG of size 256x256",
        examples=["ipfs://QmXfzKRvjZz3u5JRgC4v5mGVbm9ahrUiB4DgzHBsnWbTMM"],
    )


def validate_token(token: Dict) -> bool:
    try:
        TokenInfo(**token)
        return True
    except Exception as validation_error:
        print(f"Token validation failed: {validation_error}")
        return False


def validate_tokenlist(tokenlist: Dict) -> bool:
    try:
        UniswapTokenList(**tokenlist)
        return True
    except Exception as validation_error:
        print(f"Token list validation failed: {validation_error}")
        return False
