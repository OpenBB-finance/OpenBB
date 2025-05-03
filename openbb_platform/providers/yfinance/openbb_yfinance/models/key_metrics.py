"""YFinance Key Metrics Model."""

# pylint: disable=unused-argument

from typing import Any, Dict, List, Optional

from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.key_metrics import (
    KeyMetricsData,
    KeyMetricsQueryParams,
)
from pydantic import Field, field_validator


class YFinanceKeyMetricsQueryParams(KeyMetricsQueryParams):
    """YFinance Key Metrics Query."""

    __json_schema_extra__ = {"symbol": {"multiple_items_allowed": True}}


class YFinanceKeyMetricsData(KeyMetricsData):
    """YFinance Key Metrics Data."""

    __alias_dict__ = {
        "market_cap": "marketCap",
        "pe_ratio": "trailingPE",
        "forward_pe": "forwardPE",
        "peg_ratio": "pegRatio",
        "peg_ratio_ttm": "trailingPegRatio",
        "eps_ttm": "trailingEps",
        "eps_forward": "forwardEps",
        "enterprise_to_ebitda": "enterpriseToEbitda",
        "earnings_growth": "earningsGrowth",
        "earnings_growth_quarterly": "earningsQuarterlyGrowth",
        "revenue_per_share": "revenuePerShare",
        "revenue_growth": "revenueGrowth",
        "enterprise_to_revenue": "enterpriseToRevenue",
        "cash_per_share": "totalCashPerShare",
        "quick_ratio": "quickRatio",
        "current_ratio": "currentRatio",
        "debt_to_equity": "debtToEquity",
        "gross_margin": "grossMargins",
        "operating_margin": "operatingMargins",
        "ebitda_margin": "ebitdaMargins",
        "profit_margin": "profitMargins",
        "return_on_assets": "returnOnAssets",
        "return_on_equity": "returnOnEquity",
        "dividend_yield": "dividendYield",
        "dividend_yield_5y_avg": "fiveYearAvgDividendYield",
        "payout_ratio": "payoutRatio",
        "book_value": "bookValue",
        "price_to_book": "priceToBook",
        "enterprise_value": "enterpriseValue",
        "overall_risk": "overallRisk",
        "audit_risk": "auditRisk",
        "board_risk": "boardRisk",
        "compensation_risk": "compensationRisk",
        "shareholder_rights_risk": "shareHolderRightsRisk",
        "price_return_1y": "52WeekChange",
        "currency": "financialCurrency",
    }

    forward_pe: Optional[float] = Field(
        default=None,
        description="Forward price-to-earnings ratio.",
    )
    peg_ratio: Optional[float] = Field(
        default=None,
        description="PEG ratio (5-year expected).",
    )
    peg_ratio_ttm: Optional[float] = Field(
        default=None,
        description="PEG ratio (TTM).",
    )
    eps_ttm: Optional[float] = Field(
        default=None,
        description="Earnings per share (TTM).",
    )
    eps_forward: Optional[float] = Field(
        default=None,
        description="Forward earnings per share.",
    )
    enterprise_to_ebitda: Optional[float] = Field(
        default=None,
        description="Enterprise value to EBITDA ratio.",
    )
    earnings_growth: Optional[float] = Field(
        default=None,
        description="Earnings growth (Year Over Year), as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    earnings_growth_quarterly: Optional[float] = Field(
        default=None,
        description="Quarterly earnings growth (Year Over Year), as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    revenue_per_share: Optional[float] = Field(
        default=None,
        description="Revenue per share (TTM).",
    )
    revenue_growth: Optional[float] = Field(
        default=None,
        description="Revenue growth (Year Over Year), as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    enterprise_to_revenue: Optional[float] = Field(
        default=None,
        description="Enterprise value to revenue ratio.",
    )
    cash_per_share: Optional[float] = Field(
        default=None,
        description="Cash per share.",
    )
    quick_ratio: Optional[float] = Field(
        default=None,
        description="Quick ratio.",
    )
    current_ratio: Optional[float] = Field(
        default=None,
        description="Current ratio.",
    )
    debt_to_equity: Optional[float] = Field(
        default=None,
        description="Debt-to-equity ratio.",
    )
    gross_margin: Optional[float] = Field(
        default=None,
        description="Gross margin, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    operating_margin: Optional[float] = Field(
        default=None,
        description="Operating margin, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    ebitda_margin: Optional[float] = Field(
        default=None,
        description="EBITDA margin, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    profit_margin: Optional[float] = Field(
        default=None,
        description="Profit margin, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_assets: Optional[float] = Field(
        default=None,
        description="Return on assets, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    return_on_equity: Optional[float] = Field(
        default=None,
        description="Return on equity, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    dividend_yield: Optional[float] = Field(
        default=None,
        description="Dividend yield, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    dividend_yield_5y_avg: Optional[float] = Field(
        default=None,
        description="5-year average dividend yield, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    payout_ratio: Optional[float] = Field(
        default=None,
        description="Payout ratio.",
    )
    book_value: Optional[float] = Field(
        default=None,
        description="Book value per share.",
    )
    price_to_book: Optional[float] = Field(
        default=None,
        description="Price-to-book ratio.",
    )
    enterprise_value: Optional[int] = Field(
        default=None,
        description="Enterprise value.",
    )
    overall_risk: Optional[float] = Field(
        default=None,
        description="Overall risk score.",
    )
    audit_risk: Optional[float] = Field(
        default=None,
        description="Audit risk score.",
    )
    board_risk: Optional[float] = Field(
        default=None,
        description="Board risk score.",
    )
    compensation_risk: Optional[float] = Field(
        default=None,
        description="Compensation risk score.",
    )
    shareholder_rights_risk: Optional[float] = Field(
        default=None,
        description="Shareholder rights risk score.",
    )
    beta: Optional[float] = Field(
        default=None,
        description="Beta relative to the broad market (5-year monthly).",
    )
    price_return_1y: Optional[float] = Field(
        default=None,
        description="One-year price return, as a normalized percent.",
        json_schema_extra={"x-unit_measurement": "percent", "x-frontend_multiply": 100},
    )
    currency: Optional[str] = Field(
        default=None,
        description="Currency in which the data is presented.",
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
        # pylint: disable=import-outside-toplevel
        import asyncio  # noqa
        from curl_adapter import CurlCffiAdapter
        from openbb_core.app.model.abstract.error import OpenBBError
        from openbb_core.provider.utils.errors import EmptyDataError
        from openbb_core.provider.utils.helpers import get_requests_session
        from warnings import warn
        from yfinance import Ticker

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
        messages: list = []
        session = get_requests_session()
        session.mount("https://", CurlCffiAdapter())
        session.mount("http://", CurlCffiAdapter())

        async def get_one(symbol):
            """Get the data for one ticker symbol."""
            result: dict = {}
            ticker: dict = {}
            try:
                ticker = Ticker(
                    symbol,
                    session=session,
                ).get_info()
            except Exception as e:
                messages.append(
                    f"Error getting data for {symbol} -> {e.__class__.__name__}: {e}"
                )
            if not ticker:
                messages.append(f"No data found for {symbol}")
            elif ticker:
                for field in fields:
                    if field in ticker:
                        result[field] = ticker.get(field, None)
                if result and result.get("52WeekChange") is not None:
                    results.append(result)

        tasks = [get_one(symbol) for symbol in symbols]

        await asyncio.gather(*tasks)

        if not results and not messages:
            raise EmptyDataError("No data was returned for the given symbol(s).")

        if not results and messages:
            raise OpenBBError("\n".join(messages))

        if results and messages:
            for message in messages:
                warn(message)

        return results

    @staticmethod
    def transform_data(
        query: YFinanceKeyMetricsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[YFinanceKeyMetricsData]:
        """Transform the data."""
        return [YFinanceKeyMetricsData.model_validate(d) for d in data]
