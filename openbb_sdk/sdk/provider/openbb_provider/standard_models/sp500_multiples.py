"""SP500 Multiples  data model."""

from typing import Literal, Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class SP500MultiplesQueryParams(QueryParams):
    """SP500 Multiples Query Params"""

    series_name: str = Field(
        description="The name of the series.", default="PE Ratio by Month"
    )

    start_date: Optional[str] = Field(
        description="The start date of the time series.", default=""
    )

    end_date: Optional[str] = Field(
        description="The end date of the time series.", default=""
    )

    collapse: Optional[
        Literal["daily", "weekly", "monthly", "quarterly", "annual"]
    ] = Field(
        description="The frequency of the time series.",
        default="monthly",
    )
    transform: Optional[Literal["diff", "rdiff", "cumul", "normalize"]] = Field(
        description="The transformation of the time series.",
        default=None,
    )


class SP500MultiplesData(Data):
    """SP500 Multiples Data."""

    date: str = Field(description="The date data for the time series.")
    value: float = Field(description="The data value for the time series.")
