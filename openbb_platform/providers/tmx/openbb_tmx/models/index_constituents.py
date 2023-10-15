"""TMX Index Constituents Model"""

from typing import Any, Dict, List, Optional

from openbb_provider.abstract.fetcher import Fetcher
from openbb_provider.standard_models.index_constituents import (
    IndexConstituentsData,
    IndexConstituentsQueryParams,
)
from openbb_tmx.utils.helpers import get_index_data
from pydantic import Field


class TmxIndexConstituentsQueryParams(IndexConstituentsQueryParams):
    """TMX Index Constituents Query Params."""


class TmxIndexConstituentsData(IndexConstituentsData):
    """TMX Index Constituents Data."""

    __alias_dict__ = {
        "name": "longName",
        "value": "quotedMarketValue",
    }

    short_name: Optional[str] = Field(
        description="The short name of the index constituent.", default=None
    )
    exchange: Optional[str] = Field(
        description="The exchange the index constituent is traded on.", default=None
    )
    exchange_short_name: Optional[str] = Field(
        description="The short name of the exchange.", default=None, alias="exShortName"
    )
    exchange_long_name: Optional[str] = Field(
        description="The long name of the exchange.", default=None, alias="exLongName"
    )


class TmxIndexConstituentsFetcher(
    Fetcher[
        TmxIndexConstituentsQueryParams,
        List[TmxIndexConstituentsData],
    ]
):
    @staticmethod
    def transform_query(params: Dict[str, Any]) -> TmxIndexConstituentsQueryParams:
        """Transform the query."""

        params["symbol"] = (
            params["symbol"].upper().replace(".TO", "").replace(".TSX", "")
        )
        return TmxIndexConstituentsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: TmxIndexConstituentsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List:
        results: List[Dict] = []
        data = {}
        data = get_index_data(query.symbol)

        if data != {} and "constituents" in data:
            results.extend(data["constituents"])

        return results

    @staticmethod
    def transform_data(data: List) -> List[TmxIndexConstituentsData]:
        """Return the transformed data."""
        return [TmxIndexConstituentsData.model_validate(d) for d in data]
