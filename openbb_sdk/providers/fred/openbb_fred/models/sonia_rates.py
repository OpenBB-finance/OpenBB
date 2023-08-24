"""FRED SONIA Fetcher."""


from typing import Any, Dict, List, Literal, Optional

from openbb_fred.utils.fred_base import Fred
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.sonia_rates import SONIAData, SONIAQueryParams
from pydantic import Field, validator

SONIA_PARAMETER_TO_FRED_ID = {
    "rate": "IUDSOIA",
    "index": "IUDZOS2",
    "10th_percentile": "IUDZLS6",
    "25th_percentile": "IUDZLS7",
    "75th_percentile": "IUDZLS8",
    "90th_percentile": "IUDZLS9",
    "total_nominal_value": "IUDZLT2",
}


class FREDSONIAQueryParams(SONIAQueryParams):
    """SONIA query."""

    parameter: Literal[
        "rate",
        "index",
        "10th_percentile",
        "25th_percentile",
        "75th_percentile",
        "90th_percentile",
        "total_nominal_value",
    ] = Field(default="rate", description="Period of SONIA rate.")


class FREDSONIAData(SONIAData):
    """SONIA data."""

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


class FREDSONIAFetcher(
    Fetcher[FREDSONIAQueryParams, List[Dict[str, List[FREDSONIAData]]]]
):
    """FRED SONIA Fetcher."""

    data_type = FREDSONIAData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDSONIAQueryParams:
        return FREDSONIAQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDSONIAQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> dict:
        key = credentials.get("fred_api_key") if credentials else ""
        fred_series = SONIA_PARAMETER_TO_FRED_ID[query.parameter]
        fred = Fred(key)
        data = fred.get_series(fred_series, query.start_date, query.end_date, **kwargs)
        return data

    @staticmethod
    def transform_data(data: dict) -> List[Dict[str, List[FREDSONIAData]]]:
        keys = ["date", "value"]
        return [FREDSONIAData(**{k: x[k] for k in keys}) for x in data]
