"""TMX Index Constituents Model"""

# pylint: disable=unused-argument
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.index_constituents import (
    IndexConstituentsData,
    IndexConstituentsQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_tmx.utils.helpers import get_data_from_url, tmx_indices_backend
from pydantic import Field, field_validator


class TmxIndexConstituentsQueryParams(IndexConstituentsQueryParams):
    """TMX Index Constituents Query Params."""

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request."
        + " Index data is from a single JSON file, updated each day after close."
        + " It is cached for one day. To bypass, set to False.",
    )


class TmxIndexConstituentsData(IndexConstituentsData):
    """TMX Index Constituents Data."""

    __alias_dict__ = {
        "market_value": "quotedmarketvalue",
    }

    market_value: Optional[float] = Field(
        default=None,
        description="The quoted market value of the asset.",
    )

    @field_validator("weight", mode="before", check_fields=False)
    @classmethod
    def normalize_percent(cls, v):
        """Return percents as normalized percentage points."""
        return float(v) / 100 if v else None


class TmxIndexConstituentsFetcher(
    Fetcher[
        TmxIndexConstituentsQueryParams,
        List[TmxIndexConstituentsData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxIndexConstituentsQueryParams:
        """Transform the query."""
        return TmxIndexConstituentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxIndexConstituentsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the TMX endpoint."""

        url = "https://tmxinfoservices.com/files/indices/sptsx-indices.json"

        data = await get_data_from_url(
            url,
            use_cache=query.use_cache,
            backend=tmx_indices_backend,
        )

        return data

    @staticmethod
    def transform_data(
        query: TmxIndexConstituentsQueryParams, data: Dict, **kwargs
    ) -> List[TmxIndexConstituentsData]:
        """Return the transformed data."""
        results = []
        data = data.copy()
        if data == {}:
            raise EmptyDataError
        if query.symbol not in data.get("indices"):  # type: ignore
            raise ValueError(f"Index {query.symbol} was not found.  Check the symbol.")
        index_data = data["indices"][query.symbol]
        if (
            index_data.get("nb_constituents") == 0
            or index_data.get("constituents") is None
        ):
            raise ValueError(f"No constituents found for index, {query.symbol}")
        results = index_data["constituents"]
        return [TmxIndexConstituentsData.model_validate(d) for d in results]
