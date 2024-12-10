"""Nominal GDP Standard Model."""

from datetime import date as dateType
from typing import Optional, Union

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class GdpNominalQueryParams(QueryParams):
    """Nominal GDP Query."""

    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class GdpNominalData(Data):
    """Nominal GDP Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    country: str = Field(
        default=None, description="The country represented by the GDP value."
    )
    value: Union[int, float] = Field(
        description="GDP value for the country and date.",
    )
