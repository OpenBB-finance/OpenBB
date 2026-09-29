"""TMX Equity Profile fetcher."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_info import (
    EquityInfoData,
    EquityInfoQueryParams,
)
from pydantic import Field, field_validator, model_validator


class TmxEquityProfileQueryParams(EquityInfoQueryParams):
    """TMX Equity Profile query params."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class TmxEquityProfileData(EquityInfoData):
    """TMX Equity Profile Data."""

    __alias_dict__ = {
        "short_description": "shortDescription",
        "long_description": "longDescription",
        "company_url": "website",
        "business_phone_no": "phoneNumber",
        "business_address": "fullAddress",
        "stock_exchange": "exchangeCode",
        "industry_category": "industry",
        "industry_group": "qmdescription",
        "issue_type": "issueType",
        "share_outstanding": "shareOutStanding",
        "shares_escrow": "sharesESCROW",
        "total_shares_outstanding": "totalSharesOutStanding",
    }

    @field_validator("company_url", mode="before", check_fields=False)
    @classmethod
    def url_validate(cls, v):
        """Return the website as an absolute URL."""
        from openbb_tmx.utils.helpers import normalize_url

        return normalize_url(v)

    email: str | None = Field(description="The email of the company.", default=None)
    issue_type: str | None = Field(
        description="The issuance type of the asset.",
        default=None,
    )
    shares_outstanding: int | None = Field(
        description="The number of listed shares outstanding.",
        default=None,
    )
    shares_escrow: int | None = Field(
        description="The number of shares held in escrow.",
        default=None,
    )
    shares_total: int | None = Field(
        description="The total number of shares outstanding from all classes.",
        default=None,
    )
    dividend_frequency: str | None = Field(
        description="The dividend frequency.", default=None
    )

    @model_validator(mode="before")
    @classmethod
    def validate_empty_strings(cls, values) -> dict:
        """Validate the query parameters."""
        return {k: None if v == "" else v for k, v in values.items()}


class TmxEquityProfileFetcher(
    Fetcher[
        TmxEquityProfileQueryParams,
        list[TmxEquityProfileData],
    ]
):
    """TMX Equity Profile Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> TmxEquityProfileQueryParams:
        """Transform the query."""
        return TmxEquityProfileQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: TmxEquityProfileQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the TMX endpoint."""
        import asyncio

        from openbb_tmx.utils import gql
        from openbb_tmx.utils.cache import amake_gql_request
        from openbb_tmx.utils.helpers import normalize_symbol

        symbols = query.symbol.split(",")
        results: list[dict] = []

        async def create_task(symbol: str, results) -> None:
            """Fetch the profile for a single symbol."""
            symbol = normalize_symbol(symbol)
            response = await amake_gql_request(
                "getQuoteBySymbol",
                gql.QUOTE_BY_SYMBOL,
                {"symbol": symbol, "locale": "en"},
                symbol=symbol,
            )

            if response and response.get("getQuoteBySymbol"):
                results.append(response["getQuoteBySymbol"])

        tasks = [create_task(symbol, results) for symbol in symbols]
        await asyncio.gather(*tasks)
        return results

    @staticmethod
    def transform_data(
        query: TmxEquityProfileQueryParams,
        data: list[dict],
        **kwargs: Any,
    ) -> list[TmxEquityProfileData]:
        """Return the transformed data."""
        items_list = [
            "shortDescription",
            "longDescription",
            "website",
            "phoneNumber",
            "fullAddress",
            "sector",
            "qmdescription",
            "industry",
            "exchangeCode",
            "shareOutStanding",
            "sharesESCROW",
            "totalSharesOutStanding",
            "email",
            "issueType",
            "name",
            "symbol",
            "dividendFrequency",
            "employees",
        ]
        data = [{k: v for k, v in d.items() if k in items_list} for d in data]
        symbols = query.symbol.split(",")
        symbol_to_index = {symbol: index for index, symbol in enumerate(symbols)}
        data = sorted(data, key=lambda d: symbol_to_index[d["symbol"]])

        return [TmxEquityProfileData.model_validate(d) for d in data]
