"""TMX Futures Instruments Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_instruments import (
    FuturesInstrumentsData,
    FuturesInstrumentsQueryParams,
)
from pydantic import Field


class TmxFuturesInstrumentsQueryParams(FuturesInstrumentsQueryParams):
    """TMX Futures Instruments Query."""

    asset_class: str | None = Field(
        default=None,
        description="Restrict to one Montreal Exchange instrument class.",
    )
    instrument_type: str | None = Field(
        default="future",
        description="Restrict to 'future' or 'option'. Defaults to futures only;"
        + " set to None for the complete listed universe.",
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use the on-disk response cache. Set to False to bypass.",
    )


class TmxFuturesInstrumentsData(FuturesInstrumentsData):
    """TMX Futures Instruments Data."""

    symbol: str = Field(description="The Montreal Exchange root symbol.")
    name: str | None = Field(
        default=None,
        description="Name of the underlying or product, where TMX publishes one.",
    )
    instrument_type: str | None = Field(
        default=None, description="Whether the product is an option or a future."
    )
    underlying_symbol: str | None = Field(
        default=None, description="The symbol of the underlying instrument."
    )
    expiry_cycle: str | None = Field(
        default=None,
        description="The listed expiry cycle, either 'standard' or 'short'.",
    )
    has_weekly_options: bool | None = Field(
        default=None, description="Whether weekly expirations are listed."
    )
    has_long_term_options: bool | None = Field(
        default=None, description="Whether long-term equity options are listed."
    )
    asset_class: str | None = Field(default=None, description="The instrument class.")
    asset_class_name: str | None = Field(
        default=None, description="The instrument class, as published."
    )
    quote_symbol: str | None = Field(
        default=None,
        description="The symbol that quotes the front contract, where one exists.",
    )


class TmxFuturesInstrumentsFetcher(
    Fetcher[TmxFuturesInstrumentsQueryParams, list[TmxFuturesInstrumentsData]]
):
    """TMX Futures Instruments Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxFuturesInstrumentsQueryParams:
        """Transform the query."""
        return TmxFuturesInstrumentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxFuturesInstrumentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Montreal Exchange."""
        from openbb_tmx.utils.mx import get_instruments_by_class

        rows = await get_instruments_by_class(
            query.asset_class, use_cache=query.use_cache
        )

        if query.instrument_type:
            rows = [
                r for r in rows if r.get("instrument_type") == query.instrument_type
            ]

        return rows

    @staticmethod
    def transform_data(
        query: TmxFuturesInstrumentsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxFuturesInstrumentsData]:
        """Transform the data and validate the model."""
        return [TmxFuturesInstrumentsData.model_validate(d) for d in data]
