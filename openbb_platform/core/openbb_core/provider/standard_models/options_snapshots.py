"""Options Snapshots Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import List, Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS


class OptionsSnapshotsQueryParams(QueryParams):
    """Options Snapshots Query."""


class OptionsSnapshotsData(Data):
    """Options Snapshots Data."""

    underlying_symbol: List[str] = Field(
        description="Ticker symbol of the underlying asset."
    )
    contract_symbol: List[str] = Field(description="Symbol of the options contract.")
    expiration: List[dateType] = Field(
        description="Expiration date of the options contract."
    )
    dte: Optional[List[int]] = Field(
        default=None,
        description="Number of days to expiration of the options contract.",
    )
    strike: List[float] = Field(
        description="Strike price of the options contract.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    option_type: List[str] = Field(description="The type of option.")
    volume: Optional[List[int]] = Field(
        description=DATA_DESCRIPTIONS.get("volume", ""),
    )
    open_interest: Optional[List[int]] = Field(
        default=None,
        description="Open interest at the time.",
    )
    last_price: Optional[List[float]] = Field(
        default=None,
        description="Last trade price at the time.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    last_size: Optional[List[int]] = Field(
        default=None,
        description="Lot size of the last trade.",
    )
    last_timestamp: Optional[List[datetime]] = Field(
        default=None,
        description="Timestamp of the last price.",
    )
    open: Optional[List[float]] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("open", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    high: Optional[List[float]] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("high", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    low: Optional[List[float]] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("low", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    close: Optional[List[float]] = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("close", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
