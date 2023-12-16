"""CCI Standard Model."""
from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class ConsumerConfidenceIndexQueryParams(QueryParams):
    """CCI Query."""

    start_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("start_date")
    )
    end_date: Optional[dateType] = Field(
        default=None, description=QUERY_DESCRIPTIONS.get("end_date")
    )


class ConsumerConfidenceIndexData(Data):
    """CCI data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date"))
    value: float = Field(description="CCI value.")
