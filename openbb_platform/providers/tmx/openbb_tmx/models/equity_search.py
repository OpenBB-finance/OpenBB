"""TMX Equity Search Model."""

from typing import Any, Literal

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_search import (
    EquitySearchData,
    EquitySearchQueryParams,
)
from pydantic import Field

from openbb_tmx.utils.choices import literal_choices


class TmxEquitySearchQueryParams(EquitySearchQueryParams):
    """TMX Equity Search Query."""

    __json_schema_extra__ = {
        "country": {
            "x-widget_config": {"options": literal_choices(("CA", "US", "GB"))}
        },
    }

    country: Literal["CA", "US", "GB"] | None = Field(
        default="CA",
        description="Restrict to a two-letter country code. Set to None for every market.",
    )
    symbol_only: bool = Field(
        default=False,
        description="Match the symbol only, instead of the symbol or the name.",
    )
    limit: int = Field(default=200, description="The maximum number of results.")
    use_cache: bool = Field(
        default=True,
        description="Whether to use the on-disk response cache. Set to False to bypass.",
    )


class TmxEquitySearchData(EquitySearchData):
    """TMX Equity Search Data."""

    exchange: str | None = Field(
        default=None, description="The exchange the instrument trades on."
    )
    exchange_code: str | None = Field(default=None, description="The exchange code.")
    country: str | None = Field(
        default=None, description="The country the instrument is listed in."
    )
    security_type: str | None = Field(default=None, description="The instrument type.")
    market_cap: float | None = Field(
        default=None, description="The market capitalization."
    )
    optionable: bool | None = Field(
        default=None, description="Whether the instrument has listed options."
    )


class TmxEquitySearchFetcher(
    Fetcher[TmxEquitySearchQueryParams, list[TmxEquitySearchData]]
):
    """TMX Equity Search Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxEquitySearchQueryParams:
        """Transform the query."""
        return TmxEquitySearchQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEquitySearchQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the symbology."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_tmx.utils.directory import browse_symbols, lookup_symbols

        if not query.query:
            results = await browse_symbols(
                limit=query.limit,
                country=query.country,
                use_cache=query.use_cache,
            )
        else:
            results = await lookup_symbols(
                query.query,
                limit=query.limit,
                country=query.country,
                symbol_only=query.symbol_only,
                use_cache=query.use_cache,
            )

        if not results:
            raise EmptyDataError(f"No instruments matched '{query.query}'.")

        return results

    @staticmethod
    def transform_data(
        query: TmxEquitySearchQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxEquitySearchData]:
        """Transform the data and validate the model."""
        return [
            TmxEquitySearchData.model_validate(
                {
                    "symbol": d.get("symbol"),
                    "name": d.get("name"),
                    "exchange": d.get("exchangeShortName"),
                    "exchange_code": d.get("exchangeCode"),
                    "country": d.get("countryCode"),
                    "security_type": d.get("symbolType"),
                    "market_cap": d.get("marketCap"),
                    "optionable": d.get("optionable"),
                }
            )
            for d in data
        ]
