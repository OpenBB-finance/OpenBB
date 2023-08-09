"""Stock Peers data model."""

from typing import List, Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.standard_models.base import BaseSymbol
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS


class StockPeersQueryParams(QueryParams, BaseSymbol):
    """Stock Peers query model."""


class StockPeersData(Data):
    """Stock Peers data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    peers_list: Optional[List[str]] = Field(
        description="A list of stock peers based on sector, exchange and market cap."
    )
