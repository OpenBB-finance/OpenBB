"""TMX Symbol Reference Model."""

from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import Field


class TmxSymbolReferenceQueryParams(QueryParams):
    """TMX Symbol Reference Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}

    symbol: str = Field(description=QUERY_DESCRIPTIONS.get("symbol", ""))
    use_cache: bool = Field(
        default=True,
        description="Whether to use the on-disk response cache. Set to False to bypass.",
    )


class TmxSymbolReferenceData(Data):
    """TMX Symbol Reference Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    is_valid: bool | None = Field(
        default=None, description="Whether the feed resolves the symbol."
    )
    resolved_symbol: str | None = Field(
        default=None, description="The canonical symbol the feed addresses."
    )
    exchange: str | None = Field(
        default=None, description="The exchange code the symbol resolves to."
    )
    exchange_short_name: str | None = Field(
        default=None, description="The short name of the exchange."
    )
    exchange_name: str | None = Field(
        default=None, description="The full name of the exchange."
    )


class TmxSymbolReferenceFetcher(
    Fetcher[TmxSymbolReferenceQueryParams, list[TmxSymbolReferenceData]]
):
    """TMX Symbol Reference Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxSymbolReferenceQueryParams:
        """Transform the query."""
        return TmxSymbolReferenceQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxSymbolReferenceQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the symbology."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_tmx.utils.quotemedia import validate_symbols

        symbols = [s.strip() for s in query.symbol.split(",") if s.strip()]
        results = await validate_symbols(symbols, use_cache=query.use_cache)

        if not results:
            raise EmptyDataError(
                f"No symbol reference was returned for {query.symbol}."
            )

        return results

    @staticmethod
    def transform_data(
        query: TmxSymbolReferenceQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxSymbolReferenceData]:
        """Transform the data and validate the model."""
        return [
            TmxSymbolReferenceData.model_validate(
                {
                    "symbol": d.get("symbolstring"),
                    "is_valid": d.get("valid"),
                    "resolved_symbol": d.get("symbol"),
                    "exchange": d.get("exchange") or None,
                    "exchange_short_name": d.get("exShName"),
                    "exchange_name": d.get("exLgName"),
                }
            )
            for d in data
        ]
