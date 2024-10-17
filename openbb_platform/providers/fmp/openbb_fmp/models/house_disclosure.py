import asyncio
from typing import List, Optional, Dict, Any
from warnings import warn

from pydantic import Field

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.house_disclosure import HouseDisclosureQueryParams, HouseDisclosureData
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request
from openbb_fmp.utils.helpers import create_url, response_callback

class FMPHouseDisclosureQueryParams(HouseDisclosureQueryParams):
    """House Disclosure Query Parameters.

    Source: https://financialmodelingprep.com/api/v4/senate-disclosure
    """


class FMPHouseDisclosureData(HouseDisclosureData):
    """House Disclosure Data Model."""
    __alias_dict__ = {"symbol": "ticker"}


class FMPHouseDisclosureFetcher(Fetcher[
        FMPHouseDisclosureQueryParams,
        List[FMPHouseDisclosureData],
    ]
):
    """Fetches and transforms data from the House Disclosure endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPHouseDisclosureQueryParams:
        """Transform the query params."""
        return FMPHouseDisclosureQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPHouseDisclosureQueryParams,
        credentials: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the House Disclosure endpoint."""
        api_key = credentials.get("fmp_api_key") if credentials else ""
        symbols = query.symbol.split(",")
        results: List[Dict] = []

        async def get_one(symbol):
            """Get data for the given symbol."""
            query_ = FMPHouseDisclosureQueryParams(symbol=symbol)
            url = create_url(4, "senate-disclosure", api_key, query_)
            result = await amake_request(
                url, response_callback=response_callback, **kwargs
            )
            if not result or len(result) == 0:
                warn(f"Symbol Error: No data found for symbol {symbol}")
            if result:
                results.extend(result)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No data returned for the given symbol.")

        return results

    @staticmethod
    def transform_data(
        query: FMPHouseDisclosureQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[HouseDisclosureData]:
        """Return the transformed data."""
        return [FMPHouseDisclosureData(**d) for d in data]
