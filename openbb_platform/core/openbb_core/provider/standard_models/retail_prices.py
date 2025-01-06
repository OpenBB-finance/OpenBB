"""Retail Prices Standard Model."""

from datetime import date as dateType
from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class RetailPricesQueryParams(QueryParams):
    """Retail Prices Query."""

    item: Optional[str] = Field(
        default=None,
        description="The item or basket of items to query.",
    )
    country: str = Field(
        description=QUERY_DESCRIPTIONS.get("country", ""),
        default="united_states",
    )
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class RetailPricesData(Data):
    """Retail Prices Data."""

    date: Optional[dateType] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date")
    )
    symbol: Optional[str] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    country: Optional[str] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("country", ""),
    )
    description: str = Field(
        default=None,
        description="Description of the item.",
    )
    value: Optional[float] = Field(
        default=None,
        description="Price, or change in price, per unit.",
    )
