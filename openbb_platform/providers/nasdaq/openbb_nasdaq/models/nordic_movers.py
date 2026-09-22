"""Nasdaq Nordic Market Movers Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_nasdaq.utils.constants import CELL_CLICK_SYMBOL
from openbb_nasdaq.utils.nordic import NORDIC_MOVER_GROUPS, NORDIC_MOVER_TYPES


class NasdaqNordicMoversQueryParams(QueryParams):
    """Nasdaq Nordic Market Movers Query.

    Source: https://www.nasdaq.com/european-market-activity
    """

    __json_schema_extra__ = {"asset_group": {"choices": list(NORDIC_MOVER_GROUPS)}}

    asset_group: NORDIC_MOVER_TYPES = Field(
        default="shares", description="The Nasdaq Nordic asset group to rank."
    )
    limit: int = Field(default=15, description="The number of movers to return.")


class NasdaqNordicMoversData(Data):
    """Nasdaq Nordic Market Movers Data."""

    symbol: str | None = Field(
        default=None,
        description="The instrument symbol.",
        json_schema_extra={"x-widget_config": CELL_CLICK_SYMBOL},
    )
    name: str | None = Field(default=None, description="The instrument name.")
    isin: str | None = Field(default=None, description="The instrument ISIN.")
    asset_class: str | None = Field(
        default=None, description="The Nasdaq Nordic asset class."
    )
    currency: str | None = Field(default=None, description="The trading currency.")
    last_price: float | None = Field(default=None, description="The last traded price.")
    change: float | None = Field(
        default=None, description="The change from the previous close."
    )
    change_percent: float | None = Field(
        default=None,
        description="The change from the previous close, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    bid: float | None = Field(default=None, description="The current bid.")
    ask: float | None = Field(default=None, description="The current ask.")
    volume: float | None = Field(default=None, description="The session volume.")
    volume_change_percent: float | None = Field(
        default=None,
        description="The change in volume, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    turnover: float | None = Field(default=None, description="The session turnover.")
    turnover_eur: float | None = Field(
        default=None, description="The session turnover, in euros."
    )
    trades_count: float | None = Field(
        default=None, description="The number of trades."
    )
    contract_size: float | None = Field(
        default=None, description="The derivative contract size."
    )
    expiration: dateType | None = Field(
        default=None, description="The derivative expiration date."
    )
    orderbook_id: str | None = Field(
        default=None, description="The Nasdaq Nordic orderbook identifier."
    )


class NasdaqNordicMoversFetcher(
    Fetcher[
        NasdaqNordicMoversQueryParams,
        list[NasdaqNordicMoversData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqNordicMoversQueryParams:
        """Transform the query."""
        return NasdaqNordicMoversQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqNordicMoversQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import get_nasdaq_data

        data = await get_nasdaq_data(
            f"nordic/market-movers?assetGroup={NORDIC_MOVER_GROUPS[query.asset_group]}"
            f"&returnMovers=TOP_TRADED&size={query.limit}&lang=en"
        )
        block = ((data or {}).get("marketMovers") or {}).get("TOP_TRADED") or {}

        return block.get("rows") or []

    @staticmethod
    def transform_data(
        query: NasdaqNordicMoversQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqNordicMoversData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If the asset group published no movers.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import (
            clean_value,
            to_date,
            to_number,
            to_percent,
        )

        if not data:
            raise EmptyDataError(
                f"No movers were returned for the '{query.asset_group}' asset group."
            )

        return [
            NasdaqNordicMoversData.model_validate(
                {
                    "symbol": row.get("symbol"),
                    "name": row.get("fullName"),
                    "isin": row.get("isin"),
                    "asset_class": row.get("assetClass"),
                    "currency": clean_value(row.get("ccy")),
                    "last_price": to_number(row.get("lastSalePrice")),
                    "change": to_number(row.get("netChange")),
                    "change_percent": to_percent(row.get("percentageChange")),
                    "bid": to_number(row.get("bidPrice")),
                    "ask": to_number(row.get("askPrice")),
                    "volume": to_number(row.get("volume")),
                    "volume_change_percent": to_percent(
                        row.get("volumePercentageChange")
                    ),
                    "turnover": to_number(row.get("turnover")),
                    "turnover_eur": to_number(row.get("turnoverEUR")),
                    "trades_count": to_number(row.get("numTrades")),
                    "contract_size": to_number(row.get("contractSize")),
                    "expiration": to_date(row.get("expiryDate")),
                    "orderbook_id": row.get("orderbookId"),
                }
            )
            for row in data
        ]
