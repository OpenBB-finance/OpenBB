"""FRED FED Fetcher."""


from typing import Any, Dict, List, Literal, Optional

from openbb_fred.utils.fred_base import Fred
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.fed_rates import (
    FEDData,
    FEDQueryParams,
)
from pydantic import Field, validator

FED_PARAMETER_TO_FRED_ID = {
    "monthly": "FEDFUNDS",
    "daily": "DFF",
    "weekly": "FF",
    "daily_excl_weekend": "RIFSPFFNB",
    "annual": "RIFSPFFNA",
    "biweekly": "RIFSPFFNBWAW",
    "volume": "EFFRVOL",
}


class FREDFEDQueryParams(FEDQueryParams):
    """FED query."""

    parameter: Literal[
        "monthly",
        "daily",
        "weekly",
        "daily_excl_weekend",
        "annual",
        "biweekly",
        "volume",
    ] = Field(default="weekly", description="Period of FED rate.")


class FREDFEDData(FEDData):
    """FED data."""

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


class FREDFEDFetcher(Fetcher[FREDFEDQueryParams, List[Dict[str, List[FREDFEDData]]]]):
    """FRED FED Fetcher."""

    data_type = FREDFEDData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDFEDQueryParams:
        return FREDFEDQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDFEDQueryParams, credentials: Optional[Dict[str, str]], **kwargs: Any
    ) -> dict:
        key = credentials.get("fred_api_key") if credentials else ""
        fred_series = FED_PARAMETER_TO_FRED_ID[query.parameter]
        fred = Fred(key)
        data = fred.get_series(fred_series, query.start_date, query.end_date, **kwargs)
        return data

    @staticmethod
    def transform_data(data: dict) -> List[Dict[str, List[FREDFEDData]]]:
        keys = ["date", "value"]
        return [FREDFEDData(**{k: x[k] for k in keys}) for x in data]
