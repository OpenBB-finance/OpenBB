"""FMP Equity Screener Model."""

# pylint: disable=unused-argument

from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_screener import (
    EquityScreenerData,
    EquityScreenerQueryParams,
)
from openbb_core.provider.utils.errors import EmptyDataError
from openbb_fmp.utils.definitions import (
    Countries,
    Exchanges,
    IndustryChoices,
    Sectors,
)
from pydantic import Field, field_validator


class FMPEquityScreenerQueryParams(EquityScreenerQueryParams):
    """FMP Equity Screener Query."""

    __json_schema_extra__ = {
        "industry": {
            "x-widget_config": {
                "options": IndustryChoices,
            },
        },
        "sector": {
            "x-widget_config": {
                "options": [
                    {"label": sector.replace("_", " ").title(), "value": sector}
                    for sector in Sectors.__args__
                ],
            },
        },
        "exchange": {
            "x-widget_config": {
                "options": [
                    {"label": exchange.upper(), "value": exchange}
                    for exchange in Exchanges.__args__
                ],
            },
        },
        "country": {
            "x-widget_config": {
                "options": [
                    {"label": country.upper(), "value": country}
                    for country in Countries.__args__
                ],
            },
        },
    }

    __alias_dict__ = {
        "mktcap_min": "marketCapMoreThan",
        "mktcap_max": "marketCapLowerThan",
        "price_min": "priceMoreThan",
        "price_max": "priceLowerThan",
        "beta_min": "betaMoreThan",
        "beta_max": "betaLowerThan",
        "volume_min": "volumeMoreThan",
        "volume_max": "volumeLowerThan",
        "dividend_min": "dividendMoreThan",
        "dividend_max": "dividendLowerThan",
        "is_active": "isActivelyTrading",
        "is_etf": "isEtf",
        "is_fund": "isFund",
        "all_share_classes": "includeAllShareClasses",
    }

    mktcap_min: int | None = Field(
        default=None,
        description="Filter by market cap greater than this value.",
        title="Mkt Cap Min",
    )
    mktcap_max: int | None = Field(
        default=None,
        description="Filter by market cap less than this value.",
        title="Mkt Cap Max",
    )
    price_min: float | None = Field(
        default=None,
        description="Filter by price greater than this value.",
    )
    price_max: float | None = Field(
        default=None,
        description="Filter by price less than this value.",
    )
    beta_min: float | None = Field(
        default=None,
        description="Filter by a beta greater than this value.",
    )
    beta_max: float | None = Field(
        default=None,
        description="Filter by a beta less than this value.",
    )
    volume_min: int | None = Field(
        default=None,
        description="Filter by volume greater than this value.",
    )
    volume_max: int | None = Field(
        default=None,
        description="Filter by volume less than this value.",
    )
    dividend_min: float | None = Field(
        default=None,
        description="Filter by dividend amount greater than this value.",
    )
    dividend_max: float | None = Field(
        default=None,
        description="Filter by dividend amount less than this value.",
    )
    sector: Sectors | None = Field(
        default=None,
        description="Filter by sector.",
    )
    industry: str | None = Field(
        default=None,
        description="Filter by industry.",
    )
    country: Countries | None = Field(
        default=None, description="Filter by country, as a two-letter country code."
    )
    exchange: Exchanges | None = Field(default=None, description="Filter by exchange.")
    is_etf: bool | None = Field(
        default=None,
        description="If true, includes ETFs.",
    )
    is_active: bool | None = Field(
        default=None,
        description="If false, returns only inactive tickers.",
    )
    is_fund: bool | None = Field(
        default=None,
        description="If true, includes funds.",
    )
    all_share_classes: bool | None = Field(
        default=None,
        description="If true, includes all share classes of a equity.",
    )
    limit: int | None = Field(
        default=50000, description="Limit the number of results to return."
    )

    @field_validator("industry")
    @classmethod
    def _validate_industry(cls, v):
        """Validate industry."""
        industries = [v["value"] for v in IndustryChoices]
        if v and v not in industries + ["all"]:
            raise ValueError(f"Industry must be one of {', '.join(industries)}")
        return v


