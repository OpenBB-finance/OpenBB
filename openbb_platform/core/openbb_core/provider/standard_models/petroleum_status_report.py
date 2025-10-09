"""Petroleum Status Report Standard Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class PetroleumStatusReportQueryParams(QueryParams):
    """Petroleum Status Report Query."""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class PetroleumStatusReportData(Data):
    """Petroleum Status Report Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    table: str | None = Field(description="Table name for the data.")
    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    order: int | None = Field(
        default=None, description="Presented order of the data, relative to the table."
    )
    title: str | None = Field(default=None, description="Title of the data.")
    value: int | float = Field(description="Value of the data.")
    unit: str | None = Field(default=None, description="Unit or scale of the data.")
