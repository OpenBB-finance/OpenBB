"""SEC Symbol Mapping Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, Optional

from openbb_core.app.model.abstract.error import OpenBBError
from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.symbol_map import SymbolMapQueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class SecSymbolMapQueryParams(SymbolMapQueryParams):
    """SEC Symbol Mapping Query.

    Source: https://sec.gov/
    """


class SecSymbolMapData(Data):
    """SEC symbol map Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))


class SecSymbolMapFetcher(
    Fetcher[
        SecSymbolMapQueryParams,
        SecSymbolMapData,
    ]
):
    """Transform the query, extract and transform the data from the SEC endpoints."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> SecSymbolMapQueryParams:
        """Transform the query."""
        return SecSymbolMapQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: SecSymbolMapQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> Dict:
        """Return the raw data from the SEC endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_sec.utils.helpers import cik_map

        if not query.query.isdigit():
            raise OpenBBError("Query is required and must be a valid CIK.")
        symbol = await cik_map(int(query.query), query.use_cache)
        response = {"symbol": symbol}
        return response

    @staticmethod
    def transform_data(
        query: SecSymbolMapQueryParams, data: Dict, **kwargs: Any
    ) -> SecSymbolMapData:
        """Transform the data to the standard format."""
        return SecSymbolMapData.model_validate(data)
