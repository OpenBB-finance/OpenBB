"""TMX Stock Search fetcher."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.stock_search import (
    StockSearchData,
    StockSearchQueryParams,
)
from openbb_tmx.utils.helpers import get_all_tmx_companies


class TmxStockSearchQueryParams(StockSearchQueryParams):
    """TMX Stock Search query.

    Source: https://www.tmx.com/
    """


class TmxStockSearchData(StockSearchData):
    """TMX Stock Search Data."""


class TmxStockSearchFetcher(
    Fetcher[
        TmxStockSearchQueryParams,
        List[TmxStockSearchData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxStockSearchQueryParams:
        """Transform the query."""
        return TmxStockSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TmxStockSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        companies = get_all_tmx_companies()
        results = pd.DataFrame(
            index=companies.keys(), data=companies.values(), columns=["name"]
        )
        results = results.reset_index().rename(columns={"index": "symbol"})

        if query:
            results = results[
                results["name"].str.contains(query.query, case=False)
                | results["symbol"].str.contains(query.query, case=False)
            ]

        return results.reset_index(drop=True).astype(str).to_dict("records")

    @staticmethod
    def transform_data(data: List[Dict]) -> List[TmxStockSearchData]:
        """Transform the data to the standard format."""
        return [TmxStockSearchData.model_validate(d) for d in data]
