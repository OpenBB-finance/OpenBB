"""Tiingo TrailingDivYield end of day fetcher."""

from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.trailing_dividend_yield import (
    TrailingDivYieldData,
    TrailingDivYieldQueryParams,
)
from openbb_provider.utils.helpers import make_request


class TiingoTrailingDivYieldQueryParams(TrailingDivYieldQueryParams):
    """Tiingo trailing dividend yield Query.

    Source: https://www.tiingo.com/documentation/end-of-day
    """


class TiingoTrailingDivYieldData(TrailingDivYieldData):
    """Tiingo trailing dividend yield Data."""

    __alias_dict__ = {"trailing_dividend_yield": "trailingDiv1Y"}


class TiingoTrailingDivYieldFetcher(
    Fetcher[
        TiingoTrailingDivYieldQueryParams,
        List[TiingoTrailingDivYieldData],
    ]
):
    """Transform the query, extract and transform the data from the Tiingo endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TiingoTrailingDivYieldQueryParams:
        """Transform the query params."""
        transformed_params = params
        return TiingoTrailingDivYieldQueryParams(**transformed_params)

    # pylint: disable=protected-access
    @staticmethod
    def extract_data(
        query: TiingoTrailingDivYieldQueryParams,
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
        query: TiingoTrailingDivYieldQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TiingoTrailingDivYieldData]:
        """Return the transformed data."""

        return [TiingoTrailingDivYieldData.model_validate(d) for d in data]
