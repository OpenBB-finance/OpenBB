"""FRED European Central Bank Interest Rates Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.ecb_interest_rates import (
    EuropeanCentralBankInterestRatesData,
    EuropeanCentralBankInterestRatesParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field, field_validator

from openbb_fred.utils.query import UseCacheQueryParams

TIME_AXIS: dict[str, Any] = {"x-widget_config": {"chartDataType": "time"}}
PERCENT_SERIES: dict[str, Any] = {
    "x-unit_measurement": "percent",
    "x-widget_config": {"chartDataType": "series"},
}

NAME_TO_ID_ECB = {"deposit": "ECBDFR", "lending": "ECBMLFR", "refinancing": "ECBMRRFR"}


class FREDEuropeanCentralBankInterestRatesParams(
    UseCacheQueryParams, EuropeanCentralBankInterestRatesParams
):
    """FRED European Central Bank Interest Rates Query."""


class FREDEuropeanCentralBankInterestRatesData(EuropeanCentralBankInterestRatesData):
    """FRED European Central Bank Interest Rates Data."""

    __alias_dict__ = {"rate": "value"}

    date: dateType = Field(
        description=DATA_DESCRIPTIONS.get("date", ""),
        json_schema_extra=TIME_AXIS,
    )
    rate: float | None = Field(
        description="European Central Bank Interest Rate.",
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


class FREDEuropeanCentralBankInterestRatesFetcher(
    Fetcher[
        FREDEuropeanCentralBankInterestRatesParams,
        list[FREDEuropeanCentralBankInterestRatesData],
    ]
):
    """FRED ECB Interest Rates Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> FREDEuropeanCentralBankInterestRatesParams:
        """Transform query."""
        return FREDEuropeanCentralBankInterestRatesParams(**params)

    @staticmethod
    async def aextract_data(
        query: FREDEuropeanCentralBankInterestRatesParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list:
        """Return the raw data from the FRED endpoint."""
        from openbb_fred.utils.api import get_observations

        return await get_observations(
            NAME_TO_ID_ECB[query.interest_rate_type],
            credentials.get("fred_api_key") if credentials else None,
            start_date=query.start_date,
            end_date=query.end_date,
            use_cache=query.use_cache,
            **kwargs,
        )

    @staticmethod
    def transform_data(
        query: FREDEuropeanCentralBankInterestRatesParams, data: list, **kwargs: Any
    ) -> list[FREDEuropeanCentralBankInterestRatesData]:
        """Transform data."""
        return [
            FREDEuropeanCentralBankInterestRatesData.model_validate(d) for d in data
        ]
