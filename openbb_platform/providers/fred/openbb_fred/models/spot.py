"""SpotRate Fetcher."""


from typing import Any, Dict, List, Optional

from openbb_fred.utils.fred_base import Fred
from openbb_fred.utils.fred_helpers import get_spot_series_id
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.spot import (
    SpotRateData,
    SpotRateParams,
)
from pydantic import field_validator


class FREDSpotRateParams(SpotRateParams):
    """SpotRateParams Query."""


class FREDSpotRateData(SpotRateData):
    """SpotRateParams Data."""

    __alias_dict__ = {"rate": "value"}

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FREDSpotRateFetcher(
    Fetcher[
        FREDSpotRateParams,
        List[FREDSpotRateData],
    ]
):
    """SpotRateParams Fetcher."""

    data_type = FREDSpotRateData

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FREDSpotRateParams:
        """Transform query."""
        return FREDSpotRateParams(**params)

    @staticmethod
    def extract_data(
        query: FREDSpotRateParams, credentials: Optional[Dict[str, str]], **kwargs: Any
    ) -> list:
        """Extract data."""
        key = credentials.get("fred_api_key") if credentials else ""
        fred = Fred(key)

        series = get_spot_series_id(
            maturity=query.maturity,
            category=query.category,
        )

        data = []

        for s in series:
            id_ = s["FRED Series ID"]
            title = s["Title"]
            d = fred.get_series(
                series_id=id_,
                start_date=query.start_date,
                end_date=query.end_date,
                **kwargs,
            )
            for item in d:
                item["title"] = title
            data.extend(d)

        return data

    @staticmethod
    def transform_data(
        query: FREDSpotRateParams, data: list, **kwargs: Any
    ) -> List[FREDSpotRateData]:
        """Transform data."""
        return [FREDSpotRateData.model_validate(d) for d in data]
