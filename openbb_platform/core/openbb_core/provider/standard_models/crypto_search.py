"""Crypto Search Standard Model."""

from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class CryptoSearchQueryParams(QueryParams):
    """Crypto Search Query."""

    query: Optional[str] = Field(description="Search query.", default=None)


class CryptoSearchData(Data):
    """Crypto Search Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", "") + " (Crypto)")
    name: Optional[str] = Field(description="Name of the crypto.", default=None)
