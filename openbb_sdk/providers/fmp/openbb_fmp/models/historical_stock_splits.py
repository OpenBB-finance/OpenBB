"""FMP Historical Stock Splits fetcher."""


from datetime import datetime
from typing import Any, Dict, List, Optional

from openbb_fmp.utils.helpers import create_url, get_data_many
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.historical_stock_splits import (
    HistoricalStockSplitsData,
    HistoricalStockSplitsQueryParams,
)
from pydantic import validator


class FMPHistoricalStockSplitsQueryParams(HistoricalStockSplitsQueryParams):
    """FMP Historical Stock Splits Query.

    Source: https://site.financialmodelingprep.com/developer/docs/historical-stock-splits-api/
    """


class FMPHistoricalStockSplitsData(HistoricalStockSplitsData):
    """FMP Historical Stock Splits Data."""

    @validator("date", pre=True, check_fields=False)
    def date_validate(cls, v: str):  # pylint: disable=E0213
        """Return the date as a datetime object."""
        return datetime.strptime(v, "%Y-%m-%d") if v else None


class FMPHistoricalStockSplitsFetcher(
    Fetcher[
        FMPHistoricalStockSplitsQueryParams,
        List[FMPHistoricalStockSplitsData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPHistoricalStockSplitsQueryParams:
        """Transform the query params."""
        return FMPHistoricalStockSplitsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FMPHistoricalStockSplitsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        url = create_url(
            3, f"historical-price-full/stock_split/{query.symbol}", api_key
        )

        return get_data_many(url, "historical", **kwargs)

    @staticmethod
    def transform_data(data: List[Dict]) -> List[FMPHistoricalStockSplitsData]:
        """Return the transformed data."""
        return [FMPHistoricalStockSplitsData.parse_obj(d) for d in data]
