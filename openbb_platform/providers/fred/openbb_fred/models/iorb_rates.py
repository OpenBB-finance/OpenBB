"""FRED IORB Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.iorb_rates import (
    IORBData,
    IORBQueryParams,
)
from pydantic import field_validator


class FREDIORBQueryParams(IORBQueryParams):
    """FRED IORB Query."""


class FREDIORBData(IORBData):
    """FRED IORB Data."""

    __alias_dict__ = {"rate": "value"}

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FREDIORBFetcher(Fetcher[FREDIORBQueryParams, List[FREDIORBData]]):
    """FRED IORB Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDIORBQueryParams:
        """Transform query."""
        return FREDIORBQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDIORBQueryParams, credentials: Optional[Dict[str, str]], **kwargs: Any
    ) -> Dict:
        """Extract data."""
        # pylint: disable=import-outside-toplevel
        from openbb_fred.utils.fred_base import Fred

        key = credentials.get("fred_api_key") if credentials else ""
        fred_series = "IORB"
        fred = Fred(key)
        data = fred.get_series(fred_series, query.start_date, query.end_date, **kwargs)
        return data

    @staticmethod
    def transform_data(
        query: FREDIORBQueryParams, data: Dict, **kwargs: Any
    ) -> List[FREDIORBData]:
        """Transform data."""
        keys = ["date", "value"]
        return [FREDIORBData(**{k: x[k] for k in keys}) for x in data]
