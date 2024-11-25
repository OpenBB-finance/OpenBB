"""Yahoo Finance Available Indices Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.available_indices import (
    AvailableIndicesData,
    AvailableIndicesQueryParams,
)
from openbb_yfinance.utils.references import INDICES
from pydantic import Field


class YFinanceAvailableIndicesQueryParams(AvailableIndicesQueryParams):
    """Yahoo Finance Available Indices Query.

    Source: https://finance.yahoo.com/
    """


class YFinanceAvailableIndicesData(AvailableIndicesData):
    """Yahoo Finance Available Indices Data."""

    __alias_dict__ = {
        "symbol": "ticker",
    }

    code: str = Field(
        description="ID code for keying the index in the OpenBB Terminal."
    )
    symbol: str = Field(description="Symbol for the index.")


class YFinanceAvailableIndicesFetcher(
    Fetcher[
        YFinanceAvailableIndicesQueryParams,
        List[YFinanceAvailableIndicesData],
    ]
):
    """Transform the query, extract and transform the data from the Yahoo Finance endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceAvailableIndicesQueryParams:
        """Transform the query params."""
        return YFinanceAvailableIndicesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceAvailableIndicesQueryParams,  # pylint disable=unused-argument
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the data."""
        from pandas import DataFrame  # pylint: disable=import-outside-toplevel

        indices = DataFrame(INDICES).transpose().reset_index()
        indices.columns = ["code", "name", "ticker"]

        return indices.to_dict("records")

    @staticmethod
    def transform_data(
        query: YFinanceAvailableIndicesQueryParams, data: List[Dict], **kwargs: Any
    ) -> List[YFinanceAvailableIndicesData]:
        """Return the transformed data."""
        return [YFinanceAvailableIndicesData.model_validate(d) for d in data]
