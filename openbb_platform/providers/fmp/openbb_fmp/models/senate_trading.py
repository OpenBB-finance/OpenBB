"""FMP Senate Trading Model."""

import asyncio
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.senate_trading import SenateTradingData, SenateTradingQueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_fmp.utils.helpers import create_url, response_callback


class FMPSenateTradingQueryParams(SenateTradingQueryParams):
    """FMP Senate Trading Query.

    Source: https://site.financialmodelingprep.com/developer/docs/senate-trading-api/
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}



class FMPSenateTradingData(SenateTradingData):
    """FMP Senate Trading Data."""


class FMPSenateTradingFetcher(Fetcher[FMPSenateTradingQueryParams, List[FMPSenateTradingData]]):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPSenateTradingQueryParams:
        """Transform the query params."""
        return FMPSenateTradingQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPSenateTradingQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = query.symbol.split(",")  # type: ignore
        results: List[dict] = []

        async def get_one(symbol):
            """Get data for one symbol."""
            query_ = FMPSenateTradingQueryParams(symbol=symbol)
            url = create_url(4, "senate-trading", api_key, query_)
            result = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if not result or len(result) == 0:
                warn(f"Symbol Error: No data found for {symbol}")
            if result:
                results.extend(result)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No data returned for the given symbol.")

        return results

    @staticmethod
    def transform_data(
        query: FMPSenateTradingQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPSenateTradingData]:
        """Return the transformed data."""
        return [FMPSenateTradingData.model_validate(d) for d in data]
