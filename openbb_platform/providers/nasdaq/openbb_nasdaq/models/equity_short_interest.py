"""Nasdaq Equity Short Interest Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_short_interest import (
    ShortInterestData,
    ShortInterestQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import SYMBOL_CHOICES_ENDPOINT

EPOCH = dateType(1900, 1, 1)


class NasdaqEquityShortInterestQueryParams(ShortInterestQueryParams):
    """Nasdaq Equity Short Interest Query.

    Source: https://www.nasdaq.com/market-activity/stocks
    """

    __json_schema_extra__ = {
        "symbol": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
    }


class NasdaqEquityShortInterestData(ShortInterestData):
    """Nasdaq Equity Short Interest Data.

    Nasdaq publishes the bi-monthly settlement series only, so the fields the
    standard model marks required but Nasdaq omits are relaxed to optional.
    """

    issue_name: str | None = Field(default=None, description="The name of the issue.")
    market_class: str | None = Field(
        default=None, description="The market classification of the issue."
    )
    previous_short_position: float | None = Field(
        default=None, description="The short interest at the prior settlement."
    )
    change: float | None = Field(
        default=None, description="The change from the prior settlement."
    )
    change_pct: float | None = Field(
        default=None,
        description="The change from the prior settlement, as a normalized percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class NasdaqEquityShortInterestFetcher(
    Fetcher[
        NasdaqEquityShortInterestQueryParams,
        list[NasdaqEquityShortInterestData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(
        params: dict[str, Any],
    ) -> NasdaqEquityShortInterestQueryParams:
        """Transform the query."""
        return NasdaqEquityShortInterestQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqEquityShortInterestQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import get_nasdaq_data, rows_from_table

        symbol = query.symbol.upper()
        data = await get_nasdaq_data(f"quote/{symbol}/short-interest?assetClass=stocks")
        rows = rows_from_table((data or {}).get("shortInterestTable"))

        if not rows:
            raise EmptyDataError(f"No short interest was found for {symbol}.")

        return [{**row, "symbol": symbol} for row in rows]

    @staticmethod
    def transform_data(
        query: NasdaqEquityShortInterestQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqEquityShortInterestData]:
        """Transform the data to the standard format."""
        from openbb_nasdaq.utils.helpers import to_date, to_number

        results: list[NasdaqEquityShortInterestData] = []
        previous: float | None = None

        for row in sorted(
            data,
            key=lambda r: to_date(r.get("settlementDate")) or EPOCH,
        ):
            current = to_number(row.get("interest"))
            change = (
                current - previous
                if current is not None and previous is not None
                else None
            )
            results.append(
                NasdaqEquityShortInterestData.model_validate(
                    {
                        "symbol": row["symbol"],
                        "settlement_date": to_date(row.get("settlementDate")),
                        "current_short_position": current,
                        "previous_short_position": previous,
                        "avg_daily_volume": to_number(row.get("avgDailyShareVolume")),
                        "days_to_cover": to_number(row.get("daysToCover")),
                        "change": change,
                        "change_pct": (
                            change / previous
                            if change is not None and previous
                            else None
                        ),
                    }
                )
            )
            previous = current

        return list(reversed(results))
