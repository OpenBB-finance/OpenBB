"""Available Indices fetcher for TMX"""

from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.available_indices import (
    AvailableIndicesData,
    AvailableIndicesQueryParams,
)
from openbb_tmx.utils.helpers import get_available_tmx_indices
from pydantic import Field


class TmxAvailableIndicesQueryParams(AvailableIndicesQueryParams):
    """TMX Available Indices Query Params."""


class TmxAvailableIndicesData(AvailableIndicesData):
    """TMX Available Indices Data."""

    symbol: str = Field(description="The ticker symbol of the index.")


class TmxAvailableIndicesFetcher(
    Fetcher[
        TmxAvailableIndicesQueryParams,
        List[TmxAvailableIndicesData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxAvailableIndicesQueryParams:
        """Transform the query params."""
        return TmxAvailableIndicesQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TmxAvailableIndicesQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Return the raw data from the TMX endpoint."""
        data = get_available_tmx_indices()
        return data

    @staticmethod
    def transform_data(data: List[Dict]) -> List[TmxAvailableIndicesData]:
        """Transform the data to the standard format."""
        return [TmxAvailableIndicesData.model_validate(d) for d in data]
