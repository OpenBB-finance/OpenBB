"""SEC Equity Search Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from pydantic import Field


class SecEquitySearchQueryParams(EquitySearchQueryParams):
    """SEC Equity Search Query.

    Source: https://sec.gov/
    """

    use_cache: bool = Field(
        default=True,
        description="Whether to use the cache or not.",
    )
    is_fund: bool = Field(
        default=False,
        description="Whether to direct the search to the list of mutual funds and ETFs.",
    )


class SecEquitySearchData(EquitySearchData):
    """SEC Equity Search Data."""

    cik: str = Field(description="Central Index Key")


class SecEquitySearchFetcher(
    Fetcher[
        SecEquitySearchQueryParams,
        List[SecEquitySearchData],
    ]
):
    """SEC Equity Search Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SecEquitySearchQueryParams:
        """Transform the query."""
        return SecEquitySearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecEquitySearchQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the SEC endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_sec.utils.helpers import (
            get_all_companies,
            get_mf_and_etf_map,
        )
        from pandas import DataFrame

        results = DataFrame()

        if query.is_fund is True:
            companies = await get_mf_and_etf_map(use_cache=query.use_cache)
            results = companies[
                companies["cik"].str.contains(query.query, case=False)
                | companies["seriesId"].str.contains(query.query, case=False)
                | companies["classId"].str.contains(query.query, case=False)
                | companies["symbol"].str.contains(query.query, case=False)
            ]

        if query.is_fund is False:
            companies = await get_all_companies(use_cache=query.use_cache)

            results = companies[
                companies["name"].str.contains(query.query, case=False)
                | companies["symbol"].str.contains(query.query, case=False)
                | companies["cik"].str.contains(query.query, case=False)
            ]

        return results.astype(str).to_dict("records")

    @staticmethod
    def transform_data(
        query: SecEquitySearchQueryParams, data: Dict, **kwargs: Any
    ) -> List[SecEquitySearchData]:
        """Transform the data to the standard format."""
        return [SecEquitySearchData.model_validate(d) for d in data]
