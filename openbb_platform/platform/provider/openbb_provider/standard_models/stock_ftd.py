"""Stocks Fails to Deliver Data Model."""

from datetime import date as dateType
from typing import Optional

from pydantic import Field, field_validator

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import QUERY_DESCRIPTIONS


class StockFtdQueryParams(QueryParams):
    """Stock FTD Query Params."""

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))

    @field_validator("symbol", mode="before", check_fields=False)
    def upper_symbol(cls, v: str):
        """Convert symbol to uppercase."""
        return v.upper()


class StockFtdData(Data):
    """Stock FTD Data."""

    settlement_date: dateType = Field(description="The settlement date of the fail.")
    quantity: int = Field(description="The quantity of fails.")
    price: Optional[float] = Field(
        description="The price on the day of the fail.", default=None
    )
