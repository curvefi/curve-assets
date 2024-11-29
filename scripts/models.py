from typing import Annotated, Dict, List, Optional

from pydantic import BaseModel, Field, UrlConstraints, conint
from pydantic_core import Url


class Version(BaseModel):
    major: conint(ge=0)
    minor: conint(ge=0)
    patch: conint(ge=0)


logoUrl = Annotated[Url, UrlConstraints(max_length=2083, allowed_schemes=["http", "https", "ipfs"])]


class TokenInfo(BaseModel):
    chainId: conint(ge=1)
    address: str
    decimals: conint(ge=0, le=18)
    name: str = Field(..., min_length=1, max_length=60)
    symbol: str = Field(..., min_length=1, max_length=20)
    logoURI: Optional[logoUrl] = None
    tags: Optional[List[str]] = None


class TokenList(BaseModel):
    name: str = Field(..., min_length=1, max_length=30)
    timestamp: str
    version: Version
    tokens: List[TokenInfo]
    keywords: Optional[List[str]] = None
    tags: Optional[Dict[str, Dict[str, str]]] = None
    logoURI: Optional[logoUrl] = None
    tokenMap: Optional[Dict[str, TokenInfo]] = None


def validate_token(token: Dict) -> bool:
    try:
        TokenInfo(**token)
        return True
    except Exception as validation_error:
        print(f"Token validation failed: {validation_error}")
        return False


def validate_tokenlist(tokenlist: Dict) -> bool:
    try:
        TokenList(**tokenlist)
        return True
    except Exception as validation_error:
        print(f"Token list validation failed: {validation_error}")
        return False
