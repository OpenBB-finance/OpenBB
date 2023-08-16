"""CBOE Company Search fetcher."""


from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_search import (
    StockSearchData,
    StockSearchQueryParams,
)
from pydantic import Field

from openbb_cboe.utils.helpers import stock_search


class CboeStockSearchQueryParams(StockSearchQueryParams):
    """CBOE Company Search query.

    Source: https://www.cboe.com/
    """


class CboeStockSearchData(StockSearchData):
    """CBOE Company Search Data."""

    class Config:
        """Pydantic alias config using fields dict"""

        fields = {
            "name": "Company Name",
            "symbol": "Symbol",
        }

    dpmName: Optional[str] = Field(
        description="The name of the primary market maker.",
        alias="DPM Name",
    )
    postStation: Optional[str] = Field(
        description="The post and station location on the CBOE trading floor.",
        alias="Post/Station",
    )


class CboeStockSearchFetcher(
    Fetcher[
        CboeStockSearchQueryParams,
        CboeStockSearchData,
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints"""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeStockSearchQueryParams:
        """Transform the query"""

        return CboeStockSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeStockSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[CboeStockSearchData]:
        """Return the raw data from the CBOE endpoint"""

        data = stock_search(query.query, ticker=query.ticker)

        if "results" in data:
            return data["results"]
        else:
            raise ValueError("No results found.")

    @staticmethod
    def transform_data(data: List[CboeStockSearchData]) -> List[CboeStockSearchData]:
        """Transform the data to the standard format"""

        return [CboeStockSearchData.parse_obj(d) for d in data]
