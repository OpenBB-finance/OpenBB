"""FMP Equity Ownership Model."""

# pylint: disable=unused-argument

import asyncio
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_fmp.utils.helpers import create_url, response_callback
from pydantic import Field, field_validator


class FMPCongressTradingHistoricalQueryParams(QueryParams):
    """FMP Congress Trading Query.
       Returns senate and hor trading for a given ticker

    Source: https://site.financialmodelingprep.com/developer/docs#senate-trading
            https://site.financialmodelingprep.com/developer/docs/senate-disclosure-api (this is actuall HOR disclosures)
    """

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": False}}

class FMPCongressTradingHistoricalData(Data):
    """FMP Senate Trading Data."""

class FMPCongressTradingHistoricalFetcher(
    Fetcher[
        FMPCongressTradingHistoricalQueryParams,
        List[FMPCongressTradingHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the FMP endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPCongressTradingHistoricalQueryParams:
        """Transform the query params."""
        return FMPCongressTradingHistoricalQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPCongressTradingHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the FMP endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""

        results: List[dict] = []

        async def get_one(endpoint):
            """Get data for one symbol."""
            url = create_url(
            4, 'senate-trading', api_key, query, ["symbol"]
            )
            url += f"&symbol={query.symbol}"
            print(f'url:{url}')
            result = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if not result or len(result) == 0:
                warn(f"Symbol Error: No data found for {query.symbol}")
            if result:
                results.extend(result)

        # include both hor and senate
        await asyncio.gather(*[get_one(ep) for ep in ['senate-trading', 'senate-disclosure']])

        if not results:
            raise EmptyDataError("No data returned for the given symbols.")

        return sorted(
            results, key=lambda x: (x["transactionDate"]), reverse=True
        )

    @staticmethod
    def transform_data(
        query: FMPCongressTradingHistoricalQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPCongressTradingHistoricalData]:
        """Return the transformed data."""
        def _map_hor(item):
            return dict(ticker=item.get('ticker', ''),
                        filer=item.get('representative' ,''),
                        transactionDate=item.get('transactionDate', ''),
                        type=item.get('type', ''),
                        amount=item.get('amount', ''),
                        filingDate=item.get('disclosureDate'),
                        source='HouseOfRepresentative'
                        )

        def _map_senate(item):
            return dict(ticker=item.get('ticker', ''),
                        filer=f"{item.get('firstName' ,'')},{item.get('lastName' ,'')}",
                        transactionDate=item.get('transactionDate', ''),
                        type=item.get('type', ''),
                        amount=item.get('amount', ''),
                        filingDate=item.get('dateRecieved'),
                        source='Senate'
                        )

        results: List[FMPCongressTradingHistoricalData] = []
        for item in data:
            new_item = _map_hor(item) if 'disclosureYear' in item.keys() else _map_senate(item)
            results.append(FMPCongressTradingHistoricalData.model_validate(new_item))
        return results
