"""Equity Screener Standard Model."""

from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class EquityScreenerQueryParams(QueryParams):
    """Equity Screener Query."""


class EquityScreenerData(Data):
    """Equity Screener Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    name: Optional[str] = Field(default=None, description="Name of the company.")
