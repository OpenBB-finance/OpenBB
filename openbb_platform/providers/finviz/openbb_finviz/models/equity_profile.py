"""Finviz Equity Profile Model."""

# pylint: disable=unused-argument
import warnings
from typing import Any, Dict, List, Optional

from finvizfinance.quote import finvizfinance
from openbb_core.provider.abstract.fetcher import Fetcher
from openbb_core.provider.standard_models.equity_info import (
    EquityInfoData,
    EquityInfoQueryParams,
)
from pydantic import Field

_warn = warnings.warn


class FinvizEquityProfileQueryParams(EquityInfoQueryParams):
    """
    Finviz Equity Profile Query.

    Source: https://finviz.com/screener.ashx
    """

    __json_schema_extra__ = {"symbol": ["multiple_items_allowed"]}


class FinvizEquityProfileData(EquityInfoData):
    """Finviz Equity Profile Data."""

    __alias_dict__ = {
        "stock_exchange": "exchange",
    }

    index: Optional[str] = Field(
        default=None,
        description="Included in indices - i.e., Dow, Nasdaq, or S&P.",
    )
    optionable: Optional[str] = Field(
        default=None,
        description="Whether options trade against the ticker.",
    )
    shortable: Optional[str] = Field(
        default=None,
        description="If the asset is shortable.",
    )
    shares_outstanding: Optional[str] = Field(
        default=None,
        description="The number of shares outstanding, as an abbreviated string.",
    )
    shares_float: Optional[str] = Field(
        default=None,
        description="The number of shares in the public float, as an abbreviated string.",
    )
    short_interest: Optional[str] = Field(
        default=None,
        description="The last reported number of shares sold short, as an abbreviated string.",
    )
    institutional_ownership: Optional[float] = Field(
        default=None,
        description="The institutional ownership of the stock, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    market_cap: Optional[str] = Field(
        default=None,
        description="The market capitalization of the stock, as an abbreviated string.",
    )
    dividend_yield: Optional[float] = Field(
        default=None,
        description="The dividend yield of the stock, as a normalized percent.",
        json_schema_extra={"unit_measurement": "percent", "frontend_multiply": 100},
    )
    earnings_date: Optional[str] = Field(
        default=None,
        description="The last, or next confirmed, earnings date and announcement time, as a string."
        + " The format is Nov 02 AMC - for after market close.",
    )
    beta: Optional[float] = Field(
        default=None,
        description="The beta of the stock relative to the broad market.",
    )


class FinvizEquityProfileFetcher(
    Fetcher[FinvizEquityProfileQueryParams, List[FinvizEquityProfileData]]
):
    """Finviz Equity Profile Fetcher."""

    @staticmethod
    def transform_query(params: Dict[str, Any]) -> FinvizEquityProfileQueryParams:
        """Transform the query params."""
        return FinvizEquityProfileQueryParams(**params)

    @staticmethod
    def extract_data(
        query: FinvizEquityProfileQueryParams,
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
                description = data.ticker_description()
            except Exception as e:  # pylint: disable=W0718
                _warn(f"Failed to get data for {symbol} -> {e}")
                return result
            div_yield = (
                float(str(fundament.get("Dividend %", None)).replace("%", "")) / 100
                if fundament.get("Dividend %", "-") != "-"
                else None
            )
            inst_own = (
                float(str(fundament.get("Inst Own", None)).replace("%", "")) / 100
                if fundament.get("Inst Own", "-") != "-"
                else None
            )
            result.update(
                {
                    "symbol": symbol,
                    "exchange": (
                        fundament.get("Exchange", None)
                        if fundament.get("Exchange", "-") != "-"
                        else None
                    ),
                    "name": (
                        fundament.get("Company", None)
                        if fundament.get("Company", "-") != "-"
                        else None
                    ),
                    "sector": (
                        fundament.get("Sector", None)
                        if fundament.get("Sector", "-") != "-"
                        else None
                    ),
                    "industry_category": (
                        fundament.get("Industry", None)
                        if fundament.get("Industry", "-") != "-"
                        else None
                    ),
                    "hq_country": (
                        fundament.get("Country", None)
                        if fundament.get("Country", "-") != "-"
                        else None
                    ),
                    "employees": (
                        fundament.get("Employees", None)
                        if fundament.get("Employees", "-") != "-"
                        else None
                    ),
                    "index": (
                        fundament.get("Index", None)
                        if fundament.get("Index", "-") != "-"
                        else None
                    ),
                    "beta": (
                        fundament.get("Beta", None)
                        if fundament.get("Beta", "-") != "-"
                        else None
                    ),
                    "optionable": (
                        fundament.get("Optionable", None)
                        if fundament.get("Optionable", "-") != "-"
                        else None
                    ),
                    "shortable": (
                        fundament.get("Shortable", None)
                        if fundament.get("Shortable", "-") != "-"
                        else None
                    ),
                    "shares_outstanding": (
                        fundament.get("Shs Outstand", None)
                        if fundament.get("Shs Outstand", "-") != "-"
                        else None
                    ),
                    "shares_float": (
                        fundament.get("Shs Float", None)
                        if fundament.get("Shs Float", "-") != "-"
                        else None
                    ),
                    "short_interest": (
                        fundament.get("Short Interest", None)
                        if fundament.get("Short Interest", "-") != "-"
                        else None
                    ),
                    "institutional_ownership": inst_own if inst_own else None,
                    "market_cap": (
                        fundament.get("Market Cap", None)
                        if fundament.get("Market Cap", "-") != "-"
                        else None
                    ),
                    "dividend_yield": div_yield if div_yield else None,
                    "earnings_date": (
                        fundament.get("Earnings", None)
                        if fundament.get("Earnings", "-") != "-"
                        else None
                    ),
                    "long_description": description if description else None,
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
        query: FinvizEquityProfileQueryParams,
        data: List[Dict],
        **kwargs: Any,
    ) -> List[FinvizEquityProfileData]:
        """Transform and validate the raw data."""
        return [FinvizEquityProfileData.model_validate(d) for d in data]
