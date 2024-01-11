"""PROJECTION Standard Model."""


from datetime import date as dateType
from typing import Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS


class PROJECTIONQueryParams(QueryParams):
    """PROJECTION Query."""


class PROJECTIONData(Data):
    """PROJECTION Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    range_high: Optional[float] = Field(
        default=None,
        description="High projection of rates.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    central_tendency_high: Optional[float] = Field(
        default=None,
        description="Central tendency of high projection of rates.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    median: Optional[float] = Field(
        default=None,
        description="Median projection of rates.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    range_midpoint: Optional[float] = Field(
        default=None,
        description="Midpoint projection of rates.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    central_tendency_midpoint: Optional[float] = Field(
        default=None,
        description="Central tendency of midpoint projection of rates.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    range_low: Optional[float] = Field(
        default=None,
        description="Low projection of rates.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    central_tendency_low: Optional[float] = Field(
        default=None,
        description="Central tendency of low projection of rates.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
