"""Available Indices fetcher for TMX"""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.available_indices import (
    AvailableIndicesData,
    AvailableIndicesQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
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
        list[TmxAvailableIndicesData],
    ]
):
    """Transform the query, extract and transform the data from the TMX endpoints."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxAvailableIndicesQueryParams:
        """Transform the query params."""
        return TmxAvailableIndicesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxAvailableIndicesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> dict:
        """Return the raw data from the TMX endpoint."""
        from openbb_tmx.utils.helpers import get_data_from_url

        url = "https://tmxinfoservices.com/files/indices/sptsx-indices.json"

        return await get_data_from_url(url, use_cache=query.use_cache)

    @staticmethod
    def transform_data(
        query: TmxAvailableIndicesQueryParams,
        data: dict,
        **kwargs: Any,
    ) -> list[TmxAvailableIndicesData]:
        """Transform the data to the standard format."""
        import re

        data = data.copy()
        if data == {}:
            raise EmptyDataError

        categories: dict[str, list[str]] = {}

        for category, symbol_list in data["groups"].items():
            for symbol in symbol_list:
                categories.setdefault(symbol, []).append(category)

        symbols = {k: ", ".join(v) for k, v in categories.items()}
        new_data = []

        for symbol in data["indices"]:
            overview = data["indices"][symbol].get("overview_en", None)

            if overview:
                overview = re.sub("<.*?>", "", overview)
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
