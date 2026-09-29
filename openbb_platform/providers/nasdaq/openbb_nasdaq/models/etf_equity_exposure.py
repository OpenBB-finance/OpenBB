"""Nasdaq ETF Equity Exposure Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_equity_exposure import (
    EtfEquityExposureData,
    EtfEquityExposureQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import SYMBOL_CHOICES_ENDPOINT


class NasdaqEtfEquityExposureQueryParams(EtfEquityExposureQueryParams):
    """Nasdaq ETF Equity Exposure Query.

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


class NasdaqEtfEquityExposureData(EtfEquityExposureData):
    """Nasdaq ETF Equity Exposure Data.

    Nasdaq lists only the funds carrying the equity as a top-ten holding.
    """

    etf_name: str | None = Field(default=None, description="The name of the fund.")
    price_change_100_day: float | None = Field(
        default=None,
        description="The fund's price change over the trailing one hundred days.",
    )
    price_change_100_day_percent: float | None = Field(
        default=None,
        description="The fund's percent price change over the trailing one hundred"
        + " days, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class NasdaqEtfEquityExposureFetcher(
    Fetcher[
        NasdaqEtfEquityExposureQueryParams,
        list[NasdaqEtfEquityExposureData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqEtfEquityExposureQueryParams:
        """Transform the query."""
        return NasdaqEtfEquityExposureQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqEtfEquityExposureQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import get_nasdaq_data, resolve_asset_class

        symbol = query.symbol.upper()
        asset_class = await resolve_asset_class(symbol)
        data = await get_nasdaq_data(
            f"company/{symbol.lower()}/holdings?assetclass={asset_class}"
        )

        return ((data or {}).get("holdings") or {}).get("rows") or []

    @staticmethod
    def transform_data(
        query: NasdaqEtfEquityExposureQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqEtfEquityExposureData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If no fund carries the equity as a top-ten holding.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import to_number, to_percent

        if not data:
            raise EmptyDataError(
                f"No fund reports {query.symbol} as a top-ten holding."
            )

        results: list[NasdaqEtfEquityExposureData] = []

        for row in data:
            change, _, percent = (row.get("priceChange100Day") or "").partition("(")
            results.append(
                NasdaqEtfEquityExposureData.model_validate(
                    {
                        "equity_symbol": query.symbol,
                        "etf_symbol": row.get("symbol"),
                        "etf_name": row.get("companyname"),
                        "weight": to_percent(row.get("weighting")),
                        "price_change_100_day": to_number(change),
                        "price_change_100_day_percent": to_percent(percent.rstrip(")")),
                    }
                )
            )

        return results
