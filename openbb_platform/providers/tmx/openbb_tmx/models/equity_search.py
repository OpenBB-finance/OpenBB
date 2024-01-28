"""TMX Equity Search fetcher."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from openbb_tmx.utils.helpers import get_all_tmx_companies
from pandas import DataFrame
from pydantic import Field


class TmxEquitySearchQueryParams(EquitySearchQueryParams):
    """TMX Equity Search query.

    Source: https://www.tmx.com/
    """

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request. The list of companies is cached for two days.",
    )


class TmxEquitySearchData(EquitySearchData):
    """TMX Equity Search Data."""


class TmxEquitySearchFetcher(
    Fetcher[
        TmxEquitySearchQueryParams,
        List[TmxEquitySearchData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxEquitySearchQueryParams:
        """Transform the query."""
        return TmxEquitySearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEquitySearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""

        companies = await get_all_tmx_companies(use_cache=query.use_cache)
        results = DataFrame(index=companies, data=companies.values(), columns=["name"])
        results = results.reset_index().rename(columns={"index": "symbol"})

        if query:
            results = results[
                results["name"].str.contains(query.query, case=False)
                | results["symbol"].str.contains(query.query, case=False)
            ]

        return results.reset_index(drop=True).astype(str).to_dict("records")

    @staticmethod
    def transform_data(
        query: TmxEquitySearchQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[TmxEquitySearchData]:
        """Transform the data to the standard format."""
        return [TmxEquitySearchData.model_validate(d) for d in data]
