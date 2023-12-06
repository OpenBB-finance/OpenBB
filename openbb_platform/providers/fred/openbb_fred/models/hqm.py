"""FRED High Quality Market Corporate Bond Model."""


from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.hqm import (
    HighQualityMarketCorporateBondData,
    HighQualityMarketCorporateBondQueryParams,
)
from openbb_fred.utils.fred_base import Fred
from openbb_fred.utils.fred_helpers import (
    YIELD_CURVE_SERIES_CORPORATE_PAR,
    YIELD_CURVE_SERIES_CORPORATE_SPOT,
)
from pydantic import field_validator


class FREDHighQualityMarketCorporateBondQueryParams(
    HighQualityMarketCorporateBondQueryParams
):
    """FRED High Quality Market Corporate Bond Query."""


class FREDHighQualityMarketCorporateBondData(HighQualityMarketCorporateBondData):
    """FRED High Quality Market Corporate Bond Data."""

    __alias_dict__ = {"rate": "value"}

    @field_validator("rate", mode="before", check_fields=False)
    @classmethod
    def value_validate(cls, v):
        """Validate rate."""
        try:
            return float(v)
        except ValueError:
            return None


class FREDHighQualityMarketCorporateBondFetcher(
    Fetcher[
        FREDHighQualityMarketCorporateBondQueryParams,
        List[FREDHighQualityMarketCorporateBondData],
    ]
):
    """Transform the query, extract and transform the data from the FRED endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> FREDHighQualityMarketCorporateBondQueryParams:
        """Transform query."""
        return FREDHighQualityMarketCorporateBondQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FREDHighQualityMarketCorporateBondQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any
    ) -> list:
        """Extract data."""
        key = credentials.get("fred_api_key") if credentials else ""
        fred = Fred(key)

        data = []

        today = datetime.today().date()
        if query.date and query.date >= today:
            raise ValueError("Date must be in the past.")

        start_date = (
            query.date - timedelta(days=50)
            if query.date
            else today - timedelta(days=50)
        )

        if query.yield_curve == "spot":
            fred_series = YIELD_CURVE_SERIES_CORPORATE_SPOT
        elif query.yield_curve == "par":
            fred_series = YIELD_CURVE_SERIES_CORPORATE_PAR
        else:
            raise ValueError("Invalid yield curve type.")

        for maturity, id_ in fred_series.items():
            d = fred.get_series(
                series_id=id_,
                start_date=start_date,
                **kwargs,
            )
            for item in d:
                item["maturity"] = maturity
                item["yield_curve"] = query.yield_curve
            data.extend(d)

        return data

    @staticmethod
    def transform_data(
        query: FREDHighQualityMarketCorporateBondQueryParams, data: list, **kwargs: Any
    ) -> List[FREDHighQualityMarketCorporateBondData]:
        """Transform data."""
        return [FREDHighQualityMarketCorporateBondData.model_validate(d) for d in data]
