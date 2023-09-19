"""CBOE Index Search fetcher."""

from datetime import time
from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_cboe.utils.helpers import Europe, get_cboe_index_directory
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.index_search import (
    IndexSearchData,
    IndexSearchQueryParams,
)
from pydantic import Field


class CboeIndexSearchQueryParams(IndexSearchQueryParams):
    """CBOE Index Search query.  Search the CBOE company directory by name or ticker.

    Source: https://www.cboe.com/
    """

    europe: bool = Field(
        description="Filter for European indices. False for US indices.", default=False
    )


class CboeIndexSearchData(IndexSearchData):
    """CBOE Company Search Data."""

    isin: Optional[str] = Field(
        description="ISIN code for the index. Valid only for European indices."
    )
    region: Optional[str] = Field(
        description="Region for the index. Valid only for European indices"
    )
    description: Optional[str] = Field(description="Description for the index.")
    data_delay: Optional[int] = Field(
        description="Data delay for the index. Valid only for US indices."
    )
    currency: Optional[str] = Field(description="Currency for the index.")
    time_zone: Optional[str] = Field(
        description="Time zone for the index. Valid only for US indices."
    )
    open_time: Optional[time] = Field(
        description="Opening time for the index. Valid only for US indices."
    )
    close_time: Optional[time] = Field(
        description="Closing time for the index. Valid only for US indices."
    )
    tick_days: Optional[str] = Field(
        description="The trading days for the index. Valid only for US indices."
    )
    tick_frequency: Optional[str] = Field(
        description="Tick frequency for the index. Valid only for US indices."
    )
    tick_period: Optional[str] = Field(
        description="Tick period for the index. Valid only for US indices."
    )


class CboeIndexSearchFetcher(
    Fetcher[
        CboeIndexSearchQueryParams,
        List[CboeIndexSearchData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> CboeIndexSearchQueryParams:
        """Transform the query."""
        return CboeIndexSearchQueryParams(**params)

    @staticmethod
    def extract_data(
        query: CboeIndexSearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the CBOE endpoint."""
        symbols = pd.DataFrame()
        if query.europe is True:
            symbols = pd.DataFrame(Europe.list_indices())
        if query.europe is False:
            symbols = get_cboe_index_directory().reset_index()

        target = "name" if not query.symbol else "symbol"
        idx = symbols[target].str.contains(query.query, case=False)
        result = symbols[idx]

        return result.to_dict("records")

    @staticmethod
    def transform_data(data: dict) -> List[CboeIndexSearchData]:
        """Transform the data to the standard format."""
        return [CboeIndexSearchData.parse_obj(d) for d in data]
