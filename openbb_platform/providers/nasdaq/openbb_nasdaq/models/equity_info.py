"""Nasdaq Equity Info Model."""

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_info import (
    EquityInfoData,
    EquityInfoQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import SYMBOL_CHOICES_ENDPOINT


class NasdaqEquityInfoQueryParams(EquityInfoQueryParams):
    """Nasdaq Equity Info Query.

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


class NasdaqEquityInfoData(EquityInfoData):
    """Nasdaq Equity Info Data."""

    region: str | None = Field(
        default=None, description="The region the company is domiciled in."
    )
    exchange: str | None = Field(
        default=None, description="The exchange the security trades on."
    )
    stock_type: str | None = Field(
        default=None, description="The type of security - i.e., Common Stock."
    )
    is_nasdaq_100: bool | None = Field(
        default=None, description="Whether the security is a Nasdaq-100 constituent."
    )


class NasdaqEquityInfoFetcher(
    Fetcher[
        NasdaqEquityInfoQueryParams,
        list[NasdaqEquityInfoData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqEquityInfoQueryParams:
        """Transform the query."""
        return NasdaqEquityInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqEquityInfoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        import asyncio
        from warnings import warn

        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import get_nasdaq_data

        symbols = [s.strip().upper() for s in query.symbol.split(",") if s.strip()]
        results: list[dict] = []

        async def get_one(symbol: str) -> None:
            """Collect the profile and info payloads for one symbol."""
            try:
                profile, info = await asyncio.gather(
                    get_nasdaq_data(f"company/{symbol}/company-profile"),
                    get_nasdaq_data(f"quote/{symbol}/info?assetclass=stocks"),
                )
            except Exception as exc:  # noqa: BLE001
                warn(f"No profile was returned for {symbol}. {exc}")
                return

            results.append(
                {"symbol": symbol, "profile": profile or {}, "info": info or {}}
            )

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No company profiles were returned for any symbol.")

        return results

    @staticmethod
    def transform_data(
        query: NasdaqEquityInfoQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqEquityInfoData]:
        """Transform the data to the standard format."""
        results: list[NasdaqEquityInfoData] = []

        for item in data:
            profile = item["profile"]
            info = item["info"]

            def value(key: str, block: dict = profile) -> Any:
                """Pull the display value out of a label/value block."""
                return (block.get(key) or {}).get("value")

            results.append(
                NasdaqEquityInfoData.model_validate(
                    {
                        "symbol": item["symbol"],
                        "name": value("CompanyName") or info.get("companyName"),
                        "long_description": value("CompanyDescription"),
                        "industry": value("Industry"),
                        "sector": value("Sector"),
                        "region": value("Region"),
                        "address": value("Address"),
                        "phone_number": value("Phone"),
                        "exchange": info.get("exchange"),
                        "stock_type": info.get("stockType"),
                        "is_nasdaq_100": info.get("isNasdaq100"),
                    }
                )
            )

        return results
