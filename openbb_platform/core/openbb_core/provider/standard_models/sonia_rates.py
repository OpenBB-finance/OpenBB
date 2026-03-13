"""SONIA Standard Model."""

from datetime import date as dateType

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class SONIAQueryParams(QueryParams):
    """SONIA Query."""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class SONIAData(Data):
    """SONIA Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: float | None = Field(description="SONIA rate.")
