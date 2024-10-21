"""FMP Equity Ownership Model."""

# pylint: disable=unused-argument

import asyncio
from datetime import date, datetime
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_fmp.utils.helpers import create_url, response_callback
from pandas.tseries.offsets import BDay


class FMPSenateTradingRSSQueryParams(QueryParams):
    """FMP Senate Trading RSS Query.
       Returns senate trades for the last 100 days.
       The FMP api does not put any specific constraints, but it has a counterintuitive 'page'
       parameter with no particular ranges defined


    There is currently no FMP documentation on this

    Source: https://site.financialmodelingprep.com/developer/docs#senate-trading
    """


class FMPSenateTradingRSSData(Data):
    """FMP Senate Trading Data."""
    __alias_dict__ = {"dateRecieved": "dateReceived"}


class FMPSenateTradingRSSFetcher(
    Fetcher[
        FMPSenateTradingRSSQueryParams,
        List[FMPSenateTradingRSSData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPSenateTradingRSSQueryParams:
        """Transform the query params."""
        return FMPSenateTradingRSSQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPSenateTradingRSSQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        results: List[dict] = []

        async def get_one():
            """Get data for one symbol."""
            url = create_url(4, 'senate-trading-rss-feed', api_key, query, ["symbol"])
            url += "&page=0"
            result = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if not result or len(result) == 0:
                warn(f"Symbol Error: No data found for {query.symbol}")
            if result:
                results.extend(result)

        # include both hor and senate
        await asyncio.gather(*[get_one()])

        if not results:
            raise EmptyDataError("No data returned for the given symbols.")

        return sorted(results, key=lambda x: (x["transactionDate"]), reverse=True)

    @staticmethod
    def transform_data(
        query: FMPSenateTradingRSSQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPSenateTradingRSSData]:
        """Return the transformed data."""
        results: List[FMPSenateTradingRSSData] = []
        for item in data:

            new_item = {k: v for k, v in item.items()}
            results.append(FMPSenateTradingRSSData.model_validate(new_item))
        return results
