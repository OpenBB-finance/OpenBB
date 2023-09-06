"""FRED SOFR Fetcher."""


from typing import Any, Dict, List, Literal, Optional

from openbb_fred.utils.fred_base import Fred
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.sofr_rates import SOFRData, SOFRQueryParams
from pydantic import Field, validator

SOFR_PARAMETER_TO_FRED_ID = {
    "overnight": "SOFR",
    "30_day": "SOFR30DAYAVG",
    "90_day": "SOFR90DAYAVG",
    "180_day": "SOFR180DAYAVG",
    "index": "SOFRINDEX",
}


class FREDSOFRQueryParams(SOFRQueryParams):
    """SOFR query."""

    period: Literal["overnight", "30_day", "90_day", "180_day", "index"] = Field(
        default="overnight", description="Period of SOFR rate."
    )


class FREDSOFRData(SOFRData):
    """SOFR data."""

    class Config:
        """Pydantic alias config using fields dict."""

        fields = {
            "rate": "value",
        }

    @validator("rate", pre=True, check_fields=False)
    def value_validate(cls, v):  # pylint: disable=E0213
        try:
            return float(v)
        except ValueError:
            return float("nan")


class FREDSOFRFetcher(
    Fetcher[FREDSOFRQueryParams, List[Dict[str, List[FREDSOFRData]]]]
):
    """FRED SOFR Fetcher."""

    data_type = FREDSOFRData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDSOFRQueryParams:
        return FREDSOFRQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDSOFRQueryParams, credentials: Optional[Dict[str, str]], **kwargs: Any
    ) -> dict:
        key = credentials.get("fred_api_key") if credentials else ""
        fred_series = SOFR_PARAMETER_TO_FRED_ID[query.period]
        fred = Fred(key)
        data = fred.get_series(fred_series, query.start_date, query.end_date, **kwargs)
        return data

    @staticmethod
    def transform_data(data: dict) -> List[Dict[str, List[FREDSOFRData]]]:
        keys = ["date", "value"]
        return [FREDSOFRData(**{k: x[k] for k in keys}) for x in data]
