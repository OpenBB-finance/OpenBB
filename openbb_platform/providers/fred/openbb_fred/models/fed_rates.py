"""FRED FED Model."""

from typing import Any, Dict, List, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.fed_rates import (
    FEDData,
    FEDQueryParams,
)
from openbb_fred.utils.fred_base import Fred
from pydantic import Field, field_validator

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
    """FRED FED Query."""

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
    """FRED FED Data."""

    __alias_dict__ = {"rate": "value"}

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FREDFEDFetcher(Fetcher[FREDFEDQueryParams, List[Dict[str, List[FREDFEDData]]]]):
    """FRED FED Model."""

    data_type = FREDFEDData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDFEDQueryParams:
        """Transform query."""
        return FREDFEDQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDFEDQueryParams, credentials: Optional[Dict[str, str]], **kwargs: Any
    ) -> dict:
        """Extract data."""
        key = credentials.get("fred_api_key") if credentials else ""
        fred_series = FED_PARAMETER_TO_FRED_ID[query.parameter]
        fred = Fred(key)
        data = fred.get_series(fred_series, query.start_date, query.end_date, **kwargs)
        return data

    @staticmethod
    def transform_data(
        query: FREDFEDQueryParams, data: dict, **kwargs: Any
    ) -> List[Dict[str, List[FREDFEDData]]]:
        """Transform data."""
        keys = ["date", "value"]
        return [FREDFEDData(**{k: x[k] for k in keys}) for x in data]
