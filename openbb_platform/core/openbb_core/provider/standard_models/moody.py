"""Moody Corporate Bond Index Standard Model."""

from datetime import (
    date as dateType,
)
from typing import Optional

from pydantic import Field, field_validator

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)


class MoodyCorporateBondIndexQueryParams(QueryParams):
    """Moody Corporate Bond Index Query."""

    start_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: Optional[dateType] = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )

    @field_validator("index_type", mode="before", check_fields=False)
    @classmethod
    def to_lower(cls, v: Optional[str]) -> Optional[str]:
        """Convert field to lowercase."""
        return v.lower() if v else v


class MoodyCorporateBondIndexData(Data):
    """Moody Corporate Bond Index Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    rate: Optional[float] = Field(
        default=None,
        description="Moody Corporate Bond Index Rate.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
