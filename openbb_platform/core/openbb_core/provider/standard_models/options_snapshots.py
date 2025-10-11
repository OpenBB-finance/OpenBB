"""Options Snapshots Standard Model."""

from datetime import (
    date as dateType,
    datetime,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class OptionsSnapshotsQueryParams(QueryParams):
    """Options Snapshots Query."""


class OptionsSnapshotsData(Data):
    """Options Snapshots Data."""

    underlying_symbol: list[str] = Field(
        description="Ticker symbol of the underlying asset."
    )
    contract_symbol: list[str] = Field(description="Symbol of the options contract.")
    expiration: list[dateType] = Field(
        description="Expiration date of the options contract."
    )
    dte: list[int | None] = Field(
        default_factory=list,
        description="Number of days to expiration of the options contract.",
    )
    strike: list[float] = Field(
        description="Strike price of the options contract.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    option_type: list[str] = Field(description="The type of option.")
    volume: list[int | None] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("volume", ""),
    )
    open_interest: list[int | None] = Field(
        default_factory=list,
        description="Open interest at the time.",
    )
    last_price: list[float | None] = Field(
        default_factory=list,
        description="Last trade price at the time.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    last_size: list[int | None] = Field(
        default_factory=list,
        description="Lot size of the last trade.",
    )
    last_timestamp: list[datetime | None] = Field(
        default_factory=list,
        description="Timestamp of the last price.",
    )
    open: list[float | None] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("open", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    high: list[float | None] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("high", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    low: list[float | None] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("low", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    close: list[float | None] = Field(
        default_factory=list,
        description=DATA_DESCRIPTIONS.get("close", ""),
        json_schema_extra={"x-unit_measurement": "currency"},
    )
