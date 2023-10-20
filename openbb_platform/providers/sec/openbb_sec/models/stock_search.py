"""SEC Company Search fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_search import (
    StockSearchData,
    StockSearchQueryParams,
)
from openbb_sec.utils.helpers import get_all_companies
from pydantic import Field


class SecStockSearchQueryParams(StockSearchQueryParams):
    """SEC Company Search query.

    Source: https://sec.gov/
    """

    use_cache: bool = Field(
        default=True,
        description="Whether to use the cache or not. Company names, tickers, and CIKs are cached for seven days.",
    )


class SecStockSearchData(StockSearchData):
    """SEC Company Search Data."""

    cik: str = Field(description="Central Index Key")


class SecStockSearchFetcher(
    Fetcher[
        SecStockSearchQueryParams,
        List[SecStockSearchData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SecStockSearchQueryParams:
        """Transform the query."""
        return SecStockSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: SecStockSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the SEC endpoint."""
        companies = get_all_companies(use_cache=query.use_cache)

        results = (
            companies["name"].str.contains(query.query, case=False)
            | companies["symbol"].str.contains(query.query, case=False)
            | companies["cik"].str.contains(query.query, case=False)
        )

        return companies[results].astype(str).to_dict("records")

    @staticmethod
    def transform_data(data: Dict, **kwargs: Any) -> List[SecStockSearchData]:
        """Transform the data to the standard format."""
        return [SecStockSearchData.model_validate(d) for d in data]
