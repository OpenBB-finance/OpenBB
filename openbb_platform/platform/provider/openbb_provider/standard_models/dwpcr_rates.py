"""Discount Window Primary Credit Rate Standard Model."""
from datetime import (
    date as dateType,
)
from typing import Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams
from openbb_provider.utils.descriptions import DATA_DESCRIPTIONS, QUERY_DESCRIPTIONS


class DiscountWindowPrimaryCreditRateParams(QueryParams):
    """Discount Window Primary Credit Rate Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class DiscountWindowPrimaryCreditRateData(Data):
    """Discount Window Primary Credit Rate Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: Optional[float] = Field(description="Discount Window Primary Credit Rate.")
