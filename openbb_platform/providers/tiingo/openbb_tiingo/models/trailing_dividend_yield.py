"""Tiingo Trailing Dividend Yield Model."""

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.trailing_dividend_yield import (
    TrailingDivYieldData,
    TrailingDivYieldQueryParams,
)
from openbb_core.provider.utils.validators import check_single_value
from openbb_tiingo.utils.helpers import get_data_many
from pydantic import field_validator


class TiingoTrailingDivYieldQueryParams(TrailingDivYieldQueryParams):
    """Tiingo Trailing Dividend Yield Query.

    Source: https://www.tiingo.com/documentation/end-of-day
    """

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def check_single_value(cls, v):
        """Check that string is a single value."""
        return check_single_value(v)


class TiingoTrailingDivYieldData(TrailingDivYieldData):
    """Tiingo Trailing Dividend Yield Data."""

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

    # pylint: disable=unused-argument
    @staticmethod
    def extract_data(
        query: TiingoTrailingDivYieldQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the Tiingo endpoint."""
        api_key = credentials.get("tiingo_token") if credentials else ""
        url = (
            f"https://api.tiingo.com/tiingo/corporate-actions/{query.symbol}/distribution-yield?"
            f"token={api_key}"
        )
        return get_data_many(url)

    # pylint: disable=unused-argument
    @staticmethod
    def transform_data(
        query: TiingoTrailingDivYieldQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[TiingoTrailingDivYieldData]:
        """Return the transformed data."""
        data = data[-query.limit :] if query.limit else data
        return [TiingoTrailingDivYieldData.model_validate(d) for d in data]
