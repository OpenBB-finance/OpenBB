"""Deribit Book Summary Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator, model_validator

from openbb_deribit.utils.constants import (
    INSTRUMENT_CHOICES_ENDPOINT,
    SYMBOL_STYLE,
    InstrumentKinds,
    ListingCurrencies,
)


class DeribitBookSummaryQueryParams(QueryParams):
    """Deribit Book Summary Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_book_summary_by_currency
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

    symbol: str | None = Field(
        default=None,
        description="One or more instrument names. When given, the currency and"
        + " kind are ignored.",
    )
    currency: ListingCurrencies = Field(
        default="BTC", description="The settlement currency of the instruments."
    )
    kind: InstrumentKinds | None = Field(
        default=None, description="The kind of instrument. Default is all of them."
    )

    @model_validator(mode="after")
    def _options_are_listed_by_underlying(self):
        """Refuse a listing of options scoped to a currency that only settles them."""
        from openbb_deribit.utils.helpers import reject_options_by_settlement

        if not self.symbol:
            reject_options_by_settlement(self.currency, self.kind)

        return self


class DeribitBookSummaryData(Data):
    """Deribit Book Summary Data."""

    __alias_dict__ = {
        "symbol": "instrument_name",
        "last_price": "last",
        "bid": "bid_price",
        "ask": "ask_price",
        "mid": "mid_price",
        "change_percent": "price_change",
        "implied_volatility": "mark_iv",
        "timestamp": "creation_timestamp",
    }

    symbol: str = Field(
        description="The name of the instrument.",
        json_schema_extra={"x-widget_config": {"chartDataType": "category"}},
    )
    timestamp: datetime | None = Field(
        default=None,
        description="When the summary was published.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    base_currency: str | None = Field(
        default=None,
        description="The currency the instrument is based on.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    quote_currency: str | None = Field(
        default=None,
        description="The currency the instrument is quoted in.",
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
    mid: float | None = Field(
        default=None,
        description="The midpoint of the best bid and offer.",
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
    estimated_delivery_price: float | None = Field(
        default=None,
        description="What the instrument would deliver at right now.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    interest_rate: float | None = Field(
        default=None,
        description="The rate the exchange prices the option's greeks at.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    implied_volatility: float | None = Field(
        default=None,
        description="The volatility implied by the mark price.",
        json_schema_extra={
            "x-unit_measurement": "percent",
            "x-widget_config": {
                "headerName": "Mark IV",
                "chartDataType": "excluded",
            },
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


class DeribitBookSummaryFetcher(
    Fetcher[DeribitBookSummaryQueryParams, list[DeribitBookSummaryData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitBookSummaryQueryParams:
        """Transform the query."""
        return DeribitBookSummaryQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitBookSummaryQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If the exchange published no summary for the query.
        """
        from openbb_deribit.utils.client import gather, request
        from openbb_deribit.utils.helpers import get_perpetual_symbols

        if query.symbol:
            symbols = [s.strip().upper() for s in query.symbol.split(",") if s.strip()]
            perpetuals = await get_perpetual_symbols()
            results = await gather(
                [
                    (
                        "get_book_summary_by_instrument",
                        {"instrument_name": perpetuals.get(symbol, symbol)},
                    )
                    for symbol in symbols
                ]
            )
            data = [
                record
                for result in results
                if isinstance(result, list)
                for record in result
            ]
        else:
            data = await request(
                "get_book_summary_by_currency",
                {"currency": query.currency.upper(), "kind": query.kind},
            )

        if not data:
            raise EmptyDataError("Deribit published no summary for the query.")

        return data

    @staticmethod
    def transform_data(
        query: DeribitBookSummaryQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitBookSummaryData]:
        """Transform the data to the model."""
        return [
            DeribitBookSummaryData.model_validate(record)
            for record in sorted(data, key=lambda d: str(d.get("instrument_name")))
        ]
