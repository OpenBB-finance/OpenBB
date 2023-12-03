"""FRED Discount Window Primary Credit Rate Model."""

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.dwpcr_rates import (
    DiscountWindowPrimaryCreditRateData,
    DiscountWindowPrimaryCreditRateParams,
)
from openbb_fred.utils.fred_base import Fred
from pydantic import Field, field_validator

DWPCR_PARAMETER_TO_FRED_ID = {
    "daily_excl_weekend": "DPCREDIT",
    "monthly": "MPCREDIT",
    "weekly": "WPCREDIT",
    "daily": "RIFSRPF02ND",
    "annual": "RIFSRPF02NA",
}


class FREDDiscountWindowPrimaryCreditRateParams(DiscountWindowPrimaryCreditRateParams):
    """FRED Discount Window Primary Credit Rate Query."""

    parameter: Literal[
        "daily_excl_weekend", "monthly", "weekly", "daily", "annual"
    ] = Field(default="daily_excl_weekend", description="FRED series ID of DWPCR data.")


class FREDDiscountWindowPrimaryCreditRateData(DiscountWindowPrimaryCreditRateData):
    """FRED Discount Window Primary Credit Rate Data."""

    __alias_dict__ = {"rate": "value"}

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
        List[FREDDiscountWindowPrimaryCreditRateData],
    ]
):
    """Transform the query, extract and transform the data from the FRED endpoints."""

    data_type = FREDDiscountWindowPrimaryCreditRateData

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FREDDiscountWindowPrimaryCreditRateParams:
        """Transform query."""
        return FREDDiscountWindowPrimaryCreditRateParams(**params)

    @staticmethod
    def extract_data(
        query: FREDDiscountWindowPrimaryCreditRateParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> list:
        """Extract data."""
        key = credentials.get("fred_api_key") if credentials else ""
        fred = Fred(key)

        data = fred.get_series(
            series_id=DWPCR_PARAMETER_TO_FRED_ID[query.parameter],
            start_date=query.start_date,
            end_date=query.end_date,
            **kwargs,
        )

        return data

    @staticmethod
    def transform_data(
        query: FREDDiscountWindowPrimaryCreditRateParams, data: list, **kwargs: Any
    ) -> List[FREDDiscountWindowPrimaryCreditRateData]:
        """Transform data"""
        return [FREDDiscountWindowPrimaryCreditRateData.model_validate(d) for d in data]
