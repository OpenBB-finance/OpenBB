"""Tiingo TrailingDivYield end of day fetcher."""

from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.trailing_dividend_yield import (
    TrailingDivYieldHistoricalData,
    TrailingDivYieldHistoricalQueryParams,
)
from openbb_provider.utils.helpers import make_request


class TiingoTrailingDivYieldHistoricalQueryParams(
    TrailingDivYieldHistoricalQueryParams
):
    """Tiingo trailing dividend yield Query.

    Source: https://www.tiingo.com/documentation/end-of-day
    """


class TiingoTrailingDivYieldHistoricalData(TrailingDivYieldHistoricalData):
    """Tiingo trailing dividend yield Data."""

    __alias_dict__ = {"trailing_1y_yield": "trailingDiv1Y"}


class TiingoTrailingDivYieldHistoricalFetcher(
    Fetcher[
        TiingoTrailingDivYieldHistoricalQueryParams,
        List[TiingoTrailingDivYieldHistoricalData],
    ]
):
    """Transform the query, extract and transform the data from the Tiingo endpoints."""

    @staticmethod
    def transform_query(
        params: Dict[str, Any]
    ) -> TiingoTrailingDivYieldHistoricalQueryParams:
        """Transform the query params."""
        transformed_params = params
        return TiingoTrailingDivYieldHistoricalQueryParams(**transformed_params)

    # pylint: disable=protected-access
    @staticmethod
    def extract_data(
        query: TiingoTrailingDivYieldHistoricalQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Tiingo endpoint."""
        api_key = credentials.get("tiingo_token") if credentials else ""

        base_url = (
            f"https://api.tiingo.com/tiingo/corporate-actions/{query.symbol}/distribution-yield?"
            f"token={api_key}"
        )

        request = make_request(base_url)
        request.raise_for_status()
        return request.json()

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: TiingoTrailingDivYieldHistoricalQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TiingoTrailingDivYieldHistoricalData]:
        """Return the transformed data."""

        return [TiingoTrailingDivYieldHistoricalData.model_validate(d) for d in data]
