"""CBOE Company Search fetcher."""


from typing import Any, Dict, List, Optional

from openbb_cboe.utils.helpers import get_cboe_directory
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_search import (
    StockSearchData,
    StockSearchQueryParams,
)
from pydantic import Field


class CboeStockSearchQueryParams(StockSearchQueryParams):
    """CBOE Company Search query.

    Source: https://www.cboe.com/
    """


class CboeStockSearchData(StockSearchData):
    """CBOE Company Search Data."""

    dpm_name: Optional[str] = Field(description="Name of the primary market maker.")
    post_station: Optional[str] = Field(
        description="Post and station location on the CBOE trading floor."
    )


class CboeStockSearchFetcher(
    Fetcher[
        CboeStockSearchQueryParams,
        List[CboeStockSearchData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeStockSearchQueryParams:
        """Transform the query."""
        return CboeStockSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeStockSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the CBOE endpoint."""

        data = {}
        symbols = get_cboe_directory().reset_index()
        target = "name" if not query.ticker else "symbol"
        idx = symbols[target].str.contains(query.query, case=False)
        result = symbols[idx].to_dict("records")
        data.update({"results": result})

        return data

    @staticmethod
    def transform_data(data: dict) -> List[CboeStockSearchData]:
        """Transform the data to the standard format."""
        return [CboeStockSearchData.parse_obj(d) for d in data["results"]]
