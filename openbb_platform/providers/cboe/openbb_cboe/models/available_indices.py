"""Cboe Available Indices Model."""

# pylint: disable=unused-argument

from datetime import time
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.available_indices import (
    AvailableIndicesData,
    AvailableIndicesQueryParams,
)
from pydantic import Field


class CboeAvailableIndicesQueryParams(AvailableIndicesQueryParams):
    """Cboe Available Indices Query.

    Source: https://www.cboe.com/
    """

    use_cache: bool = Field(
        default=True,
        description="When True, the Cboe Index directory will be cached for 24 hours."
        + " Set as False to bypass.",
    )


class CboeAvailableIndicesData(AvailableIndicesData):
    """Cboe Available Indices Data.

    Source: https://www.cboe.com/
    """

    __alias_dict__ = {
        "symbol": "index_symbol",
        "data_delay": "mkt_data_delay",
        "open_time": "calc_start_time",
        "close_time": "calc_end_time",
    }

    symbol: str | None = Field(description="Symbol for the index.")

    description: str | None = Field(
        default=None,
        description="Description for the index. Valid only for US indices.",
    )

    data_delay: int | None = Field(
        default=None, description="Data delay for the index. Valid only for US indices."
    )

    open_time: time | None = Field(
        default=None,
        description="Opening time for the index. Valid only for US indices.",
    )

    close_time: time | None = Field(
        default=None,
        description="Closing time for the index. Valid only for US indices.",
    )

    time_zone: str | None = Field(
        default=None, description="Time zone for the index. Valid only for US indices."
    )

    tick_days: str | None = Field(
        default=None,
        description="The trading days for the index. Valid only for US indices.",
    )

    tick_frequency: str | None = Field(
        default=None,
        description="The frequency of the index ticks. Valid only for US indices.",
    )

    tick_period: str | None = Field(
        default=None,
        description="The period of the index ticks. Valid only for US indices.",
    )


class CboeAvailableIndicesFetcher(
    Fetcher[
        CboeAvailableIndicesQueryParams,
        list[CboeAvailableIndicesData],
    ]
):
    """Transform the query, extract and transform the data from the CBOE endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> CboeAvailableIndicesQueryParams:
        """Transform the query params."""
        return CboeAvailableIndicesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: CboeAvailableIndicesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the CBOE endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_cboe.utils.helpers import get_index_directory

        data = await get_index_directory(use_cache=query.use_cache, **kwargs)
        return data.to_dict("records")

    @staticmethod
    def transform_data(
        query: CboeAvailableIndicesQueryParams, data: list[dict], **kwargs: Any
    ) -> list[CboeAvailableIndicesData]:
        """Transform the data to the standard format."""
        return [CboeAvailableIndicesData.model_validate(d) for d in data]
