"""Deribit Block RFQ Trades Model."""

from datetime import datetime
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.errors import EmptyDataError
from pydantic import Field, field_validator

from openbb_deribit.utils.constants import (
    BLOCK_RFQ_MAX_COUNT,
    BLOCK_RFQ_MIN_COUNT,
    AnyListingCurrencies,
)


class DeribitBlockRfqTradesQueryParams(QueryParams):
    """Deribit Block RFQ Trades Query.

    Source: https://docs.deribit.com/api-reference/block-rfq/public-get_block_rfq_trades
    """

    currency: AnyListingCurrencies = Field(
        default="any", description="The settlement currency of the quoted legs."
    )
    limit: int = Field(
        default=BLOCK_RFQ_MAX_COUNT,
        description=f"The number of requests to return, between"
        f" {BLOCK_RFQ_MIN_COUNT} and {BLOCK_RFQ_MAX_COUNT}.",
        ge=BLOCK_RFQ_MIN_COUNT,
        le=BLOCK_RFQ_MAX_COUNT,
    )


class DeribitBlockRfqTradesData(Data):
    """Deribit Block RFQ Trades Data."""

    timestamp: datetime = Field(
        description="When the request traded.",
        json_schema_extra={
            "x-widget_config": {"chartDataType": "category", "pinned": "left"}
        },
    )
    rfq_id: int | None = Field(
        default=None,
        description="The identifier of the request.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "RFQ ID",
                "cellDataType": "text",
                "chartDataType": "excluded",
            }
        },
    )
    combo_id: str | None = Field(
        default=None,
        description="The combo the request was quoted as.",
        json_schema_extra={
            "x-widget_config": {
                "headerName": "Combo ID",
                "chartDataType": "excluded",
            }
        },
    )
    direction: str | None = Field(
        default=None,
        description="Which side the taker was on.",
        json_schema_extra={
            "x-widget_config": {"headerName": "Side", "chartDataType": "excluded"}
        },
    )
    amount: float | None = Field(
        default=None,
        description="The size of the request.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    mark_price: float | None = Field(
        default=None,
        description="The price the exchange marked the structure at.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "excluded"},
        },
    )
    leg: str | None = Field(
        default=None,
        description="The instrument the leg trades.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    leg_direction: str | None = Field(
        default=None,
        description="Which side the leg was traded on.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    leg_price: float | None = Field(
        default=None,
        description="The price the leg traded at.",
        json_schema_extra={
            "x-unit_measurement": "currency",
            "x-widget_config": {"chartDataType": "series"},
        },
    )
    leg_ratio: float | None = Field(
        default=None,
        description="How many of the leg one structure holds.",
        json_schema_extra={"x-widget_config": {"chartDataType": "excluded"}},
    )
    index_prices: dict | None = Field(
        default=None,
        description="The index prices the structure was marked against.",
        json_schema_extra={
            "x-widget_config": {
                "cellDataType": "text",
                "chartDataType": "excluded",
                "hide": True,
            }
        },
    )

    @field_validator("timestamp", mode="before", check_fields=False)
    @classmethod
    def validate_timestamp(cls, v):
        """Read the timestamp as a datetime."""
        from openbb_deribit.utils.helpers import from_timestamp

        return from_timestamp(v)


class DeribitBlockRfqTradesFetcher(
    Fetcher[DeribitBlockRfqTradesQueryParams, list[DeribitBlockRfqTradesData]]
):
    """Transform the query, extract and transform the data from the Deribit endpoint."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> DeribitBlockRfqTradesQueryParams:
        """Transform the query."""
        return DeribitBlockRfqTradesQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: DeribitBlockRfqTradesQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Deribit endpoint.

        Raises
        ------
        EmptyDataError
            If no block request traded.
        """
        from openbb_deribit.utils.client import request
        from openbb_deribit.utils.helpers import normalize_currency

        result = await request(
            "get_block_rfq_trades",
            {
                "currency": normalize_currency(query.currency),
                "count": query.limit,
            },
            use_cache=False,
        )
        data = (result or {}).get("block_rfqs") or []

        if not data:
            raise EmptyDataError("Deribit reports no block requests traded.")

        return data

    @staticmethod
    def transform_data(
        query: DeribitBlockRfqTradesQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[DeribitBlockRfqTradesData]:
        """Transform the data to the model."""
        records: list[dict] = []

        for rfq in data:
            context = {
                "timestamp": rfq.get("timestamp"),
                "rfq_id": rfq.get("id"),
                "combo_id": rfq.get("combo_id"),
                "direction": rfq.get("direction"),
                "amount": rfq.get("amount"),
                "mark_price": rfq.get("mark_price"),
                "index_prices": rfq.get("index_prices"),
            }

            for leg in rfq.get("legs") or [{}]:
                records.append(
                    {
                        **context,
                        "leg": leg.get("instrument_name"),
                        "leg_direction": leg.get("direction"),
                        "leg_price": leg.get("price"),
                        "leg_ratio": leg.get("ratio"),
                    }
                )

        return [
            DeribitBlockRfqTradesData.model_validate(record)
            for record in sorted(
                records,
                key=lambda d: (d["timestamp"] or 0, d["rfq_id"] or 0),
                reverse=True,
            )
        ]
