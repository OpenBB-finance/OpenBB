"""Available Indices fetcher for TMX"""

# pylint: disable=unused-argument
import re
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.available_indices import (
    AvailableIndicesData,
    AvailableIndicesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_tmx.utils.helpers import get_data_from_url, tmx_indices_backend
from pydantic import Field


class TmxAvailableIndicesQueryParams(AvailableIndicesQueryParams):
    """TMX Available Indices Query Params."""

    use_cache: bool = Field(
        default=True,
        description="Whether to use a cached request."
        + " Index data is from a single JSON file, updated each day after close."
        + " It is cached for one day. To bypass, set to False.",
    )


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
    async def aextract_data(
        query: TmxAvailableIndicesQueryParams,
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
        query: TmxAvailableIndicesQueryParams,
        data: Dict,
        **kwargs: Any,
    ) -> List[TmxAvailableIndicesData]:
        """Transform the data to the standard format."""

        data = data.copy()
        if data == {}:
            raise EmptyDataError

        # Extract the category for each index.
        symbols = {}
        for category, symbol_list in data["groups"].items():
            for symbol in symbol_list:
                if symbol not in symbols:
                    symbols[symbol] = category
                else:
                    symbols[symbol].append(category)
            category = {"category": symbols}  # noqa: PLW2901
        # Extract the data for each index and combine with the category.
        new_data = []
        for symbol in data["indices"]:
            overview = data["indices"][symbol].get("overview_en", None)
            if overview:
                # Remove HTML tags from the overview
                overview = re.sub("<.*?>", "", overview)
                # Remove additional artifacts from the overview
                overview = re.sub("\r|\n|amp;", "", overview)
            new_data.append(
                {
                    "symbol": symbol,
                    "name": data["indices"][symbol].get("name_en", None),
                    "currency": (
                        "USD"
                        if "(USD)" in data["indices"][symbol]["name_en"]
                        else "CAD"
                    ),
                    "category": symbols[symbol],
                    "market_value": (
                        data["indices"][symbol]["quotedmarketvalue"].get("total", None)
                        if data["indices"][symbol].get("quotedmarketvalue")
                        else None
                    ),
                    "num_constituents": data["indices"][symbol].get(
                        "nb_constituents", None
                    ),
                    "overview": (
                        overview
                        if data["indices"][symbol].get("overview") != ""
                        else None
                    ),
                    "methodology": (
                        data["indices"][symbol].get("methodology", None)
                        if data["indices"][symbol].get("methodology") != ""
                        else None
                    ),
                    "factsheet": (
                        data["indices"][symbol].get("factsheet", None)
                        if data["indices"][symbol].get("factsheet") != ""
                        else None
                    ),
                }
            )

        return [TmxAvailableIndicesData.model_validate(d) for d in new_data]
