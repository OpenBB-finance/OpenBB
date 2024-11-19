"""Historical Rating Model."""

import asyncio
from typing import Any, Dict, List, Optional
from warnings import warn

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.rating import (
    RatingData,
    RatingQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_core.provider.utils.helpers import amake_request, to_snake_case
from openbb_fmp.utils.helpers import create_url


class FMPHistoricalRatingQueryParams(RatingQueryParams):
    """Historical Rating Query Parameters.

    Source: https://financialmodelingprep.com/api/v3/historical-rating/AAPLL
    """


class FMPHistoricalRatingData(RatingData):
    """Historical Rating Data Model."""

    __alias_dict__ = {
        "symbol": "ticker",
    }


class FMPHistoricalRatingFetcher(
    Fetcher[
        FMPHistoricalRatingQueryParams,
        List[FMPHistoricalRatingData],
    ]
):
    """Fetches and transforms data from the Historical Rating endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FMPHistoricalRatingQueryParams:
        """Transform the query params."""
        return FMPHistoricalRatingQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPHistoricalRatingQueryParams,
        credentials: Optional[Dict[str, str]] = None,
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Historical Rating endpoint."""
        symbols = query.symbol.split(",")
        results: List[Dict] = []

        async def get_one(symbol):
            api_key = credentials.get("fmp_api_key") if credentials else ""
            url = create_url(
                3, f"historical-rating/{symbol}", api_key, query, exclude=["symbol"]
            )
            result = await amake_request(url, **kwargs)
            if not result or len(result) == 0:
                warn(f"Symbol Error: No data found for symbol {symbol}")
            if result:
                results.extend(result)

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])
        results = [
            {to_snake_case(key): value for key, value in d.items()}
            for d in results
            if isinstance(d, dict)
        ]
        if not results:
            raise EmptyDataError("No data returned for the given symbol.")

        return results

    @staticmethod
    def transform_data(
        query: FMPHistoricalRatingQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[FMPHistoricalRatingData]:
        """Return the transformed data."""
        return [FMPHistoricalRatingData(**d) for d in data]
