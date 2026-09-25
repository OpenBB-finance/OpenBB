"""FRED SONIA Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.sonia_rates import SONIAData, SONIAQueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field, field_validator

from openbb_fred.utils.query import UseCacheQueryParams

TIME_AXIS: dict[str, Any] = {"x-widget_config": {"chartDataType": "time"}}
RATE_SERIES: dict[str, Any] = {"x-widget_config": {"chartDataType": "series"}}

SONIA_PARAMETER_TO_FRED_ID = {
    "rate": "IUDSOIA",
    "index": "IUDZOS2",
    "10th_percentile": "IUDZLS6",
    "25th_percentile": "IUDZLS7",
    "75th_percentile": "IUDZLS8",
    "90th_percentile": "IUDZLS9",
    "total_nominal_value": "IUDZLT2",
}


class FREDSONIAQueryParams(UseCacheQueryParams, SONIAQueryParams):
    """FRED SONIA Query."""

    parameter: Literal[
        "rate",
        "index",
        "10th_percentile",
        "25th_percentile",
        "75th_percentile",
        "90th_percentile",
        "total_nominal_value",
    ] = Field(default="rate", description="Period of SONIA rate.")


class FREDSONIAData(SONIAData):
    """FRED SONIA Data."""

    __alias_dict__ = {"rate": "value"}

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra=TIME_AXIS,
    )
    rate: float | None = Field(
        description="SONIA rate.",
        json_schema_extra=RATE_SERIES,
    )

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FREDSONIAFetcher(Fetcher[FREDSONIAQueryParams, list[FREDSONIAData]]):
    """FRED SONIA Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FREDSONIAQueryParams:
        """Transform query."""
        return FREDSONIAQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FREDSONIAQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FRED endpoint."""
        from openbb_fred.utils.api import get_observations

        return await get_observations(
            SONIA_PARAMETER_TO_FRED_ID[query.parameter],
            credentials.get("fred_api_key") if credentials else None,
            start_date=query.start_date,
            end_date=query.end_date,
            use_cache=query.use_cache,
            **kwargs,
        )

    @staticmethod
    def transform_data(
        query: FREDSONIAQueryParams, data: dict, **kwargs: Any
    ) -> list[FREDSONIAData]:
        """Transform data."""
        keys = ["date", "value"]
        return [FREDSONIAData(**{k: x[k] for k in keys}) for x in data]
