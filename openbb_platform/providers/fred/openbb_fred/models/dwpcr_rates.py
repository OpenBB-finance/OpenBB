"""FRED Discount Window Primary Credit Rate Model."""

from datetime import date as dateType
from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.dwpcr_rates import (
    DiscountWindowPrimaryCreditRateData,
    DiscountWindowPrimaryCreditRateParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field, field_validator

from openbb_fred.utils.query import UseCacheQueryParams

TIME_AXIS: dict[str, Any] = {"x-widget_config": {"chartDataType": "time"}}
PERCENT_SERIES: dict[str, Any] = {
    "x-unit_measurement": "percent",
    "x-widget_config": {"chartDataType": "series"},
}

DWPCR_PARAMETER_TO_FRED_ID = {
    "daily_excl_weekend": "DPCREDIT",
    "monthly": "MPCREDIT",
    "weekly": "WPCREDIT",
    "daily": "RIFSRPF02ND",
    "annual": "RIFSRPF02NA",
}


class FREDDiscountWindowPrimaryCreditRateParams(
    UseCacheQueryParams, DiscountWindowPrimaryCreditRateParams
):
    """FRED Discount Window Primary Credit Rate Query."""

    parameter: Literal["daily_excl_weekend", "monthly", "weekly", "daily", "annual"] = (
        Field(default="daily_excl_weekend", description="FRED series ID of DWPCR data.")
    )


class FREDDiscountWindowPrimaryCreditRateData(DiscountWindowPrimaryCreditRateData):
    """FRED Discount Window Primary Credit Rate Data."""

    __alias_dict__ = {"rate": "value"}

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra=TIME_AXIS,
    )
    rate: float | None = Field(
        description="Discount Window Primary Credit Rate.",
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


class FREDDiscountWindowPrimaryCreditRateFetcher(
    Fetcher[
        FREDDiscountWindowPrimaryCreditRateParams,
        list[FREDDiscountWindowPrimaryCreditRateData],
    ]
):
    """FRED Discount Window Primary Credit Rate Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FREDDiscountWindowPrimaryCreditRateParams:
        """Transform query."""
        return FREDDiscountWindowPrimaryCreditRateParams(**params)

    @staticmethod
    async def aextract_data(
        query: FREDDiscountWindowPrimaryCreditRateParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FRED endpoint."""
        from openbb_fred.utils.api import get_observations

        return await get_observations(
            DWPCR_PARAMETER_TO_FRED_ID[query.parameter],
            credentials.get("fred_api_key") if credentials else None,
            start_date=query.start_date,
            end_date=query.end_date,
            use_cache=query.use_cache,
            **kwargs,
        )

    @staticmethod
    def transform_data(
        query: FREDDiscountWindowPrimaryCreditRateParams, data: list, **kwargs: Any
    ) -> list[FREDDiscountWindowPrimaryCreditRateData]:
        """Transform data."""
        return [FREDDiscountWindowPrimaryCreditRateData.model_validate(d) for d in data]
