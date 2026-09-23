"""Deribit Instruments Model."""

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
    AnyListingCurrencies,
    InstrumentKinds,
)

PERPETUAL_EXPIRATION = 32503708800000


class DeribitInstrumentsQueryParams(QueryParams):
    """Deribit Instruments Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_instruments
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
    currency: AnyListingCurrencies = Field(
        default="any", description="The settlement currency of the instruments."
    )
    kind: InstrumentKinds | None = Field(
        default=None,
        description="The kind of instrument. Default is all of them.",
    )
    expired: bool = Field(
        default=False,
        description="When True, returns instruments that have already expired.",
    )

    @model_validator(mode="after")
    def _options_are_listed_by_underlying(self):
        """Refuse a listing of options scoped to a currency that only settles them."""
        from openbb_deribit.utils.helpers import reject_options_by_settlement

        if not self.symbol:
            reject_options_by_settlement(self.currency, self.kind)

        return self


class DeribitInstrumentsData(Data):
    """Deribit Instruments Data."""

    __alias_dict__ = {"symbol": "instrument_name"}

    symbol: str = Field(
        description="The name of the instrument.",
        json_schema_extra={"x-widget_config": {"chartDataType": "category"}},
    )
    instrument_id: int | None = Field(
        default=None,
        description="The numeric identifier of the instrument.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Instrument ID",
                "cellDataType": "text",
                "chartDataType": "excluded",
            },
        },
    )
    kind: str | None = Field(
        default=None,
        description="The kind of instrument.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    instrument_type: str | None = Field(
        default=None,
        description="Whether the instrument is linear or reversed.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    future_type: str | None = Field(
        default=None,
        description="Whether the future is linear or reversed.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    state: str | None = Field(
        default=None,
        description="Whether the instrument's book is open.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    base_currency: str | None = Field(
        default=None,
        description="The currency the instrument is based on.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    quote_currency: str | None = Field(
        default=None,
        description="The currency the instrument is quoted in.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    counter_currency: str | None = Field(
        default=None,
        description="The counter currency of the instrument.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    settlement_currency: str | None = Field(
        default=None,
        description="The currency the instrument settles in.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    settlement_period: str | None = Field(
        default=None,
        description="How often the instrument settles.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    underlying_type: str | None = Field(
        default=None,
        description="The asset class of the underlying.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    product_group: str | None = Field(
        default=None,
        description="The margin group the instrument belongs to.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    price_index: str | None = Field(
        default=None,
        description="The index the instrument is priced against.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    lot_size: int | None = Field(
        default=None,
        description="The number of contracts in one lot.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    min_trade_amount: float | None = Field(
        default=None,
        description="The smallest amount that can be traded.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    tick_size: float | None = Field(
        default=None,
        description="The smallest price increment.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    max_leverage: int | None = Field(
        default=None,
        description="The highest leverage the instrument allows.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    max_non_default_leverage: float | None = Field(
        default=None,
        description="The highest leverage available outside the default tier.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    max_liquidation_commission: float | None = Field(
        default=None,
        description="The largest commission a liquidation is charged.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    maker_commission: float | None = Field(
        default=None,
        description="The commission charged to a resting order.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    taker_commission: float | None = Field(
        default=None,
        description="The commission charged to an aggressing order.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    block_trade_commission: float | None = Field(
        default=None,
        description="The commission charged to a block trade.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    block_trade_min_trade_amount: float | None = Field(
        default=None,
        description="The smallest amount a block trade can be.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    block_trade_tick_size: float | None = Field(
        default=None,
        description="The smallest price increment of a block trade.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    option_type: str | None = Field(
        default=None,
        description="Whether the option is a call or a put.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    strike: float | None = Field(
        default=None,
        description="The strike price of the option.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    is_active: bool | None = Field(
        default=None,
        description="Whether the instrument can be traded right now.",
        json_schema_extra={
            "x-widget_config": {"cellDataType": "boolean", "chartDataType": "excluded"},
        },
    )
    contract_size: float | None = Field(
        default=None,
        description="The size of one contract.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "series"},
        },
    )
    is_csr: bool | None = Field(
        default=None,
        description="Whether the instrument is a cross settled routed pair.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Is CSR",
                "cellDataType": "boolean",
                "chartDataType": "excluded",
                "hide": True,
            },
        },
    )
    is_cbe_routed: bool | None = Field(
        default=None,
        description="Whether the instrument routes to Coinbase Exchange liquidity.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Is CBE Routed",
                "cellDataType": "boolean",
                "chartDataType": "excluded",
            },
        },
    )
    index_id: int | None = Field(
        default=None,
        description="The numeric identifier of the price index.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Index ID",
                "cellDataType": "text",
                "chartDataType": "excluded",
                "hide": True,
            },
        },
    )
    tick_size_steps: list[dict] | None = Field(
        default=None,
        description="The price levels above which a different tick size applies.",
        json_schema_extra={
            "x-widget_config": {
                "cellDataType": "text",
                "chartDataType": "excluded",
                "hide": True,
            },
        },
    )
    base_currency_uuid: str | None = Field(
        default=None,
        description="The unique identifier of the base currency.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Base Currency UUID",
                "chartDataType": "excluded",
                "hide": True,
            },
        },
    )
    quote_currency_uuid: str | None = Field(
        default=None,
        description="The unique identifier of the quote currency.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Quote Currency UUID",
                "chartDataType": "excluded",
                "hide": True,
            },
        },
    )
    creation_timestamp: datetime | None = Field(
        default=None,
        description="When the instrument was listed.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    expiration_timestamp: datetime | None = Field(
        default=None,
        description="When the instrument expires. Perpetual and spot instruments carry none.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )

    @field_validator(
        "creation_timestamp", "expiration_timestamp", mode="before", check_fields=False
    )
    @classmethod
    def validate_timestamp(cls, v):
        """Read the timestamp as a datetime, dropping the perpetual sentinel."""
        from openbb_deribit.utils.helpers import from_timestamp

        return None if not v or int(v) == PERPETUAL_EXPIRATION else from_timestamp(v)


class DeribitInstrumentsFetcher(
    Fetcher[DeribitInstrumentsQueryParams, list[DeribitInstrumentsData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitInstrumentsQueryParams:
        """Transform the query."""
        return DeribitInstrumentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitInstrumentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If the exchange lists no matching instrument.
        """
        from openbb_deribit.utils.client import gather
        from openbb_deribit.utils.helpers import get_instruments

        if query.symbol:
            symbols = [s.strip().upper() for s in query.symbol.split(",") if s.strip()]
            results = await gather(
                [("get_instrument", {"instrument_name": s}) for s in symbols]
            )
            data = [result for result in results if isinstance(result, dict) and result]
        else:
            data = await get_instruments(query.currency, query.kind, query.expired)

        if not data:
            raise EmptyDataError("Deribit lists no instrument matching the query.")

        return data

    @staticmethod
    def transform_data(
        query: DeribitInstrumentsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitInstrumentsData]:
        """Transform the data to the model."""
        return [
            DeribitInstrumentsData.model_validate(record)
            for record in sorted(
                data,
                key=lambda d: (
                    str(d.get("kind")),
                    d.get("expiration_timestamp") or 0,
                    str(d.get("instrument_name")),
                ),
            )
        ]
