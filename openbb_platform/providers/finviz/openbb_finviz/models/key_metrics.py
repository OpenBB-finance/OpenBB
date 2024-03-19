"""Finviz Key Metrics Model."""

# pylint: disable=unused-argument
import warnings
from typing import Any, Dict, List, Optional

from finvizfinance.quote import finvizfinance
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.key_metrics import (
    KeyMetricsData,
    KeyMetricsQueryParams,
)
from pydantic import Field

_warn = warnings.warn


class FinvizKeyMetricsQueryParams(KeyMetricsQueryParams):
    """
    Finviz Key Metrics Query.

    Source: https://finviz.com/screener.ashx
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class FinvizKeyMetricsData(KeyMetricsData):
    """Finviz Key Metrics Data."""

    foward_pe: Optional[float] = Field(
        default=None, description="Forward price-to-earnings ratio (forward P/E)"
    )
    eps: Optional[float] = Field(default=None, description="Earnings per share (EPS)")
    price_to_sales: Optional[float] = Field(
        default=None, description="Price-to-sales ratio (P/S)"
    )
    price_to_book: Optional[float] = Field(
        default=None, description="Price-to-book ratio (P/B)"
    )
    book_value_per_share: Optional[float] = Field(
        default=None, description="Book value per share (Book/sh)"
    )
    price_to_cash: Optional[float] = Field(
        default=None, description="Price-to-cash ratio (P/C)"
    )
    cash_per_share: Optional[float] = Field(
        default=None, description="Cash per share (Cash/sh)"
    )
    price_to_free_cash_flow: Optional[float] = Field(
        default=None, description="Price-to-free cash flow ratio (P/FCF)"
    )
    debt_to_equity: Optional[float] = Field(
        default=None, description="Debt-to-equity ratio (Debt/Eq)"
    )
    long_term_debt_to_equity: Optional[float] = Field(
        default=None, description="Long-term debt-to-equity ratio (LT Debt/Eq)"
    )
    quick_ratio: Optional[float] = Field(default=None, description="Quick ratio")
    current_ratio: Optional[float] = Field(default=None, description="Current ratio")
    gross_margin: Optional[float] = Field(
        default=None,
        description="Gross margin, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    profit_margin: Optional[float] = Field(
        default=None,
        description="Profit margin, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    operating_margin: Optional[float] = Field(
        default=None,
        description="Operating margin, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_on_assets: Optional[float] = Field(
        default=None,
        description="Return on assets (ROA), as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_on_investment: Optional[float] = Field(
        default=None,
        description="Return on investment (ROI), as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    return_on_equity: Optional[float] = Field(
        default=None,
        description="Return on equity (ROE), as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    payout_ratio: Optional[float] = Field(
        default=None,
        description="Payout ratio, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    dividend_yield: Optional[float] = Field(
        default=None,
        description="Dividend yield, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )


class FinvizKeyMetricsFetcher(
    Fetcher[FinvizKeyMetricsQueryParams, List[FinvizKeyMetricsData]]
):
    """Finviz Key Metrics Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FinvizKeyMetricsQueryParams:
        """Transform the query params."""
        return FinvizKeyMetricsQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FinvizKeyMetricsQueryParams,
        credentials: Optional[Dict[str, str]],
        **kwargs: Any,
    ) -> List[Dict]:
        """Extract the raw data from Finviz."""

        results = []

        def get_one(symbol) -> Dict:
            """Get the data for one symbol."""
            result = {}
            try:
                data = finvizfinance(symbol)
                fundament = data.ticker_fundament()
                mkt_cap = (
                    fundament.get("Market Cap", None)
                    if fundament.get("Market Cap", "-") != "-"
                    else None
                )
                if mkt_cap:
                    mkt_cap = float(
                        str(mkt_cap)
                        .replace("B", "e+9")
                        .replace("M", "e+6")
                        .replace("K", "e+3")
                    )
            except Exception as e:  # pylint: disable=W0718
                _warn(f"Failed to get data for {symbol} -> {e}")
                return result
            result.update(
                {
                    "symbol": symbol,
                    "market_cap": int(mkt_cap) if mkt_cap is not None else None,
                    "pe_ratio": (
                        fundament.get("P/E", None)
                        if fundament.get("P/E", "-") != "-"
                        else None
                    ),
                    "eps": (
                        fundament.get("EPS (ttm)", None)
                        if fundament.get("EPS (ttm)", "-") != "-"
                        else None
                    ),
                    "foward_pe": (
                        fundament.get("Forward P/E", None)
                        if fundament.get("Forward P/E", "-") != "-"
                        else None
                    ),
                    "price_to_sales": (
                        fundament.get("P/S", None)
                        if fundament.get("P/S", "-") != "-"
                        else None
                    ),
                    "price_to_book": (
                        fundament.get("P/B", None)
                        if fundament.get("P/B", "-") != "-"
                        else None
                    ),
                    "book_value_per_share": (
                        fundament.get("Book/sh", None)
                        if fundament.get("Book/sh", "-") != "-"
                        else None
                    ),
                    "price_to_cash": (
                        fundament.get("P/C", None)
                        if fundament.get("P/C", "-") != "-"
                        else None
                    ),
                    "cash_per_share": (
                        fundament.get("Cash/sh", None)
                        if fundament.get("Cash/sh", "-") != "-"
                        else None
                    ),
                    "price_to_free_cash_flow": (
                        fundament.get("P/FCF", None)
                        if fundament.get("P/FCF", "-") != "-"
                        else None
                    ),
                    "debt_to_equity": (
                        fundament.get("Debt/Eq", None)
                        if fundament.get("Debt/Eq", "-") != "-"
                        else None
                    ),
                    "long_term_debt_to_equity": (
                        fundament.get("LT Debt/Eq", None)
                        if fundament.get("LT Debt/Eq", "-") != "-"
                        else None
                    ),
                    "quick_ratio": (
                        fundament.get("Quick Ratio", None)
                        if fundament.get("Quick Ratio", "-") != "-"
                        else None
                    ),
                    "current_ratio": (
                        fundament.get("Current Ratio", None)
                        if fundament.get("Current Ratio", "-") != "-"
                        else None
                    ),
                    "gross_margin": (
                        float(str(fundament.get("Gross Margin", None)).replace("%", ""))
                        / 100
                        if fundament.get("Gross Margin", "-") != "-"
                        else None
                    ),
                    "profit_margin": (
                        float(
                            str(fundament.get("Profit Margin", None)).replace("%", "")
                        )
                        / 100
                        if fundament.get("Profit Margin", "-") != "-"
                        else None
                    ),
                    "operating_margin": (
                        float(str(fundament.get("Oper. Margin", None)).replace("%", ""))
                        / 100
                        if fundament.get("Oper. Margin", "-") != "-"
                        else None
                    ),
                    "return_on_assets": (
                        float(str(fundament.get("ROA", None)).replace("%", "")) / 100
                        if fundament.get("ROA", "-") != "-"
                        else None
                    ),
                    "return_on_investment": (
                        float(str(fundament.get("ROI", None)).replace("%", "")) / 100
                        if fundament.get("ROI", "-") != "-"
                        else None
                    ),
                    "return_on_equity": (
                        float(str(fundament.get("ROE", None)).replace("%", "")) / 100
                        if fundament.get("ROE", "-") != "-"
                        else None
                    ),
                    "payout_ratio": (
                        float(str(fundament.get("Payout", None)).replace("%", "")) / 100
                        if fundament.get("Payout", "-") != "-"
                        else None
                    ),
                    "dividend_yield": (
                        float(str(fundament.get("Dividend %", None)).replace("%", ""))
                        / 100
                        if fundament.get("Dividend %", "-") != "-"
                        else None
                    ),
                }
            )

            return result

        symbols = query.symbol.split(",")
        for symbol in symbols:
            result = get_one(symbol)
            if result is not None and result:
                results.append(result)

        return results

    @staticmethod
    def transform_data(
        query: FinvizKeyMetricsQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FinvizKeyMetricsData]:
        """Transform and validate the raw data."""
        return [FinvizKeyMetricsData.model_validate(d) for d in data]
