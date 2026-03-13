"""Mortgage Indices Standard Model."""

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


class MortgageIndicesQueryParams(QueryParams):
    """Mortgage Indices Query."""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class MortgageIndicesData(Data):
    """Mortgage Indices Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    symbol: str | None = Field(
        default=None,
        description=DATA_DESCRIPTIONS.get("symbol", ""),
    )
    name: str | None = Field(
        default=None,
        description="Name of the index.",
    )
    rate: float = Field(
        description="Mortgage rate.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
