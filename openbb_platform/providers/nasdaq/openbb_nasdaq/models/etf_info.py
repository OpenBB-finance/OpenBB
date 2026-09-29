"""Nasdaq ETF Info Model."""

from datetime import date as dateType
from typing import Any

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.etf_info import (
    EtfInfoData,
    EtfInfoQueryParams,
)
from pydantic import Field

from openbb_nasdaq.utils.constants import ETF_SYMBOL_CHOICES_ENDPOINT

KEY_DATA_FIELDS = {
    "aum": "AUM",
    "expense_ratio": "ExpenseRatio",
    "market_cap": "MarketCap",
    "previous_close": "PreviousClose",
    "volume": "ShareVolume",
    "alpha": "Alpha",
    "weighted_alpha": "WeightedAlpha",
    "beta": "Beta",
    "standard_deviation": "StandardDeviation",
    "volume_avg_20d": "AvgDailyVol20Days",
    "volume_avg_50d": "FiftyDayAvgDailyVol",
    "volume_avg_65d": "AvgDailyVol65Days",
}

FUND_SECTION_FIELDS = {
    "previous_close": ("PerformanceSummary", "PreviousClose"),
    "aum": ("PerformanceSummary", "TotalNetAssets"),
    "last_dividend": ("PerformanceSummary", "LastDividend"),
    "expense_ratio": ("FeesAndExpenses", "totalExpenseRatio"),
    "management_fee": ("FeesAndExpenses", "managementFees"),
    "distribution_fee": ("FeesAndExpenses", "account12b1Fees"),
    "other_expenses": ("FeesAndExpenses", "otherExpenses"),
    "front_load": ("FeesAndExpenses", "frontLoad"),
    "minimum_initial_investment": ("FeesAndExpenses", "minimumInitialSubscription"),
}

FUND_PERCENT_FIELDS = {
    "expense_ratio",
    "management_fee",
    "distribution_fee",
    "other_expenses",
    "front_load",
}

FUND_TEXT_FIELDS = {
    "investment_category": ("AboutTheFund", "fundInvestmentCategory"),
    "investment_focus": ("AboutTheFund", "investmentFocus"),
    "asset_focus": ("AboutTheFund", "assetFocus"),
    "management_style": ("AboutTheFund", "managementStyle"),
    "portfolio_type": ("AboutTheFund", "portfolioType"),
    "industry_alignment": ("AboutTheFund", "industryAlignment"),
    "country_of_issuance": ("AboutTheFund", "countryOfIssuance"),
}


class NasdaqEtfInfoQueryParams(EtfInfoQueryParams):
    """Nasdaq ETF Info Query.

    Source: https://www.nasdaq.com/market-activity/etf
    """

    __json_schema_extra__ = {
        "symbol": {
            "multiple_items_allowed": True,
            "x-widget_config": {
                "type": "endpoint",
                "optionsEndpoint": ETF_SYMBOL_CHOICES_ENDPOINT,
                "style": {"popupWidth": 850},
            },
        },
    }


class NasdaqEtfInfoData(EtfInfoData):
    """Nasdaq ETF Info Data.

    The 'Key Data' block published on the Nasdaq ETF quote page. Mutual funds
    carry the fund profile instead, so the populated fields differ by symbol.
    """

    aum: float | None = Field(
        default=None,
        description="Assets under management, in thousands.",
    )
    expense_ratio: float | None = Field(
        default=None,
        description="The fund expense ratio, as a normalized percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    market_cap: float | None = Field(
        default=None, description="The market capitalization of the fund."
    )
    previous_close: float | None = Field(
        default=None, description="The previous session's closing price."
    )
    volume: float | None = Field(default=None, description="The last session's volume.")
    volume_avg_20d: float | None = Field(
        default=None, description="The 20-day average daily volume."
    )
    volume_avg_50d: float | None = Field(
        default=None, description="The 50-day average daily volume."
    )
    volume_avg_65d: float | None = Field(
        default=None, description="The 65-day average daily volume."
    )
    alpha: float | None = Field(default=None, description="The fund's alpha.")
    weighted_alpha: float | None = Field(
        default=None, description="The fund's weighted alpha."
    )
    beta: float | None = Field(default=None, description="The fund's beta.")
    standard_deviation: float | None = Field(
        default=None, description="The fund's standard deviation."
    )
    year_high: float | None = Field(default=None, description="The 52-week high price.")
    year_low: float | None = Field(default=None, description="The 52-week low price.")
    last_dividend: float | None = Field(
        default=None, description="The most recent distribution amount."
    )
    management_fee: float | None = Field(
        default=None,
        description="The management fee, as a normalized percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    distribution_fee: float | None = Field(
        default=None,
        description="The account or 12b-1 fee, as a normalized percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    other_expenses: float | None = Field(
        default=None,
        description="Other expenses, as a normalized percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    front_load: float | None = Field(
        default=None,
        description="The front load, as a normalized percentage.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    minimum_initial_investment: float | None = Field(
        default=None, description="The minimum initial investment."
    )
    inception_date: dateType | None = Field(
        default=None, description="The fund's inception date."
    )
    investment_category: str | None = Field(
        default=None, description="The fund investment category."
    )
    investment_focus: str | None = Field(
        default=None, description="The fund's investment focus."
    )
    asset_focus: str | None = Field(default=None, description="The fund's asset focus.")
    management_style: str | None = Field(
        default=None, description="The fund's management style."
    )
    portfolio_type: str | None = Field(
        default=None, description="The fund's portfolio type."
    )
    industry_alignment: str | None = Field(
        default=None, description="The fund's industry alignment."
    )
    country_of_issuance: str | None = Field(
        default=None, description="The fund's country of issuance."
    )


