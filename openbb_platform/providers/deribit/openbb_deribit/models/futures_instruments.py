"""Deribit Futures Instruments Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.futures_instruments import (
    FuturesInstrumentsData,
    FuturesInstrumentsQueryParams,
)
from openbb_core.provider.utils.descriptions import DATA_DESCRIPTIONS
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import ConfigDict, Field, field_validator

from openbb_deribit.models.instruments import PERPETUAL_EXPIRATION


class DeribitFuturesInstrumentsQueryParams(FuturesInstrumentsQueryParams):
    """Deribit Futures Instruments Query.

    Source: https://docs.deribit.com/api-reference/market-data/public-get_instruments
    """


class DeribitFuturesInstrumentData(FuturesInstrumentsData):
    """Deribit Futures Instrument Data."""

    __alias_dict__ = {"symbol": "instrument_name"}

    model_config = ConfigDict(extra="ignore")

    symbol: str = Field(
        description=DATA_DESCRIPTIONS.get("symbol", ""),
        json_schema_extra={"x-widget_config": {"chartDataType": "category"}},
    )
    instrument_id: int = Field(
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
        description="When the instrument expires. Perpetual contracts carry none.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )

    @field_validator("expiration_timestamp", mode="before", check_fields=False)
    @classmethod
    def validate_expiration(cls, v):
        """Read the expiration, dropping the sentinel a perpetual carries."""
        return None if not v or int(v) == PERPETUAL_EXPIRATION else v


class DeribitFuturesInstrumentsFetcher(
    Fetcher[DeribitFuturesInstrumentsQueryParams, list[DeribitFuturesInstrumentData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> DeribitFuturesInstrumentsQueryParams:
        """Transform the query."""
        return DeribitFuturesInstrumentsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitFuturesInstrumentsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If the exchange lists no futures.
        """
        from openbb_deribit.utils.helpers import get_instruments

        data = await get_instruments("any", "future")

        if not data:
            raise EmptyDataError("Deribit lists no futures.")

        return data

    @staticmethod
    def transform_data(
        query: DeribitFuturesInstrumentsQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitFuturesInstrumentData]:
        """Transform the data to the model."""
        return [
            DeribitFuturesInstrumentData.model_validate(record)
            for record in sorted(
                data,
                key=lambda d: (
                    d.get("expiration_timestamp") or 0,
                    str(d.get("instrument_name")),
                ),
            )
        ]
