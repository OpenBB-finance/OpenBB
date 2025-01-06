"""Deribit Futures Info Models."""

# pylint: disable=unused-argument

from datetime import datetime
from typing import Any, Literal, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_info import (
    FuturesInfoData,
    FuturesInfoQueryParams,
)
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)
from pydantic import ConfigDict, Field, field_validator


class DeribitFuturesInfoQueryParams(FuturesInfoQueryParams):
    """Deribit Futures Instruments Query."""

    __json_schema_extra__ = {
        "symbol": {"multiple_items_allowed": True},
    }

    symbol: str = Field(
        description=QUERY_DESCRIPTIONS.get("symbol", "")
        + " Perpetual contracts can be referenced by their currency pair - i.e, SOLUSDC"
        + " - or by their official Deribit symbol - i.e, SOL_USDC-PERPETUAL"
        + " For a list of currently available instruments, use `derivatives.futures.instruments()`"
    )

    @field_validator("symbol", mode="before", check_fields=False)
    @classmethod
    def _validate_symbol(cls, v):
        """Validate the symbol."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import run_async
        from openbb_deribit.utils.helpers import (
            get_futures_symbols,
            get_perpetual_symbols,
        )

        symbols = v.split(",")
        new_symbols: list = []
        perpetual_symbols = run_async(get_perpetual_symbols)
        futures_symbols = run_async(get_futures_symbols)
        all_symbols = futures_symbols + list(perpetual_symbols)

        for s in symbols:
            if s not in all_symbols:
                raise ValueError(
                    f"Invalid symbol: {s}. Valid symbols are: {all_symbols}"
                )
            if s in perpetual_symbols:
                new_symbols.append(perpetual_symbols[s])
            else:
                new_symbols.append(s)

        return ",".join(new_symbols)


class DeribitFuturesInfoData(FuturesInfoData):
    """Deribit Futures Info Data."""

    __alias_dict__ = {
        "symbol": "instrument_name",
        "change_percent": "price_change",
    }
    model_config = ConfigDict(extra="ignore")

    symbol: str = Field(description=DATA_DESCRIPTIONS.get("symbol", ""))
    state: Literal["open", "closed"] = Field(
        description="The state of the order book. Possible values are open and closed."
    )
    open_interest: float = Field(
        description="The total amount of outstanding contracts in the corresponding amount units."
    )
    index_price: float = Field(
        description="Current index (reference) price",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    best_ask_amount: Optional[float] = Field(
        default=None,
        description="It represents the requested order size of all best asks",
    )
    best_ask_price: Optional[float] = Field(
        default=None,
        description="The current best ask price, null if there aren't any asks",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    best_bid_price: Optional[float] = Field(
        default=None,
        description="The current best bid price, null if there aren't any bids",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    best_bid_amount: Optional[float] = Field(
        default=None,
        description="It represents the requested order size of all best bids",
    )
    last_price: Optional[float] = Field(
        default=None,
        description="The price for the last trade",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    high: Optional[float] = Field(
        default=None,
        description="Highest price during 24h",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    low: Optional[float] = Field(
        default=None,
        description="Lowest price during 24h",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    change_percent: Optional[float] = Field(
        default=None,
        description="24-hour price change expressed as a percentage, null if there weren't any trades",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume: Optional[float] = Field(
        default=None,
        description="Volume during last 24h in base currency",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    volume_usd: Optional[float] = Field(
        default=None,
        description="Volume in USD",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    mark_price: float = Field(
        description="The mark price for the instrument",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    settlement_price: Optional[float] = Field(
        default=None,
        description="The settlement price for the instrument. Only when state = open",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    delivery_price: Optional[float] = Field(
        default=None,
        description="The settlement price for the instrument. Only when state = closed.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    estimated_delivery_price: float = Field(
        description="Estimated delivery price for the market.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    current_funding: Optional[float] = Field(
        default=None,
        description="Current funding (perpetual only)",
    )
    funding_8h: Optional[float] = Field(
        default=None,
        description="Funding 8h (perpetual only)",
    )
    interest_value: Optional[float] = Field(
        default=None,
        description="Value used to calculate realized_funding in positions (perpetual only)",
    )
    max_price: float = Field(
        description="The maximum price for the future."
        + " Any buy orders submitted higher than this price, will be clamped to this maximum.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    min_price: float = Field(
        description="The minimum price for the future."
        + " Any sell orders submitted lower than this price will be clamped to this minimum.",
        json_schema_extra={"x-unit_measurement": "currency"},
    )
    timestamp: datetime = Field(description="The timestamp of the data.")

    @field_validator("change_percent", mode="before", check_fields=False)
    @classmethod
    def _validate_change_percent(cls, v):
        """Validate the change percent."""
        return v / 100 if v else v


class DeribitFuturesInfoFetcher(
    Fetcher[DeribitFuturesInfoQueryParams, list[DeribitFuturesInfoData]]
):
    """Deribit Futures Info Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitFuturesInfoQueryParams:
        """Transform the query."""
        return DeribitFuturesInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitFuturesInfoQueryParams,
        credentials: Optional[dict[str, str]],
        **kwargs: Any,
    ) -> list:
        """Extract data from the response."""
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from openbb_core.provider.utils.errors import EmptyDataError, OpenBBError
        from openbb_deribit.utils.helpers import get_ticker_data

        result: list = []
        symbols = query.symbol.split(",")
        try:
            tasks = [get_ticker_data(symbol) for symbol in symbols]
            for task in asyncio.as_completed(tasks, timeout=10):
                result.append(await task)
        except Exception as e:  # pylint: disable=broad-except
            raise OpenBBError(f"Error fetching data: {e}") from e

        if not result:
            raise EmptyDataError("No data found for the given symbol(s).")

        return sorted(result, key=lambda x: symbols.index(x["instrument_name"]))

    @staticmethod
    def transform_data(
        query: DeribitFuturesInfoQueryParams,
        data: list,
        **kwargs: Any,
    ) -> list[DeribitFuturesInfoData]:
        """Transform the data."""
        return [DeribitFuturesInfoData(**d) for d in data]
