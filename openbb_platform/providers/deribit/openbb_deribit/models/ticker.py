"""Deribit Ticker Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_deribit.utils.constants import (
    INSTRUMENT_CHOICES_ENDPOINT,
    SYMBOL_STYLE,
)


class DeribitTickerQueryParams(QueryParams):
    """Deribit Ticker Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-ticker
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": INSTRUMENT_CHOICES_ENDPOINT,
                "style": SYMBOL_STYLE,
            },
        }
    }

    symbol: str = Field(
        description="One or more instrument names. A perpetual can also be given"
        + " by its shortened root, such as 'SOLUSDC'."
    )


class DeribitTickerData(Data):
    """Deribit Ticker Data."""

    __alias_dict__ = {
        "symbol": "instrument_name",
        "change_percent": "price_change",
        "implied_volatility": "mark_iv",
        "bid": "best_bid_price",
        "ask": "best_ask_price",
        "bid_size": "best_bid_amount",
        "ask_size": "best_ask_amount",
        "last_price": "last_price",
    }

    symbol: str = Field(
        description="The name of the instrument.",
        json_schema_extra={"x-widget_config": {"chartDataType": "category"}},
    )
    timestamp: datetime | None = Field(
        default=None,
        description="When the quote was published.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    state: str | None = Field(
        default=None,
        description="Whether the instrument's book is open.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    combo_state: str | None = Field(
        default=None,
        description="Whether the combo is still tradeable.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    last_price: float | None = Field(
        default=None,
        description="The price the instrument last traded at.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    bid: float | None = Field(
        default=None,
        description="The highest price bid.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    ask: float | None = Field(
        default=None,
        description="The lowest price offered.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    bid_size: float | None = Field(
        default=None,
        description="The size resting at the best bid.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    ask_size: float | None = Field(
        default=None,
        description="The size resting at the best offer.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    implied_bid: float | None = Field(
        default=None,
        description="The bid implied by the legs of a combo.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    implied_ask: float | None = Field(
        default=None,
        description="The offer implied by the legs of a combo.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    mark_price: float | None = Field(
        default=None,
        description="The price the exchange marks positions at.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "series"},
        },
    )
    index_price: float | None = Field(
        default=None,
        description="The price of the index the instrument is priced against.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    settlement_price: float | None = Field(
        default=None,
        description="The price the instrument last settled at.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    delivery_price: float | None = Field(
        default=None,
        description="The price an expired instrument was delivered at.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    estimated_delivery_price: float | None = Field(
        default=None,
        description="What the instrument would deliver at right now.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    min_price: float | None = Field(
        default=None,
        description="The lowest price an order will be accepted at.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    max_price: float | None = Field(
        default=None,
        description="The highest price an order will be accepted at.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    high: float | None = Field(
        default=None,
        description="The highest price of the last 24 hours.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    low: float | None = Field(
        default=None,
        description="The lowest price of the last 24 hours.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    change_percent: float | None = Field(
        default=None,
        description="The price change over the last 24 hours.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    volume: float | None = Field(
        default=None,
        description="The volume of the last 24 hours, in base currency.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    volume_notional: float | None = Field(
        default=None,
        description="The volume of the last 24 hours, in quote currency.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    volume_usd: float | None = Field(
        default=None,
        description="The volume of the last 24 hours, in USD.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {
                "headerName": "Volume USD",
                "chartDataType": "excluded",
            },
        },
    )
    open_interest: float | None = Field(
        default=None,
        description="The contracts left outstanding.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    current_funding: float | None = Field(
        default=None,
        description="The funding rate a perpetual is paying right now.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    funding_8h: float | None = Field(
        default=None,
        description="The funding rate a perpetual paid over eight hours.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "Funding 8H",
                "chartDataType": "excluded",
            },
        },
    )
    interest_value: float | None = Field(
        default=None,
        description="The value realized funding on a perpetual is derived from.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    interest_rate: float | None = Field(
        default=None,
        description="The rate the exchange prices the option's greeks at.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    underlying_index: str | None = Field(
        default=None,
        description="The future or index the option is priced against.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    underlying_price: float | None = Field(
        default=None,
        description="The price of the underlying the option is priced against.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    implied_volatility: float | None = Field(
        default=None,
        description="The volatility implied by the mark price.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "Mark IV", "chartDataType": "excluded"},
        },
    )
    bid_iv: float | None = Field(
        default=None,
        description="The volatility implied by the best bid.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "Bid IV", "chartDataType": "excluded"},
        },
    )
    ask_iv: float | None = Field(
        default=None,
        description="The volatility implied by the best offer.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"headerName": "Ask IV", "chartDataType": "excluded"},
        },
    )
    delta: float | None = Field(
        default=None,
        description="The sensitivity to the underlying's price.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    gamma: float | None = Field(
        default=None,
        description="The sensitivity of delta to the underlying's price.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    vega: float | None = Field(
        default=None,
        description="The sensitivity to implied volatility.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    theta: float | None = Field(
        default=None,
        description="The sensitivity to the passage of time.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    rho: float | None = Field(
        default=None,
        description="The sensitivity to the interest rate.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )

    @field_validator("timestamp", mode="before", check_fields=False)
    @classmethod
    def validate_timestamp(cls, v):
        """Read the timestamp as a datetime."""
        from openbb_deribit.utils.helpers import from_timestamp

        return from_timestamp(v) if v else None

    @field_validator(
        "current_funding",
        "funding_8h",
        "interest_rate",
        mode="before",
        check_fields=False,
    )
    @classmethod
    def as_percent(cls, v):
        """Return a rate the exchange sends as a fraction in percent units."""
        return v * 100 if v is not None else None


class DeribitTickerFetcher(Fetcher[DeribitTickerQueryParams, list[DeribitTickerData]]):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitTickerQueryParams:
        """Transform the query."""
        return DeribitTickerQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitTickerQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If none of the instruments published a quote.
        """
        from openbb_deribit.utils.client import gather
        from openbb_deribit.utils.helpers import get_perpetual_symbols

        symbols = [s.strip().upper() for s in query.symbol.split(",") if s.strip()]
        perpetuals = await get_perpetual_symbols()
        resolved = [perpetuals.get(symbol, symbol) for symbol in symbols]
        results = await gather(
            [("ticker", {"instrument_name": s}) for s in resolved], use_cache=False
        )
        data = [result for result in results if isinstance(result, dict) and result]

        if not data:
            raise EmptyDataError(
                f"Deribit published no quote for {', '.join(resolved)}."
            )

        return data

    @staticmethod
    def transform_data(
        query: DeribitTickerQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitTickerData]:
        """Transform the data to the model."""
        from openbb_deribit.utils.helpers import flatten_ticker

        return [
            DeribitTickerData.model_validate(flatten_ticker(record)) for record in data
        ]
