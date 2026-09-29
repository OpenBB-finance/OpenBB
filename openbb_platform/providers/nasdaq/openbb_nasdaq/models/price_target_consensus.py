"""Nasdaq Price Target Consensus Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.price_target_consensus import (
    PriceTargetConsensusData,
    PriceTargetConsensusQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import SYMBOL_CHOICES_ENDPOINT


class NasdaqPriceTargetConsensusQueryParams(PriceTargetConsensusQueryParams):
    """Nasdaq Price Target Consensus Query.

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


class NasdaqPriceTargetConsensusData(PriceTargetConsensusData):
    """Nasdaq Price Target Consensus Data."""

    buy_ratings: int | None = Field(
        default=None, description="The number of buy ratings."
    )
    hold_ratings: int | None = Field(
        default=None, description="The number of hold ratings."
    )
    sell_ratings: int | None = Field(
        default=None, description="The number of sell ratings."
    )
    consensus_rating: str | None = Field(
        default=None, description="The mean analyst rating."
    )


class NasdaqPriceTargetConsensusFetcher(
    Fetcher[
        NasdaqPriceTargetConsensusQueryParams,
        list[NasdaqPriceTargetConsensusData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> NasdaqPriceTargetConsensusQueryParams:
        """Transform the query."""
        return NasdaqPriceTargetConsensusQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqPriceTargetConsensusQueryParams,
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
            """Collect the consensus and rating payloads for one symbol."""
            try:
                target, ratings = await asyncio.gather(
                    get_nasdaq_data(f"analyst/{symbol}/targetprice"),
                    get_nasdaq_data(f"analyst/{symbol}/ratings"),
                    return_exceptions=True,
                )
            except Exception as exc:  # noqa: BLE001
                warn(f"No price target was returned for {symbol}. {exc}")
                return

            if isinstance(target, BaseException) or not target:
                warn(f"No price target was returned for {symbol}.")
                return

            results.append(
                {
                    "symbol": symbol,
                    "target": target,
                    "ratings": {}
                    if isinstance(ratings, BaseException)
                    else (ratings or {}),
                }
            )

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No price targets were returned for any symbol.")

        return results

    @staticmethod
    def transform_data(
        query: NasdaqPriceTargetConsensusQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqPriceTargetConsensusData]:
        """Transform the data to the standard format."""
        from openbb_nasdaq.utils.helpers import to_number

        results: list[NasdaqPriceTargetConsensusData] = []

        for item in data:
            overview = (item["target"] or {}).get("consensusOverview") or {}
            results.append(
                NasdaqPriceTargetConsensusData.model_validate(
                    {
                        "symbol": item["symbol"],
                        "target_high": to_number(overview.get("highPriceTarget")),
                        "target_low": to_number(overview.get("lowPriceTarget")),
                        "target_consensus": to_number(overview.get("priceTarget")),
                        "buy_ratings": to_number(overview.get("buy")),
                        "hold_ratings": to_number(overview.get("hold")),
                        "sell_ratings": to_number(overview.get("sell")),
                        "consensus_rating": (item["ratings"] or {}).get(
                            "meanRatingType"
                        ),
                    }
                )
            )

        return results
