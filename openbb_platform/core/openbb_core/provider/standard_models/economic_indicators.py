"""Economic Indicators Standard Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class EconomicIndicatorsQueryParams(QueryParams):
    """Economic Indicators Query."""

    country: str | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("country", "")
        + " The country represented by the indicator, if available.",
    )
    start_date: dateType | None = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: dateType | None = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )


class EconomicIndicatorsData(Data):
    """Economic Indicators Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol_root: str | None = Field(
        default=None, description="The root symbol for the indicator (e.g. GDP)."
    )
    symbol: str | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("symbol", "")
    )
    country: str | None = Field(
        default=None, description="The country represented by the data."
    )
    value: int | float | None = Field(
        default=None, description=DATA_DESCRIPTIONS.get("value", "")
    )
