"""Commodity Spot Prices Standard Model."""

from datetime import (
    date as dateType,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class CommoditySpotPricesQueryParams(QueryParams):
    """Commodity Spot Prices Query."""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class CommoditySpotPricesData(Data):
    """Commodity Spot Prices Data."""

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
    )
    symbol: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    commodity: str | None = Field(
        default=None,
        description="Commodity name.",
    )
    price: float = Field(
        description="Price of the commodity.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    unit: str | None = Field(
        default=None,
        description="Unit of the commodity price.",
    )
