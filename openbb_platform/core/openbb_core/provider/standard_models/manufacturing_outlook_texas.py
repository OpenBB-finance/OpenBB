"""Manufacturing Outlook - Texas - Standard Model."""

from datetime import (
    date as dateType,
)

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class ManufacturingOutlookTexasQueryParams(QueryParams):
    """Manufacturing Outlook - Texas - Query."""

    start_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("start_date", ""),
    )
    end_date: dateType | None = Field(
        default=None,
        description=QUERY_DESCRIPTIONS.get("end_date", ""),
    )


class ManufacturingOutlookTexasData(Data):
    """Manufacturing Outlook - Texas - Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
    topic: str | None = Field(default=None, description="Topic of the survey response.")
    diffusion_index: float | None = Field(default=None, description="Diffusion Index.")
    percent_reporting_increase: float | None = Field(
        default=None,
        description="Percent of respondents reporting an increase over the last month.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percent_reporting_decrease: float | None = Field(
        default=None,
        description="Percent of respondents reporting a decrease over the last month.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    percent_reporting_no_change: float | None = Field(
        default=None,
        description="Percent of respondents reporting no change over the last month.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