class FMPEquityScreenerData(EquityScreenerData):
    """FMP Equity Screener Data."""

    __alias_dict__ = {
        "name": "companyName",
        "market_cap": "marketCap",
        "last_annual_dividend": "lastAnnualDividend",
        "exchange": "exchangeShortName",
        "exchange_name": "exchange",
        "is_etf": "isEtf",
        "actively_trading": "isActivelyTrading",
    }

    market_cap: int | None = Field(
        description="The market cap of ticker.", default=None
    )
    sector: str | None = Field(
        description="The sector the ticker belongs to.",
        default=None,
    )
    industry: str | None = Field(
        description="The industry ticker belongs to.", default=None
    )
    beta: float | None = Field(description="The beta of the ETF.", default=None)
    price: float | None = Field(description="The current price.", default=None)
    last_annual_dividend: float | None = Field(
        description="The last annual amount dividend paid.",
        default=None,
    )
    volume: int | None = Field(description="The current trading volume.", default=None)
    exchange: str | None = Field(
        description="The exchange code the asset trades on.",
        default=None,
    )
    exchange_name: str | None = Field(
        description="The full name of the primary exchange.",
        default=None,
    )
    country: str | None = Field(
        description="The two-letter country abbreviation where the head office is located.",
        default=None,
    )
    is_etf: bool | None = Field(
        description="Whether the ticker is an ETF.", default=None
    )
    is_fund: bool | None = Field(
        description="Whether the ticker is a fund.", default=None
    )
    actively_trading: bool | None = Field(
        description="Whether the ETF is actively trading.",
        default=None,
    )


class FMPEquityScreenerFetcher(
    Fetcher[
        FMPEquityScreenerQueryParams,
        list[FMPEquityScreenerData],
    ]
):
    """FMP Equity Screener Fetcher."""

    @staticmethod
    def transform_query(params: dict[str, Any]) -> FMPEquityScreenerQueryParams:
        """Transform the query."""
        return FMPEquityScreenerQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: FMPEquityScreenerQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the FMP endpoint."""
        # pylint: disable=import-outside-toplevel
        from openbb_core.provider.utils.helpers import get_querystring
        from openbb_fmp.utils.helpers import get_data

        api_key = credentials.get("fmp_api_key") if credentials else ""
        sector: str = (
            query.sector.replace("_", " ").title().replace(" ", "%20")
            if query.sector
            else ""
        )
        industry_map = {v["value"]: v["label"] for v in IndustryChoices}
        industry: str = (
            industry_map.get(query.industry, query.industry) if query.industry else ""
        )
        industry = (
            industry.replace(" & ", "%20%26%20")
            .replace(" ", "%20")
            .replace("/", "%2F")
            .replace("-", "%2D")
            .replace(",", "%2C")
        )
        exchange: str = query.exchange.upper() if query.exchange else ""
        country: str = query.country.upper() if query.country else ""
        query.is_active = True if query.is_active is None else query.is_active
        query.is_etf = False if query.is_etf is None else query.is_etf
        query.is_fund = False if query.is_fund is None else query.is_fund
        query.all_share_classes = (
            False if query.all_share_classes is None else query.all_share_classes
        )

        query_dict = query.model_dump(exclude_none=True, by_alias=True)

        if sector:
            query_dict["sector"] = sector
        if industry:
            query_dict["industry"] = industry
        if exchange:
            query_dict["exchange"] = exchange
        if country:
            query_dict["country"] = country

        query_str = (
            get_querystring(query_dict, exclude=["query"])
            .replace("True", "true")
            .replace("False", "false")
        )
        base_url = "https://financialmodelingprep.com/stable/company-screener"
        url = f"{base_url}?{query_str}&apikey={api_key}"

        return await get_data(url, **kwargs)  # type: ignore

    @staticmethod
    def transform_data(
        query: FMPEquityScreenerQueryParams, data: list[dict], **kwargs: Any
    ) -> list[FMPEquityScreenerData]:
        """Return the transformed data."""
        if not data:
            raise EmptyDataError("The request was returned empty.")
        return [
            FMPEquityScreenerData.model_validate(d)
            for d in sorted(data, key=lambda x: x["marketCap"], reverse=True)
        ]
