"""YFinance Key Metrics Model."""

# pylint: disable=unused-argument
import asyncio
import warnings
from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.key_metrics import (
    KeyMetricsData,
    KeyMetricsQueryParams,
)
from pydantic import Field, field_validator
from yfinance import Ticker

_warn = warnings.warn


class YFinanceKeyMetricsQueryParams(KeyMetricsQueryParams):
    """YFinance Key Metrics Query."""

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class YFinanceKeyMetricsData(KeyMetricsData):
    """YFinance Key Metrics Data."""

    __alias_dict__ = {
        "market_cap": "marketCap",
        "pe_ratio": "trailingPE",
    }
    forward_pe: Optional[float] = Field(
        default=None,
        description="Forward price-to-earnings ratio.",
        alias="forwardPE",
    )
    peg_ratio: Optional[float] = Field(
        default=None,
        description="PEG ratio (5-year expected).",
        alias="pegRatio",
    )
    peg_ratio_ttm: Optional[float] = Field(
        default=None,
        description="PEG ratio (TTM).",
        alias="trailingPegRatio",
    )
    eps_ttm: Optional[float] = Field(
        default=None,
        description="Earnings per share (TTM).",
        alias="trailingEps",
    )
    eps_forward: Optional[float] = Field(
        default=None,
        description="Forward earnings per share.",
        alias="forwardEps",
    )
    enterprise_to_ebitda: Optional[float] = Field(
        default=None,
        description="Enterprise value to EBITDA ratio.",
        alias="enterpriseToEbitda",
    )
    earnings_growth: Optional[float] = Field(
        default=None,
        description="Earnings growth (Year Over Year), as a normalized percent.",
        alias="earningsGrowth",
    )
    earnings_growth_quarterly: Optional[float] = Field(
        default=None,
        description="Quarterly earnings growth (Year Over Year), as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="earningsQuarterlyGrowth",
    )
    revenue_per_share: Optional[float] = Field(
        default=None,
        description="Revenue per share (TTM).",
        alias="revenuePerShare",
    )
    revenue_growth: Optional[float] = Field(
        default=None,
        description="Revenue growth (Year Over Year), as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="revenueGrowth",
    )
    enterprise_to_revenue: Optional[float] = Field(
        default=None,
        description="Enterprise value to revenue ratio.",
        alias="enterpriseToRevenue",
    )
    cash_per_share: Optional[float] = Field(
        default=None,
        description="Cash per share.",
        alias="totalCashPerShare",
    )
    quick_ratio: Optional[float] = Field(
        default=None,
        description="Quick ratio.",
        alias="quickRatio",
    )
    current_ratio: Optional[float] = Field(
        default=None,
        description="Current ratio.",
        alias="currentRatio",
    )
    debt_to_equity: Optional[float] = Field(
        default=None,
        description="Debt-to-equity ratio.",
        alias="debtToEquity",
    )
    gross_margin: Optional[float] = Field(
        default=None,
        description="Gross margin, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="grossMargins",
    )
    operating_margin: Optional[float] = Field(
        default=None,
        description="Operating margin, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="operatingMargins",
    )
    ebitda_margin: Optional[float] = Field(
        default=None,
        description="EBITDA margin, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="ebitdaMargins",
    )
    profit_margin: Optional[float] = Field(
        default=None,
        description="Profit margin, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="profitMargins",
    )
    return_on_assets: Optional[float] = Field(
        default=None,
        description="Return on assets, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="returnOnAssets",
    )
    return_on_equity: Optional[float] = Field(
        default=None,
        description="Return on equity, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="returnOnEquity",
    )
    dividend_yield: Optional[float] = Field(
        default=None,
        description="Dividend yield, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="dividendYield",
    )
    dividend_yield_5y_avg: Optional[float] = Field(
        default=None,
        description="5-year average dividend yield, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="fiveYearAvgDividendYield",
    )
    payout_ratio: Optional[float] = Field(
        default=None,
        description="Payout ratio.",
    )
    book_value: Optional[float] = Field(
        default=None,
        description="Book value per share.",
        alias="bookValue",
    )
    price_to_book: Optional[float] = Field(
        default=None,
        description="Price-to-book ratio.",
        alias="priceToBook",
    )
    enterprise_value: Optional[int] = Field(
        default=None,
        description="Enterprise value.",
        alias="enterpriseValue",
    )
    overall_risk: Optional[float] = Field(
        default=None,
        description="Overall risk score.",
        alias="overallRisk",
    )
    audit_risk: Optional[float] = Field(
        default=None,
        description="Audit risk score.",
        alias="auditRisk",
    )
    board_risk: Optional[float] = Field(
        default=None,
        description="Board risk score.",
        alias="boardRisk",
    )
    compensation_risk: Optional[float] = Field(
        default=None,
        description="Compensation risk score.",
        alias="compensationRisk",
    )
    shareholder_rights_risk: Optional[float] = Field(
        default=None,
        description="Shareholder rights risk score.",
        alias="shareHolderRightsRisk",
    )
    beta: Optional[float] = Field(
        default=None,
        description="Beta relative to the broad market (5-year monthly).",
    )
    price_return_1y: Optional[float] = Field(
        default=None,
        description="One-year price return, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
        alias="52WeekChange",
    )
    currency: Optional[str] = Field(
        default=None,
        description="Currency in which the data is presented.",
        alias="financialCurrency",
    )

    @field_validator("dividend_yield_5y_avg")
    @classmethod
    def normalize_percent(cls, v: float):
        """Normalize the percent values."""
        return float(v) / 100 if v else None


class YFinanceKeyMetricsFetcher(
    Fetcher[YFinanceKeyMetricsQueryParams, List[YFinanceKeyMetricsData]]
):
    """YFinance Key Metrics fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> YFinanceKeyMetricsQueryParams:
        """Transform the query."""
        return YFinanceKeyMetricsQueryParams(**params)

    @staticmethod
    async def aextract_data(
        query: YFinanceKeyMetricsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from YFinance."""
        symbols = query.symbol.split(",")
        results = []
        fields = [
            "symbol",
            "marketCap",
            "trailingPE",
            "forwardPE",
            "pegRatio",
            "trailingPegRatio",
            "earningsQuarterlyGrowth",
            "earningsGrowth",
            "revenuePerShare",
            "revenueGrowth",
            "cashPerShare",
            "quickRatio",
            "currentRatio",
            "debtToEquity",
            "grossMargins",
            "ebitdaMargins",
            "operatingMargins",
            "profitMargins",
            "returnOnAssets",
            "returnOnEquity",
            "dividendYield",
            "fiveYearAvgDividendYield",
            "payoutRatio",
            "bookValue",
            "priceToBook",
            "enterpriseValue",
            "enterpriseToRevenue",
            "enterpriseToEbitda",
            "overallRisk",
            "auditRisk",
            "boardRisk",
            "compensationRisk",
            "shareHolderRightsRisk",
            "beta",
            "52WeekChange",
            "financialCurrency",
        ]

        async def get_one(symbol):
            """Get the data for one ticker symbol."""
            result = {}
            ticker = {}
            try:
                ticker = Ticker(symbol).get_info()
            except Exception as e:
                _warn(f"Error getting data for {symbol}: {e}")
            if ticker:
                for field in fields:
                    if field in ticker:
                        result[field] = ticker.get(field, None)
                if result and result.get("52WeekChange") is not None:
                    results.append(result)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        return results

    @staticmethod
    def transform_data(
        query: YFinanceKeyMetricsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceKeyMetricsData]:
        """Transform the data."""
        return [YFinanceKeyMetricsData.model_validate(d) for d in data]
