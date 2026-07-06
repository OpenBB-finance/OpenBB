"""Yahoo Finance Futures Expirations Model."""

# pylint: disable=unused-argument

import asyncio
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_expirations import (
    FuturesExpirationsData,
    FuturesExpirationsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError


class YFinanceFuturesExpirationsQueryParams(FuturesExpirationsQueryParams):
    """Yahoo Finance Futures Expirations Query.

    Source: https://finance.yahoo.com/
    """


class YFinanceFuturesExpirationsData(FuturesExpirationsData):
    """Yahoo Finance Futures Expirations Data."""


class YFinanceFuturesExpirationsFetcher(
    Fetcher[
        YFinanceFuturesExpirationsQueryParams,
        list[YFinanceFuturesExpirationsData],
    ]
):
    """YFinance Futures Expirations Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> YFinanceFuturesExpirationsQueryParams:
        """Transform the query."""
        return YFinanceFuturesExpirationsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceFuturesExpirationsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Extract futures expiration data from Yahoo."""
        # pylint: disable=import-outside-toplevel
        from openbb_yfinance.utils.helpers import get_futures_expirations

        data = await asyncio.to_thread(get_futures_expirations, query.symbol)

        if not data:
            raise EmptyDataError()

        return data

    @staticmethod
    def transform_data(
        query: YFinanceFuturesExpirationsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[YFinanceFuturesExpirationsData]:
        """Transform the data to the standard format."""
        return [YFinanceFuturesExpirationsData.model_validate(d) for d in data]
