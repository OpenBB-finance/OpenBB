"""CBOE Equity Search Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from pydantic import Field


class CboeEquitySearchQueryParams(EquitySearchQueryParams):
    """CBOE Equity Search Query.

    Source: https://www.cboe.com/
    """

    use_cache: bool = Field(
        default=True,
        description="Whether to use the cache or not.",
    )


class CboeEquitySearchData(EquitySearchData):
    """CBOE Equity Search Data."""

    __alias_dict__ = {
        "dpm_name": "DPM Name",
    }

    dpm_name: str | None = Field(
        default=None,
        description="Name of the primary market maker.",
    )
    post_station: str | None = Field(
        default=None, description="Post and station location on the CBOE trading floor."
    )


class CboeEquitySearchFetcher(
    Fetcher[
        CboeEquitySearchQueryParams,
        list[CboeEquitySearchData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CboeEquitySearchQueryParams:
        """Transform the query."""
        return CboeEquitySearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CboeEquitySearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the CBOE endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_cboe.utils.helpers import get_company_directory

        data = {}
        symbols = await get_company_directory(query.use_cache, **kwargs)
        symbols = symbols.reset_index()
        target = "name" if query.is_symbol is False else "symbol"
        idx = symbols[target].str.contains(query.query, case=False)
        result = symbols[idx].to_dict("records")
        data.update({"results": result})

        return data

    @staticmethod
    def transform_data(
        query: CboeEquitySearchQueryParams, data: dict, **kwargs: Any
    ) -> list[CboeEquitySearchData]:
        """Transform the data to the standard format."""
        return [CboeEquitySearchData.model_validate(d) for d in data["results"]]
