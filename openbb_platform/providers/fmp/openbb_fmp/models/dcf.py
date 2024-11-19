"""Dcf Model."""

import asyncio
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.dcf import (
    DcfData,
    DcfQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_fmp.utils.helpers import create_url
from pydantic import Field


class FMPDcfQueryParams(DcfQueryParams):
    """Dcf Query Parameters.

    Source: https://financialmodelingprep.com/api/v3/discounted-cash-flow/AAPL
    """


class FMPDcfData(DcfData):
    """Dcf Data Model."""

    __alias_dict__ = {
        "stock_price": "Stock Price",
    }
    stock_price: Optional[float] = Field(default=None, description="Stock Price.")


class FMPDcfFetcher(
    Fetcher[
        FMPDcfQueryParams,
        List[FMPDcfData],
    ]
):
    """Fetches and transforms data from the Dcf endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPDcfQueryParams:
        """Transform the query params."""
        return FMPDcfQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPDcfQueryParams,
        credentials: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Dcf endpoint."""
        symbols = query.symbol.split(",")
        results: List[Dict] = []

        async def get_one(symbol):
            """Get data for the given symbol."""
            api_key = credentials.get("fmp_api_key") if credentials else ""
            url = create_url(
                3, f"discounted-cash-flow/{symbol}", api_key, query, exclude=["symbol"]
            )
            result = await amake_request(url, **kwargs)
            if not result or len(result) == 0:
                warn(f"Symbol Error: No data found for symbol {symbol}")
            if result:
                results.extend(result)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        results = [i for i in results if isinstance(i, dict)]
        if not results:
            raise EmptyDataError("No data returned for the given symbol.")

        return results

    @staticmethod
    def transform_data(
        query: FMPDcfQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPDcfData]:
        """Return the transformed data."""
        return [FMPDcfData(**d) for d in data]
