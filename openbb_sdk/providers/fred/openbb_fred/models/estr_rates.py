"""FRED ESTR Fetcher."""


from typing import Any, Dict, List, Literal, Optional

from openbb_fred.utils.fred_base import Fred
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.estr_rates import ESTRData, ESTRQueryParams
from pydantic import Field, validator

ESTR_PARAMETER_TO_ID = {
    "volume_weighted_trimmed_mean_rate": "ECBESTRVOLWGTTRMDMNRT",
    "number_of_transactions": "ECBESTRNUMTRANS",
    "number_of_active_banks": "ECBESTRNUMACTBANKS",
    "total_volume": "ECBESTRTOTVOL",
    "share_of_volume_of_the_5_largest_active_banks": "ECBESTRSHRVOL5LRGACTBNK",
    "rate_at_75th_percentile_of_volume": "ECBESTRRT75THPCTVOL",
    "rate_at_25th_percentile_of_volume": "ECBESTRRT25THPCTVOL",
}


class FREDESTRQueryParams(ESTRQueryParams):
    """ESTR query."""

    parameter: Literal[
        "volume_weighted_trimmed_mean_rate",
        "number_of_transactions",
        "number_of_active_banks",
        "total_volume",
        "share_of_volume_of_the_5_largest_active_banks",
        "rate_at_75th_percentile_of_volume",
        "rate_at_25th_percentile_of_volume",
    ] = Field(
        default="volume_weighted_trimmed_mean_rate", description="Period of ESTR rate."
    )


class FREDESTRData(ESTRData):
    """ESTR data."""

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


class FREDESTRFetcher(
    Fetcher[FREDESTRQueryParams, List[Dict[str, List[FREDESTRData]]]]
):
    """FRED ESTR Fetcher."""

    data_type = FREDESTRData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDESTRQueryParams:
        return FREDESTRQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDESTRQueryParams, credentials: Optional[Dict[str, str]], **kwargs: Any
    ) -> dict:
        key = credentials.get("fred_api_key") if credentials else ""
        fred_series = ESTR_PARAMETER_TO_ID[query.parameter]
        fred = Fred(key)
        data = fred.get_series(fred_series, query.start_date, query.end_date, **kwargs)
        return data

    @staticmethod
    def transform_data(data: dict) -> List[Dict[str, List[FREDESTRData]]]:
        keys = ["date", "value"]
        return [FREDESTRData(**{k: x[k] for k in keys}) for x in data]
