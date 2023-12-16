"""Real Unemployment Model."""
from datetime import date as dateType
from typing import Literal, Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class UnemploymentQueryParams(QueryParams):
    """Unemployment Query."""

    period: Literal["annual", "quarterly", "monthly"] = Field(
        default="monthly",
        description=QUERY_DESCRIPTIONS.get("units", "")
        + " Can be annual, quarterly or monthly.",
    )
    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class UnemploymentData(Data):
    """Unemployment Data."""

    date: Optional[dateType] = Field(
        default=None, description=DATA_DESCRIPTIONS.get("date")
    )
    value: Optional[float] = Field(
        default=None, description="Nominal GDP value on the date."
    )
