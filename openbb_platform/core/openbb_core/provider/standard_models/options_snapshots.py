"""Options Snapshots Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)
from typing import List, Union

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
    dte: List[Union[int, None]] = Field(
        default_factory=list,
        description="Number of days to expiration of the options contract.",
    )
    strike: List[float] = Field(
        description="Strike price of the options contract.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    option_type: List[str] = Field(description="The type of option.")
    volume: List[Union[int, None]] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("volume", ""),
    )
    open_interest: List[Union[int, None]] = Field(
        default_factory=list,
        description="Open interest at the time.",
    )
    last_price: List[Union[float, None]] = Field(
        default_factory=list,
        description="Last trade price at the time.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    last_size: List[Union[int, None]] = Field(
        default_factory=list,
        description="Lot size of the last trade.",
    )
    last_timestamp: List[Union[datetime, None]] = Field(
        default_factory=list,
        description="Timestamp of the last price.",
    )
    open: List[Union[float, None]] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("open", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    high: List[Union[float, None]] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("high", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    low: List[Union[float, None]] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("low", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    close: List[Union[float, None]] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("close", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
