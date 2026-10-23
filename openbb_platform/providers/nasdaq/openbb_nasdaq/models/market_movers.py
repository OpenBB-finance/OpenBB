"""Nasdaq Market Movers Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.market_movers import (
    MarketMoversData,
    MarketMoversQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import (
    CELL_CLICK_SYMBOL,
    MOVER_ASSET_CLASSES,
    MOVER_KEYS,
    MOVER_LISTS,
    MOVER_SESSION_KEYS,
    MOVER_SESSIONS,
)


class NasdaqMarketMoversQueryParams(MarketMoversQueryParams):
    """Nasdaq Market Movers Query.

    Source: https://www.nasdaq.com/market-activity/most-active
    """

    __json_schema_extra__ = {
        "category": {"choices": list(MOVER_KEYS)},
        "asset_class": {"choices": list(MOVER_ASSET_CLASSES)},
        "session": {"choices": list(MOVER_SESSION_KEYS)},
    }

    category: MOVER_LISTS = Field(
        default="most_active_share_volume",
        description="The mover list to return.",
    )
    asset_class: str = Field(
        default="stocks",
        description="The asset class. Mutual funds publish advancers and decliners"
        + " only; ETFs add most-active by share volume.",
    )
    session: MOVER_SESSIONS = Field(
        default="market",
        description="The trading session the list is ranked over.",
    )
    limit: int = Field(
        default=10,
        description="The number of movers to return.",
    )


class NasdaqMarketMoversData(MarketMoversData):
    """Nasdaq Market Movers Data.

    Nasdaq omits the price columns on some lists, so the standard required
    fields are relaxed rather than dropping the row.
    """

    symbol: str = Field(
        description="The ticker symbol.",
        json_schema_extra={"x-widget_config": CELL_CLICK_SYMBOL},
    )
    price: float | None = Field(default=None, description="The last price.")
    change: float | None = Field(
        default=None, description="The change in price from open."
    )
    change_percent: float | None = Field(
        default=None,
        description="The change in percent from open.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    volume: float | None = Field(
        default=None,
        description="The share or dollar volume, for the most-active lists.",
    )


class NasdaqMarketMoversFetcher(
    Fetcher[
        NasdaqMarketMoversQueryParams,
        list[NasdaqMarketMoversData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqMarketMoversQueryParams:
        """Transform the query."""
        return NasdaqMarketMoversQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqMarketMoversQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint.

        Raises
        ------
        OpenBBError
            If the asset class does not publish the requested list.
        """
        from openbb_core.app.model.abstract.error import OpenBBError

        from openbb_nasdaq.utils.helpers import get_nasdaq_data, rows_from_table

        asset_key = MOVER_ASSET_CLASSES.get(query.asset_class)

        if asset_key is None:
            raise OpenBBError(
                f"'{query.asset_class}' is not a Nasdaq market-movers asset class."
                f" Choose one of: {', '.join(MOVER_ASSET_CLASSES)}."
            )

        data = await get_nasdaq_data(
            f"marketmovers?assetclass={asset_key}"
            f"&exchangestatus={MOVER_SESSION_KEYS[query.session]}"
            f"&limit={query.limit}"
        )
        block = (data or {}).get(asset_key) or {}
        listing = block.get(MOVER_KEYS[query.category])

        if not listing:
            raise OpenBBError(
                f"Nasdaq does not publish '{query.category}'"
                f" for the '{query.asset_class}' asset class."
            )

        return rows_from_table(listing.get("table"))

    @staticmethod
    def transform_data(
        query: NasdaqMarketMoversQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqMarketMoversData]:
        """Transform the data to the standard format."""
        from openbb_nasdaq.utils.helpers import to_number, to_percent

        results: list[NasdaqMarketMoversData] = []
        is_volume_list = "most_active" in query.category

        for row in data:
            change_field = row.get("change")
            price = to_number(row.get("lastSalePrice"))
            change = to_number(row.get("lastSaleChange"))
            percent = to_percent(
                row.get("percentageChange") if is_volume_list else change_field
            )

            if percent is None and price is not None and change is not None:
                previous = price - change
                percent = change / previous if previous else None

            results.append(
                NasdaqMarketMoversData.model_validate(
                    {
                        "symbol": row.get("symbol"),
                        "name": row.get("name"),
                        "price": price,
                        "change": change,
                        "change_percent": percent,
                        "volume": to_number(change_field) if is_volume_list else None,
                    }
                )
            )

        return results
