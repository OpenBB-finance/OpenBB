"""Available Indices Fetcher for YFinance."""

from typing import Any, Dict, List, Optional

import pandas as pd
from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.available_indices import (
    AvailableIndicesData,
    AvailableIndicesQueryParams,
)
from openbb_yfinance.utils.references import INDICES
from pydantic import Field


class YFinanceAvailableIndicesQueryParams(AvailableIndicesQueryParams):
    """Available Indices query for YFinance."""


class YFinanceAvailableIndicesData(AvailableIndicesData):
    """Available Indices data for YFinance."""

    code: str = Field(
        description="ID code for keying the index in the OpenBB Terminal."
    )
    symbol: str = Field(description="Symbol for the index.", alias="ticker")


class YFinanceAvailableIndicesFetcher(
    Fetcher[
        YFinanceAvailableIndicesQueryParams,
        List[YFinanceAvailableIndicesData],
    ]
):
    """Transform the query, extract and transform the data."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceAvailableIndicesQueryParams:
        """Transform the query params."""
        return YFinanceAvailableIndicesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: YFinanceAvailableIndicesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        indices = pd.DataFrame(INDICES).transpose().reset_index()
        indices.columns = ["code", "name", "ticker"]

        return indices.to_dict("records")

    @staticmethod
    def transform_data(data: List[Dict]) -> List[YFinanceAvailableIndicesData]:
        """Return the transformed data."""
        return [YFinanceAvailableIndicesData.parse_obj(d) for d in data]
