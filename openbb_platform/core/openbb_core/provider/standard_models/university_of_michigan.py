"""University Of Michigan Survey Standard Model."""

from datetime import (
    date as dateType,
)
from typing import Optional

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class UofMichiganQueryParams(QueryParams):
    """University Of Michigan Survey Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class UofMichiganData(Data):
    """University Of Michigan Survey Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    consumer_sentiment: Optional[float] = Field(
        default=None,
        description="Index of the results of the University of Michigan's monthly Survey of Consumers,"
        + " which is used to estimate future spending and saving.  (1966:Q1=100).",
    )
    inflation_expectation: Optional[float] = Field(
        default=None,
        description="Median expected price change next 12 months, Surveys of Consumers.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
