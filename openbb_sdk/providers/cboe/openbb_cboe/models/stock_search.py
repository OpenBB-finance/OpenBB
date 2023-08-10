"""CBOE Company Search fetcher."""

# IMPORT STANDARD
from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_search import (
    StockSearchData,
    StockSearchQueryParams,
)
from pydantic import Field, validator

from openbb_cboe.utils.helpers import stock_search


class CboeStockSearchQueryParams(StockSearchQueryParams):
    """CBOE Company Search query.

    Source: https://www.cboe.com/
    """


class CboeStockSearchData(StockSearchData):
    """CBOE Company Search Data."""

    class Config:
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

    @validator("symbol", pre=True, check_fields=False)
    def name_validate(cls, v):  # pylint: disable=E0213
        return v.upper()


class CboeStockSearchFetcher(
    Fetcher[
        CboeStockSearchQueryParams,
        CboeStockSearchData,
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeStockSearchQueryParams:
        return CboeStockSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeStockSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[CboeStockSearchData]:
        data = stock_search(query.query, ticker=query.ticker)

        return [CboeStockSearchData.parse_obj(d) for d in data.get("results", [])]

    @staticmethod
    def transform_data(data: List[CboeStockSearchData]) -> List[CboeStockSearchData]:
        return data
