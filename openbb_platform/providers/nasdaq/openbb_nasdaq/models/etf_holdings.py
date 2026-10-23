"""Nasdaq ETF Holdings Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_holdings import (
    EtfHoldingsData,
    EtfHoldingsQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import ETF_SYMBOL_CHOICES_ENDPOINT


class NasdaqEtfHoldingsQueryParams(EtfHoldingsQueryParams):
    """Nasdaq ETF Holdings Query.

    Source: https://www.nasdaq.com/market-activity/etf
    """

    __json_schema_extra__ = {
        "symbol": {
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": ETF_SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
    }


class NasdaqEtfHoldingsData(EtfHoldingsData):
    """Nasdaq ETF Holdings Data.

    Nasdaq publishes the fund's ten largest positions. Exchange-traded funds
    are served from the company holdings endpoint and mutual funds from the
    fund profile, so a single command covers both.
    """

    symbol: str | None = Field(default=None, description="The symbol of the holding.")
    weight: float | None = Field(
        default=None,
        description="The position's weight in the fund, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )


class NasdaqEtfHoldingsFetcher(
    Fetcher[
        NasdaqEtfHoldingsQueryParams,
        list[NasdaqEtfHoldingsData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqEtfHoldingsQueryParams:
        """Transform the query."""
        return NasdaqEtfHoldingsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqEtfHoldingsQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        from openbb_nasdaq.utils.helpers import (
            get_nasdaq_data,
            resolve_asset_class,
            rows_from_table,
        )

        symbol = query.symbol.upper()
        asset_class = await resolve_asset_class(symbol)

        if asset_class == "mutualfunds":
            data = await get_nasdaq_data(f"funds/section/{symbol}")
            table = ((data or {}).get("TopTenHoldings") or {}).get(
                "topTenHoldingsTable"
            )

            return rows_from_table(table)

        data = await get_nasdaq_data(
            f"company/{symbol.lower()}/holdings?assetclass={asset_class}"
        )

        return ((data or {}).get("holdings") or {}).get("rows") or []

    @staticmethod
    def transform_data(
        query: NasdaqEtfHoldingsQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqEtfHoldingsData]:
        """Transform the data to the standard format.

        Raises
        ------
        EmptyDataError
            If Nasdaq publishes no holdings for the symbol.
        """
        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import to_percent

        if not data:
            raise EmptyDataError(f"No holdings were returned for {query.symbol}.")

        return [
            NasdaqEtfHoldingsData.model_validate(
                {
                    "symbol": row.get("symbol"),
                    "name": row.get("companyname") or row.get("name"),
                    "weight": to_percent(row.get("weighting") or row.get("assets")),
                }
            )
            for row in data
        ]
