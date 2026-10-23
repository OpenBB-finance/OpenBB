"""FRED IORB Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.iorb_rates import (
    IORBData,
    IORBQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field, field_validator

from openbb_fred.utils.query import UseCacheQueryParams

TIME_AXIS: dict[str, Any] = {"x-widget_config": {"chartDataType": "time"}}
PERCENT_SERIES: dict[str, Any] = {
    "x-unit_measurement": "percent",
    "x-widget_config": {"chartDataType": "series"},
}


class FREDIORBQueryParams(UseCacheQueryParams, IORBQueryParams):
    """FRED IORB Query."""


class FREDIORBData(IORBData):
    """FRED IORB Data."""

    __alias_dict__ = {"rate": "value"}

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra=TIME_AXIS,
    )
    rate: float | None = Field(
        description="IORB rate.",
        json_schema_extra=PERCENT_SERIES,
    )

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FREDIORBFetcher(Fetcher[FREDIORBQueryParams, list[FREDIORBData]]):
    """FRED IORB Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FREDIORBQueryParams:
        """Transform query."""
        return FREDIORBQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FREDIORBQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FRED endpoint."""
        from openbb_fred.utils.api import get_observations

        return await get_observations(
            "IORB",
            credentials.get("fred_api_key") if credentials else None,
            start_date=query.start_date,
            end_date=query.end_date,
            use_cache=query.use_cache,
            **kwargs,
        )

    @staticmethod
    def transform_data(
        query: FREDIORBQueryParams, data: dict, **kwargs: Any
    ) -> list[FREDIORBData]:
        """Transform data."""
        keys = ["date", "value"]
        return [FREDIORBData(**{k: x[k] for k in keys}) for x in data]
