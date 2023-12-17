"""PPI Standard Model."""
from datetime import date as dateType
from typing import Literal, Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class ProducerPriceIndexQueryParams(QueryParams):
    """PPI Query."""

    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )
    period: Literal["annual", "quarterly", "monthly"] = Field(
        default="monthly",
        description=(
            QUERY_DESCRIPTIONS.get("period", "")
            + " Can be annual, quarterly or monthly."
        ),
    )


class ProducerPriceIndexData(Data):
    """PPI data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    value: float = Field(description="PPI value.")
