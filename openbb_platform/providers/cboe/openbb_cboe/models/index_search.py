"""CBOE Index Search Model."""

# pylint: disable=unused-argument

from datetime import time
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_search import (
    IndexSearchData,
    IndexSearchQueryParams,
)
from pydantic import Field


class CboeIndexSearchQueryParams(IndexSearchQueryParams):
    """CBOE Index Search Query.

    Source: https://www.cboe.com/
    """

    use_cache: bool = Field(
        default=True,
        description="When True, the Cboe Index directory will be cached for 24 hours."
        + " Set as False to bypass.",
    )


class CboeIndexSearchData(IndexSearchData):
    """CBOE Index Search Data."""

    __alias_dict__ = {
        "symbol": "index_symbol",
        "data_delay": "mkt_data_delay",
        "open_time": "calc_start_time",
        "close_time": "calc_end_time",
    }

    description: str | None = Field(
        description="Description for the index.", default=None
    )
    data_delay: int | None = Field(
        description="Data delay for the index. Valid only for US indices.", default=None
    )
    currency: str | None = Field(description="Currency for the index.", default=None)
    time_zone: str | None = Field(
        description="Time zone for the index. Valid only for US indices.", default=None
    )
    open_time: time | None = Field(
        description="Opening time for the index. Valid only for US indices.",
        default=None,
    )
    close_time: time | None = Field(
        description="Closing time for the index. Valid only for US indices.",
        default=None,
    )
    tick_days: str | None = Field(
        description="The trading days for the index. Valid only for US indices.",
        default=None,
    )
    tick_frequency: str | None = Field(
        description="Tick frequency for the index. Valid only for US indices.",
        default=None,
    )
    tick_period: str | None = Field(
        description="Tick period for the index. Valid only for US indices.",
        default=None,
    )


class CboeIndexSearchFetcher(
    Fetcher[
        CboeIndexSearchQueryParams,
        list[CboeIndexSearchData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CboeIndexSearchQueryParams:
        """Transform the query."""
        return CboeIndexSearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CboeIndexSearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the CBOE endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_cboe.utils.helpers import get_index_directory

        symbols = await get_index_directory(use_cache=query.use_cache, **kwargs)
        symbols.drop(columns=["source"], inplace=True)
        if query.is_symbol is True:
            result = symbols[
                symbols["index_symbol"].str.contains(query.query, case=False)
            ]
        else:
            result = symbols[
                symbols["name"].str.contains(query.query, case=False)
                | symbols["index_symbol"].str.contains(query.query, case=False)
                | symbols["description"].str.contains(query.query, case=False)
            ]

        return result.to_dict("records")

    @staticmethod
    def transform_data(
        query: CboeIndexSearchQueryParams, data: list[dict], **kwargs: Any
    ) -> list[CboeIndexSearchData]:
        """Transform the data to the standard format."""
        return [CboeIndexSearchData.model_validate(d) for d in data]
