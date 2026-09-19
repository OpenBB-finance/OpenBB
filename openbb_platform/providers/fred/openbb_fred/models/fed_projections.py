"""FRED PROJECTION Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.fed_projections import (
    PROJECTIONData,
    PROJECTIONQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field

from openbb_fred.utils.query import UseCacheQueryParams

TIME_AXIS: dict[str, Any] = {"x-widget_config": {"chartDataType": "time"}}
PERCENT_SERIES: dict[str, Any] = {
    "x-unit_measurement": "percent",
    "x-widget_config": {"chartDataType": "series"},
}

NAME_TO_ID_PROJECTION = {
    "range_high": ["FEDTARRH", "FEDTARRHLR"],
    "central_tendency_high": ["FEDTARCTH", "FEDTARCTHLR"],
    "median": ["FEDTARMD", "FEDTARMDLR"],
    "range_midpoint": ["FEDTARRM", "FEDTARRMLR"],
    "central_tendency_midpoint": ["FEDTARCTM", "FEDTARCTMLR"],
    "range_low": ["FEDTARRL", "FEDTARRLLR"],
    "central_tendency_low": ["FEDTARCTL", "FEDTARCTLLR"],
}


class FREDPROJECTIONQueryParams(UseCacheQueryParams, PROJECTIONQueryParams):
    """FRED PROJECTION Query."""

    long_run: bool = Field(
        default=False, description="Flag to show long run projections"
    )


class FREDPROJECTIONData(PROJECTIONData):
    """FRED PROJECTION Data."""

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra=TIME_AXIS,
    )
    range_high: float | None = Field(
        description="High projection of rates.",
        json_schema_extra=PERCENT_SERIES,
    )
    central_tendency_high: float | None = Field(
        description="Central tendency of high projection of rates.",
        json_schema_extra=PERCENT_SERIES,
    )
    median: float | None = Field(
        description="Median projection of rates.",
        json_schema_extra=PERCENT_SERIES,
    )
    range_midpoint: float | None = Field(
        description="Midpoint projection of rates.",
        json_schema_extra=PERCENT_SERIES,
    )
    central_tendency_midpoint: float | None = Field(
        description="Central tendency of midpoint projection of rates.",
        json_schema_extra=PERCENT_SERIES,
    )
    range_low: float | None = Field(
        description="Low projection of rates.",
        json_schema_extra=PERCENT_SERIES,
    )
    central_tendency_low: float | None = Field(
        description="Central tendency of low projection of rates.",
        json_schema_extra=PERCENT_SERIES,
    )


class FREDPROJECTIONFetcher(
    Fetcher[FREDPROJECTIONQueryParams, list[FREDPROJECTIONData]]
):
    """FRED Federal Funds Rate Projections Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FREDPROJECTIONQueryParams:
        """Transform query."""
        return FREDPROJECTIONQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FREDPROJECTIONQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FRED endpoint."""
        from openbb_fred.utils.api import get_observations_many
        from openbb_fred.utils.fred_helpers import process_projections

        api_key = credentials.get("fred_api_key") if credentials else None
        names = list(NAME_TO_ID_PROJECTION)
        series = await get_observations_many(
            [NAME_TO_ID_PROJECTION[name][query.long_run] for name in names],
            api_key,
            use_cache=query.use_cache,
            **kwargs,
        )

        return process_projections(dict(zip(names, series)))

    @staticmethod
    def transform_data(
        query: FREDPROJECTIONQueryParams, data: list, **kwargs: Any
    ) -> list[FREDPROJECTIONData]:
        """Transform data"""
        keys = ["date"] + list(NAME_TO_ID_PROJECTION.keys())
        return [FREDPROJECTIONData(**{k: x[k] for k in keys}) for x in data]
