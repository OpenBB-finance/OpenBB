"""FRED SOFR Model."""

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.sofr_rates import SOFRData, SOFRQueryParams
from openbb_fred.utils.fred_base import Fred
from pydantic import Field, field_validator

SOFR_PARAMETER_TO_FRED_ID = {
    "overnight": "SOFR",
    "30_day": "SOFR30DAYAVG",
    "90_day": "SOFR90DAYAVG",
    "180_day": "SOFR180DAYAVG",
    "index": "SOFRINDEX",
}


class FREDSOFRQueryParams(SOFRQueryParams):
    """FRED SOFR Query."""

    period: Literal["overnight", "30_day", "90_day", "180_day", "index"] = Field(
        default="overnight", description="Period of SOFR rate."
    )


class FREDSOFRData(SOFRData):
    """FRED SOFR Data."""

    __alias_dict__ = {"rate": "value"}

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FREDSOFRFetcher(
    Fetcher[FREDSOFRQueryParams, List[Dict[str, List[FREDSOFRData]]]]
):
    """Transform the query, extract and transform the data from the FRED endpoints."""

    data_type = FREDSOFRData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDSOFRQueryParams:
        """Transform query."""
        return FREDSOFRQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDSOFRQueryParams, credentials: Optional[Dict[str, str]], **kwargs: Any
    ) -> dict:
        """Extract data."""
        key = credentials.get("fred_api_key") if credentials else ""
        fred_series = SOFR_PARAMETER_TO_FRED_ID[query.period]
        fred = Fred(key)
        data = fred.get_series(fred_series, query.start_date, query.end_date, **kwargs)
        return data

    @staticmethod
    def transform_data(
        query: FREDSOFRQueryParams, data: dict, **kwargs: Any
    ) -> List[Dict[str, List[FREDSOFRData]]]:
        """Transform data"""
        keys = ["date", "value"]
        return [FREDSOFRData(**{k: x[k] for k in keys}) for x in data]
