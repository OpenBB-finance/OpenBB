"""Nasdaq Nordic Screener Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.abstract.query_params import QueryParams
from pydantic import Field

from openbb_nasdaq.utils.constants import CELL_CLICK_SYMBOL
from openbb_nasdaq.utils.nordic import (
    NORDIC_ASSET_CLASSES,
    NORDIC_CATEGORIES,
    NORDIC_MARKET_KEYS,
    NORDIC_MARKETS,
    NORDIC_PATHS,
)

PAGE_SIZE = 500


class NasdaqNordicScreenerQueryParams(QueryParams):
    """Nasdaq Nordic Screener Query.

    Source: https://www.nasdaq.com/european-market-activity
    """

    __json_schema_extra__ = {
        "asset_class": {"choices": list(NORDIC_PATHS)},
        "market": {"choices": list(NORDIC_MARKET_KEYS)},
    }

    asset_class: NORDIC_ASSET_CLASSES = Field(
        default="shares",
        description="The Nasdaq Nordic instrument listing to screen.",
    )
    market: NORDIC_MARKETS | None = Field(
        default=None,
        description="The listing venue. Shares are segmented by market tier and"
        + " fixed income by country; other asset classes ignore this.",
    )


class NasdaqNordicScreenerData(Data):
    """Nasdaq Nordic Screener Data."""

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
    sector: str | None = Field(default=None, description="The sector classification.")
    issuer: str | None = Field(default=None, description="The issuing entity.")
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
    high: float | None = Field(default=None, description="The session high.")
    low: float | None = Field(default=None, description="The session low.")
    volume: float | None = Field(default=None, description="The session volume.")
    reported_volume: float | None = Field(
        default=None, description="The off-book reported volume."
    )
    total_volume: float | None = Field(default=None, description="The total volume.")
    turnover: float | None = Field(
        default=None, description="The session turnover, in the trading currency."
    )
    trades_count: float | None = Field(
        default=None, description="The number of trades."
    )
    average_price: float | None = Field(
        default=None, description="The average price across all trades."
    )
    net_asset_value: float | None = Field(
        default=None, description="The fund net asset value."
    )
    total_expense_ratio: float | None = Field(
        default=None,
        description="The fund total expense ratio, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    coupon_rate: float | None = Field(
        default=None,
        description="The bond coupon rate, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    strike: float | None = Field(
        default=None, description="The derivative strike price."
    )
    contract_size: float | None = Field(
        default=None, description="The derivative contract size."
    )
    open_interest: float | None = Field(
        default=None, description="The derivative open interest."
    )
    basket_value: float | None = Field(
        default=None, description="The value of the underlying custom basket."
    )
    theoretical_price: float | None = Field(
        default=None, description="The theoretical price of the basket contract."
    )
    deferral_threshold: float | None = Field(
        default=None, description="The publication deferral threshold."
    )
    settlement_price: float | None = Field(
        default=None, description="The derivative settlement price."
    )
    expiration: dateType | None = Field(
        default=None, description="The instrument expiration date."
    )
    last_traded: dateType | None = Field(
        default=None, description="The date the instrument last traded."
    )
    mic_code: str | None = Field(default=None, description="The venue MIC code.")
    price_notation: str | None = Field(
        default=None, description="How the price is quoted."
    )
    note_code: str | None = Field(default=None, description="The exchange note code.")
    note_description: str | None = Field(
        default=None, description="The exchange note description."
    )
    instrument_type: str | None = Field(
        default=None, description="The instrument type."
    )
    exchange_symbol: str | None = Field(
        default=None, description="The symbol used by the exchange."
    )
    green_equity_designation: str | None = Field(
        default=None, description="The Nasdaq green equity designation."
    )
    orderbook_id: str | None = Field(
        default=None, description="The Nasdaq Nordic orderbook identifier."
    )


class NasdaqNordicScreenerFetcher(
    Fetcher[
        NasdaqNordicScreenerQueryParams,
        list[NasdaqNordicScreenerData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqNordicScreenerQueryParams:
        """Transform the query."""
        return NasdaqNordicScreenerQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqNordicScreenerQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint.

        Raises
        ------
        OpenBBError
            If the market is not one the asset class is segmented by.
        """
        import asyncio

        from openbb_core.app.model.abstract.error import OpenBBError

        from openbb_nasdaq.utils.helpers import get_nasdaq_data
        from openbb_nasdaq.utils.nordic import NORDIC_FIXED_CATEGORIES

        path = NORDIC_PATHS[query.asset_class]
        markets = NORDIC_CATEGORIES.get(query.asset_class)
        category = NORDIC_FIXED_CATEGORIES.get(query.asset_class)

        if markets:
            market = query.market or markets[0]

            if market not in markets:
                raise OpenBBError(
                    f"'{market}' is not a market for '{query.asset_class}'."
                    f" Choose one of: {', '.join(markets)}."
                )

            category = NORDIC_MARKET_KEYS[market]

        suffix = f"&category={category}" if category else ""
        base = f"nordic/screener/{path}?tableonly=false&lang=en&size={PAGE_SIZE}"
        first = await get_nasdaq_data(f"{base}&page=1{suffix}") or {}
        rows = list(_rows(first))
        total_pages = int((first.get("pagination") or {}).get("totalPages") or 1)

        async def get_page(page: int) -> list[dict]:
            """Collect one page of the listing."""
            data = await get_nasdaq_data(f"{base}&page={page}{suffix}") or {}

            return _rows(data)

        if total_pages > 1:
            pages = await asyncio.gather(
                *[get_page(page) for page in range(2, total_pages + 1)]
            )

            for page_rows in pages:
                rows.extend(page_rows)

        return rows

    @staticmethod
    def transform_data(
        query: NasdaqNordicScreenerQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqNordicScreenerData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If the listing returned no instruments.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import (
            clean_value,
            to_date,
            to_number,
            to_percent,
        )
        from openbb_nasdaq.utils.nordic import (
            NORDIC_NUMBER_FIELDS,
            NORDIC_TEXT_FIELDS,
        )

        if not data:
            raise EmptyDataError(f"No '{query.asset_class}' instruments were returned.")

        results: list[NasdaqNordicScreenerData] = []

        for row in data:
            record: dict[str, Any] = {
                "symbol": row.get("symbol"),
                "asset_class": row.get("assetClass"),
                "change_percent": to_percent(row.get("percentageChange")),
                "total_expense_ratio": to_percent(row.get("totalExpenseRatio")),
                "expiration": to_date(row.get("expirationDate")),
                "last_traded": to_date(row.get("lastTraded")),
            }

            for field, key in NORDIC_TEXT_FIELDS.items():
                record[field] = clean_value(row.get(key))

            for field, key in NORDIC_NUMBER_FIELDS.items():
                record[field] = to_number(row.get(key))

            record["coupon_rate"] = to_percent(row.get("couponRate"))
            results.append(NasdaqNordicScreenerData.model_validate(record))

        return results


def _rows(payload: dict) -> list[dict]:
    """Return the rows of a Nordic screener page.

    Most listings nest their rows under ``instrumentListing``; the custom
    basket listing returns them at the top level.

    Parameters
    ----------
    payload : dict
        The screener response.

    Returns
    -------
    list[dict]
        The instrument rows, or an empty list when the page carries none.
    """
    listing = payload.get("instrumentListing") or {}

    return listing.get("rows") or payload.get("rows") or []
