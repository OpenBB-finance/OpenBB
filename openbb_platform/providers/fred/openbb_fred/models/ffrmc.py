"""FRED Selected Treasury Constant Maturity Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.ffrmc import (
    SelectedTreasuryConstantMaturityData,
    SelectedTreasuryConstantMaturityQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field, field_validator

from openbb_fred.utils.query import UseCacheQueryParams

TIME_AXIS: dict[str, Any] = {"x-widget_config": {"chartDataType": "time"}}
PERCENT_SERIES: dict[str, Any] = {
    "x-unit_measurement": "percent",
    "x-widget_config": {"chartDataType": "series"},
}

FFRMC_PARAMETER_TO_FRED_ID = {
    "10y": "T10YFF",
    "5y": "T5YFF",
    "1y": "T1YFF",
    "6m": "T6MFF",
    "3m": "T3MFF",
}


class FREDSelectedTreasuryConstantMaturityQueryParams(
    UseCacheQueryParams, SelectedTreasuryConstantMaturityQueryParams
):
    """FRED Selected Treasury Constant Maturity Query."""


class FREDSelectedTreasuryConstantMaturityData(SelectedTreasuryConstantMaturityData):
    """FRED Selected Treasury Constant Maturity Data."""

    __alias_dict__ = {"rate": "value"}

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra=TIME_AXIS,
    )
    rate: float | None = Field(
        description="Selected Treasury Constant Maturity Rate.",
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


class FREDSelectedTreasuryConstantMaturityFetcher(
    Fetcher[
        FREDSelectedTreasuryConstantMaturityQueryParams,
        list[FREDSelectedTreasuryConstantMaturityData],
    ]
):
    """FRED Selected Treasury Constant Maturity Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FREDSelectedTreasuryConstantMaturityQueryParams:
        """Transform query."""
        return FREDSelectedTreasuryConstantMaturityQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FREDSelectedTreasuryConstantMaturityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FRED endpoint."""
        from openbb_fred.utils.api import get_observations

        return await get_observations(
            FFRMC_PARAMETER_TO_FRED_ID[query.maturity or "10y"],
            credentials.get("fred_api_key") if credentials else None,
            start_date=query.start_date,
            end_date=query.end_date,
            use_cache=query.use_cache,
            **kwargs,
        )

    @staticmethod
    def transform_data(
        query: FREDSelectedTreasuryConstantMaturityQueryParams,
        data: list,
        **kwargs: Any,
    ) -> list[FREDSelectedTreasuryConstantMaturityData]:
        """Transform data."""
        return [
            FREDSelectedTreasuryConstantMaturityData.model_validate(d) for d in data
        ]
