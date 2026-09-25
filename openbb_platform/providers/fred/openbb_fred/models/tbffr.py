"""FRED Selected Treasury Bill Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.tbffr import (
    SelectedTreasuryBillData,
    SelectedTreasuryBillQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field, field_validator

from openbb_fred.utils.query import UseCacheQueryParams

TIME_AXIS: dict[str, Any] = {"x-widget_config": {"chartDataType": "time"}}
PERCENT_SERIES: dict[str, Any] = {
    "x-unit_measurement": "percent",
    "x-widget_config": {"chartDataType": "series"},
}

TBFFR_PARAMETER_TO_FRED_ID = {
    "3m": "TB3SMFFM",
    "6m": "TB6SMFFM",
}


class FREDSelectedTreasuryBillQueryParams(
    UseCacheQueryParams, SelectedTreasuryBillQueryParams
):
    """FRED Selected Treasury Bill Query."""


class FREDSelectedTreasuryBillData(SelectedTreasuryBillData):
    """FRED Selected Treasury Bill Data."""

    __alias_dict__ = {"rate": "value"}

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra=TIME_AXIS,
    )
    rate: float | None = Field(
        description="SelectedTreasuryBill Rate.",
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


class FREDSelectedTreasuryBillFetcher(
    Fetcher[
        FREDSelectedTreasuryBillQueryParams,
        list[FREDSelectedTreasuryBillData],
    ]
):
    """FRED Selected Treasury Bill Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FREDSelectedTreasuryBillQueryParams:
        """Transform query."""
        return FREDSelectedTreasuryBillQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FREDSelectedTreasuryBillQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FRED endpoint."""
        from openbb_fred.utils.api import get_observations

        return await get_observations(
            TBFFR_PARAMETER_TO_FRED_ID[query.maturity or "3m"],
            credentials.get("fred_api_key") if credentials else None,
            start_date=query.start_date,
            end_date=query.end_date,
            use_cache=query.use_cache,
            **kwargs,
        )

    @staticmethod
    def transform_data(
        query: FREDSelectedTreasuryBillQueryParams, data: list, **kwargs: Any
    ) -> list[FREDSelectedTreasuryBillData]:
        """Transform data."""
        return [FREDSelectedTreasuryBillData.model_validate(d) for d in data]
