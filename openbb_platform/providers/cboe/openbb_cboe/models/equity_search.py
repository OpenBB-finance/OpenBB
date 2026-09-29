"""Cboe Equity Search Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from pydantic import Field


class CboeEquitySearchQueryParams(EquitySearchQueryParams):
    """Cboe Equity Search Query.

    Source: https://www.cboe.com/
    """

    use_cache: bool = Field(
        default=True,
        description="When True, the company directory will be cached for 24 hours."
        + " Set as False to bypass.",
    )


class CboeEquitySearchData(EquitySearchData):
    """Cboe Equity Search Data."""

    __alias_dict__ = {
        "dpm_name": "DPM Name",
    }

    dpm_name: str | None = Field(
        default=None,
        description="Name of the primary market maker.",
    )
    post_station: str | None = Field(
        default=None, description="Post and station location on the Cboe trading floor."
    )


class CboeEquitySearchFetcher(
    Fetcher[
        CboeEquitySearchQueryParams,
        list[CboeEquitySearchData],
    ]
):
    """Transform the query, extract and transform the data from the Cboe endpoints."""

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
        """Return the raw data from the Cboe endpoint."""
        from openbb_cboe.utils.helpers import get_company_directory

        symbols = await get_company_directory(query.use_cache, **kwargs)
        symbols = symbols.reset_index()
        target = "name" if query.is_symbol is False else "symbol"
        idx = symbols[target].str.contains(query.query, case=False)

        return {"results": symbols[idx].to_dict("records")}

    @staticmethod
    def transform_data(
        query: CboeEquitySearchQueryParams, data: dict, **kwargs: Any
    ) -> list[CboeEquitySearchData]:
        """Transform the data to the standard format."""
        from math import isnan

        def clean_nan(d: dict) -> dict:
            """Replace nan values with None for Pydantic validation."""
            return {
                k: None if isinstance(v, float) and isnan(v) else v
                for k, v in d.items()
            }

        return [
            CboeEquitySearchData.model_validate(clean_nan(d)) for d in data["results"]
        ]
