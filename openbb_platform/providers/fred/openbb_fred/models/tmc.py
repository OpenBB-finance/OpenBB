"""FRED Treasury Constant Maturity Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.tmc import (
    TreasuryConstantMaturityData,
    TreasuryConstantMaturityQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field, field_validator

from openbb_fred.utils.query import UseCacheQueryParams

TIME_AXIS: dict[str, Any] = {"x-widget_config": {"chartDataType": "time"}}
PERCENT_SERIES: dict[str, Any] = {
    "x-unit_measurement": "percent",
    "x-widget_config": {"chartDataType": "series"},
}

TMC_PARAMETER_TO_FRED_ID = {
    "3m": "T10Y3M",
    "2y": "T10Y2Y",
}


class FREDTreasuryConstantMaturityQueryParams(
    UseCacheQueryParams, TreasuryConstantMaturityQueryParams
):
    """FRED Treasury Constant Maturity Query."""


class FREDTreasuryConstantMaturityData(TreasuryConstantMaturityData):
    """FRED Treasury Constant Maturity Data."""

    __alias_dict__ = {"rate": "value"}

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra=TIME_AXIS,
    )
    rate: float | None = Field(
        description="TreasuryConstantMaturity Rate.",
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


class FREDTreasuryConstantMaturityFetcher(
    Fetcher[
        FREDTreasuryConstantMaturityQueryParams,
        list[FREDTreasuryConstantMaturityData],
    ]
):
    """Transform the query, extract and transform the data from the FRED endpoints."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FREDTreasuryConstantMaturityQueryParams:
        """Transform query."""
        return FREDTreasuryConstantMaturityQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FREDTreasuryConstantMaturityQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FRED endpoint."""
        from openbb_fred.utils.api import get_observations

        return await get_observations(
            TMC_PARAMETER_TO_FRED_ID[query.maturity or "3m"],
            credentials.get("fred_api_key") if credentials else None,
            start_date=query.start_date,
            end_date=query.end_date,
            use_cache=query.use_cache,
            **kwargs,
        )

    @staticmethod
    def transform_data(
        query: FREDTreasuryConstantMaturityQueryParams, data: list, **kwargs: Any
    ) -> list[FREDTreasuryConstantMaturityData]:
        """Transform data."""
        return [FREDTreasuryConstantMaturityData.model_validate(d) for d in data]