class NasdaqEtfInfoFetcher(
    Fetcher[
        NasdaqEtfInfoQueryParams,
        list[NasdaqEtfInfoData],
    ]
):
    """Transform the query, extract and transform the data from the Nasdaq endpoints."""

    require_credentials = False

    @staticmethod
    def transform_query(params: dict[str, Any]) -> NasdaqEtfInfoQueryParams:
        """Transform the query."""
        return NasdaqEtfInfoQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: NasdaqEtfInfoQueryParams,
        credentials: dict[str, str] | None,
        **kwargs: Any,
    ) -> list[dict]:
        """Return the raw data from the Nasdaq endpoint."""
        import asyncio
        from warnings import warn

        from openbb_core.provider.utils.errors import EmptyDataError

        from openbb_nasdaq.utils.helpers import get_nasdaq_data, resolve_asset_class

        symbols = [s.strip().upper() for s in query.symbol.split(",") if s.strip()]
        results: list[dict] = []

        async def get_one(symbol: str) -> None:
            """Collect the profile payloads for one fund."""
            asset_class = await resolve_asset_class(symbol)

            try:
                if asset_class == "mutualfunds":
                    section, info = await asyncio.gather(
                        get_nasdaq_data(f"funds/section/{symbol}"),
                        get_nasdaq_data(f"quote/{symbol}/info?assetclass=mutualfunds"),
                    )
                    results.append(
                        {"symbol": symbol, "section": section or {}, "info": info or {}}
                    )

                    return

                summary, info = await asyncio.gather(
                    get_nasdaq_data(f"quote/{symbol}/summary?assetclass={asset_class}"),
                    get_nasdaq_data(f"quote/{symbol}/info?assetclass={asset_class}"),
                )
            except Exception as exc:  # noqa: BLE001
                warn(f"No key data was returned for {symbol}. {exc}")
                return

            results.append(
                {"symbol": symbol, "summary": summary or {}, "info": info or {}}
            )

        await asyncio.gather(*[get_one(symbol) for symbol in symbols])

        if not results:
            raise EmptyDataError("No ETF key data was returned for any symbol.")

        return results

    @staticmethod
    def transform_data(
        query: NasdaqEtfInfoQueryParams, data: list[dict], **kwargs: Any
    ) -> list[NasdaqEtfInfoData]:
        """Transform the data to the standard format."""
        from openbb_nasdaq.models.equity_quote import _split_range
        from openbb_nasdaq.utils.helpers import (
            clean_value,
            to_date,
            to_number,
            to_percent,
        )

        results: list[NasdaqEtfInfoData] = []

        for item in data:
            info = item["info"] or {}
            record: dict[str, Any] = {
                "symbol": item["symbol"],
                "name": info.get("companyName"),
            }

            if "section" in item:
                section = item["section"] or {}

                def section_value(block: str, key: str, source: dict = section) -> Any:
                    """Pull the display value out of a fund profile block."""
                    return ((source.get(block) or {}).get(key) or {}).get("value")

                for field, (block, key) in FUND_SECTION_FIELDS.items():
                    raw = section_value(block, key)
                    record[field] = (
                        to_percent(raw)
                        if field in FUND_PERCENT_FIELDS
                        else to_number(raw)
                    )

                for field, (block, key) in FUND_TEXT_FIELDS.items():
                    value = clean_value(section_value(block, key))
                    record[field] = None if value == "Not Assigned" else value

                record["inception_date"] = to_date(
                    section_value("AboutTheFund", "inceptionDate")
                )
                results.append(NasdaqEtfInfoData.model_validate(record))

                continue

            summary = (item["summary"] or {}).get("summaryData") or {}

            for field, key in KEY_DATA_FIELDS.items():
                raw = (summary.get(key) or {}).get("value")
                record[field] = (
                    to_percent(raw) if field == "expense_ratio" else to_number(raw)
                )

            high, low = _split_range(
                (summary.get("FiftTwoWeekHighLow") or {}).get("value")
            )
            record["year_high"] = high
            record["year_low"] = low
            results.append(NasdaqEtfInfoData.model_validate(record))

        return results
