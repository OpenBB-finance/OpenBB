"""Nasdaq Price Target Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.price_target import (
    PriceTargetData,
    PriceTargetQueryParams,
)

from openbb_nasdaq.utils.constants import SYMBOL_CHOICES_ENDPOINT

EPOCH = dateType(1900, 1, 1)


class NasdaqPriceTargetQueryParams(PriceTargetQueryParams):
    """Nasdaq Price Target Query.

    Source: https://www.nasdaq.com/market-activity/stocks
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
    }


class NasdaqPriceTargetData(PriceTargetData):
    """Nasdaq Price Target Data."""


class NasdaqPriceTargetFetcher(
    Fetcher[
        NasdaqPriceTargetQueryParams,
        list[NasdaqPriceTargetData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqPriceTargetQueryParams:
        """Transform the query."""
        return NasdaqPriceTargetQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqPriceTargetQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        import asyncio
        from warnings import warn

        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import get_nasdaq_data

        symbols = [
            s.strip().upper() for s in (query.symbol or "").split(",") if s.strip()
        ]
        results: list[dict] = []

        async def get_one(symbol: str) -> None:
            """Collect the ratings actions for one symbol."""
            try:
                data = await get_nasdaq_data(f"analyst/{symbol}/ratings")
            except Exception as exc:  # noqa: BLE001
                warn(f"No analyst ratings were returned for {symbol}. {exc}")
                return

            for row in (data or {}).get("upgradesDowngrades") or []:
                results.append({**row, "symbol": symbol})

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError(
                "No rating changes were returned. Nasdaq only publishes recent"
                " upgrades and downgrades, and the list is often empty."
            )

        return results

    @staticmethod
    def transform_data(
        query: NasdaqPriceTargetQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqPriceTargetData]:
        """Transform the data to the standard format."""
        from openbb_nasdaq.utils.helpers import to_date, to_number

        results = [
            NasdaqPriceTargetData.model_validate(
                {
                    "symbol": row["symbol"],
                    "published_date": to_date(row.get("date")),
                    "analyst_firm": row.get("company") or row.get("firm"),
                    "rating_current": row.get("toRating") or row.get("rating"),
                    "rating_previous": row.get("fromRating"),
                    "action": row.get("action"),
                    "price_target": to_number(
                        row.get("toPT") or row.get("priceTarget")
                    ),
                    "price_target_previous": to_number(row.get("fromPT")),
                }
            )
            for row in data
        ]

        return sorted(
            results,
            key=lambda r: r.published_date or EPOCH,
            reverse=True,
        )[: query.limit]
