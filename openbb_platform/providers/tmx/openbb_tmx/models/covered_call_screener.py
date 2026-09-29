"""TMX Covered Call Screener Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from pydantic import Field


class TmxCoveredCallScreenerQueryParams(QueryParams):
    """TMX Covered Call Screener Query."""

    symbol: str | None = Field(
        default=None,
        description="Restrict to one underlying. Leave unset to screen every listing.",
    )
    expiration: str | None = Field(
        default=None,
        description="Restrict to one expiry month, as YYYY-MM.",
    )
    premium_return_min: float = Field(
        default=5.0,
        description="Minimum annualized premium return, in percent. The exchange"
        + " enforces a floor of 0.5.",
    )
    capital_gain_min: float = Field(
        default=5.0,
        description="Minimum annualized potential capital gain, in percent. The"
        + " exchange enforces a floor of 0.5.",
    )
    use_cache: bool = Field(
        default=True,
        description="Whether to use the on-disk response cache. Set to False to bypass.",
    )


class TmxCoveredCallScreenerData(Data):
    """TMX Covered Call Screener Data."""

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    expiration: dateType | None = Field(
        default=None, description="Expiration date of the contract."
    )
    strike: float | None = Field(
        default=None, description="Strike price of the contract."
    )
    underlying_price: float | None = Field(
        default=None, description="Last price of the underlying."
    )
    total_return: float | None = Field(
        default=None,
        description="Annualized potential total return, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    premium_return: float | None = Field(
        default=None,
        description="Annualized premium return, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    capital_gain: float | None = Field(
        default=None,
        description="Annualized potential capital gain, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    bid: float | None = Field(default=None, description="Bid price of the contract.")
    bid_size: int | None = Field(default=None, description="Bid size.")
    ask: float | None = Field(default=None, description="Ask price of the contract.")
    ask_size: int | None = Field(default=None, description="Ask size.")
    volume: int | None = Field(default=None, description="Contract volume.")
    open_interest: int | None = Field(default=None, description="Open interest.")


class TmxCoveredCallScreenerFetcher(
    Fetcher[TmxCoveredCallScreenerQueryParams, list[TmxCoveredCallScreenerData]]
):
    """TMX Covered Call Screener Fetcher."""

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> TmxCoveredCallScreenerQueryParams:
        """Transform the query."""
        return TmxCoveredCallScreenerQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxCoveredCallScreenerQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Montreal Exchange screener."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_tmx.utils.mx import screen_covered_calls

        results = await screen_covered_calls(
            symbol=query.symbol,
            expiration=query.expiration,
            premium=query.premium_return_min,
            gain=query.capital_gain_min,
            use_cache=query.use_cache,
        )

        if not results:
            raise EmptyDataError("No contracts matched the screen.")

        return results

    @staticmethod
    def transform_data(
        query: TmxCoveredCallScreenerQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxCoveredCallScreenerData]:
        """Transform the data and validate the model."""
        return [TmxCoveredCallScreenerData.model_validate(d) for d in data]
