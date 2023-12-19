"""FRED ESTR Model."""

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.estr_rates import ESTRData, ESTRQueryParams
from openbb_fred.utils.fred_base import Fred
from pydantic import Field, field_validator

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
    """FRED ESTR Query."""

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
    """FRED ESTR Data."""

    __alias_dict__ = {"rate": "value"}

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FREDESTRFetcher(
    Fetcher[FREDESTRQueryParams, List[Dict[str, List[FREDESTRData]]]]
):
    """Transform the query, extract and transform the data from the FRED endpoints."""

    data_type = FREDESTRData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDESTRQueryParams:
        """Transform query"""
        return FREDESTRQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDESTRQueryParams, credentials: Optional[Dict[str, str]], **kwargs: Any
    ) -> dict:
        """Extract data"""
        key = credentials.get("fred_api_key") if credentials else ""
        fred_series = ESTR_PARAMETER_TO_ID[query.parameter]
        fred = Fred(key)
        data = fred.get_series(fred_series, query.start_date, query.end_date, **kwargs)
        return data

    @staticmethod
    def transform_data(
        query: FREDESTRQueryParams, data: dict, **kwargs: Any
    ) -> List[Dict[str, List[FREDESTRData]]]:
        """Transform data"""
        keys = ["date", "value"]
        return [FREDESTRData(**{k: x[k] for k in keys}) for x in data]
