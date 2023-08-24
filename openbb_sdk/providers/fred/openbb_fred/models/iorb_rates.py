"""FRED FED Fetcher."""


from typing import Any, Dict, List, Optional

from openbb_fred.utils.fred_base import Fred
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.iorb_rates import (
    IORBData,
    IORBQueryParams,
)
from pydantic import validator


class FREDIORBQueryParams(IORBQueryParams):
    """IORB query."""


class FREDIORBData(IORBData):
    """IORB data."""

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


class FREDIORBFetcher(
    Fetcher[FREDIORBQueryParams, List[Dict[str, List[FREDIORBData]]]]
):
    """FRED IORB Fetcher."""

    data_type = FREDIORBData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDIORBQueryParams:
        return FREDIORBQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDIORBQueryParams, credentials: Optional[Dict[str, str]], **kwargs: Any
    ) -> dict:
        key = credentials.get("fred_api_key") if credentials else ""
        fred_series = "IORB"
        fred = Fred(key)
        data = fred.get_series(fred_series, query.start_date, query.end_date, **kwargs)
        return data

    @staticmethod
    def transform_data(data: dict) -> List[Dict[str, List[FREDIORBData]]]:
        keys = ["date", "value"]
        return [FREDIORBData(**{k: x[k] for k in keys}) for x in data]
