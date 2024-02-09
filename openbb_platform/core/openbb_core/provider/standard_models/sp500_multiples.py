"""SP500 Multiples Standard Model."""

from datetime import date as dateType
from typing import Literal, Optional

from pydantic import Field

from openbb_core.provider.abstract.data import Data
from openbb_core.provider.abstract.query_params import QueryParams
from openbb_core.provider.utils.descriptions import (
    DATA_DESCRIPTIONS,
    QUERY_DESCRIPTIONS,
)

SERIES_DICT = {
    "shiller_pe_month": "Shiller PE Ratio by Month",
    "shiller_pe_year": "Shiller PE Ratio by Year",
    "pe_year": "PE Ratio by Year",
    "pe_month": "PE Ratio by Month",
    "dividend_year": "Dividend by Year",
    "dividend_month": "Dividend by Month",
    "dividend_growth_quarter": "Dividend Growth by Quarter",
    "dividend_growth_year": "Dividend Growth by Year",
    "dividend_yield_year": "Dividend Yield by Year",
    "dividend_yield_month": "Dividend Yield by Month",
    "earnings_year": "Earnings by Year",
    "earnings_month": "Earnings by Month",
    "earnings_growth_year": "Earnings Growth by Year",
    "earnings_growth_quarter": "Earnings Growth by Quarter",
    "real_earnings_growth_year": "Real Earnings Growth by Year",
    "real_earnings_growth_quarter": "Real Earnings Growth by Quarter",
    "earnings_yield_year": "Earnings Yield by Year",
    "earnings_yield_month": "Earnings Yield by Month",
    "real_price_year": "Real Price by Year",
    "real_price_month": "Real Price by Month",
    "inflation_adjusted_price_year": "Inflation Adjusted Price by Year",
    "inflation_adjusted_price_month": "Inflation Adjusted Price by Month",
    "sales_year": "Sales by Year",
    "sales_quarter": "Sales by Quarter",
    "sales_growth_year": "Sales Growth by Year",
    "sales_growth_quarter": "Sales Growth by Quarter",
    "real_sales_year": "Real Sales by Year",
    "real_sales_quarter": "Real Sales by Quarter",
    "real_sales_growth_year": "Real Sales Growth by Year",
    "real_sales_growth_quarter": "Real Sales Growth by Quarter",
    "price_to_sales_year": "Price to Sales Ratio by Year",
    "price_to_sales_quarter": "Price to Sales Ratio by Quarter",
    "price_to_book_value_year": "Price to Book Value Ratio by Year",
    "price_to_book_value_quarter": "Price to Book Value Ratio by Quarter",
    "book_value_year": "Book Value per Share by Year",
    "book_value_quarter": "Book Value per Share by Quarter",
}

SERIES_NAMES = Literal[
    "shiller_pe_month",
    "shiller_pe_year",
    "pe_year",
    "pe_month",
    "dividend_year",
    "dividend_month",
    "dividend_growth_quarter",
    "dividend_growth_year",
    "dividend_yield_year",
    "dividend_yield_month",
    "earnings_year",
    "earnings_month",
    "earnings_growth_year",
    "earnings_growth_quarter",
    "real_earnings_growth_year",
    "real_earnings_growth_quarter",
    "earnings_yield_year",
    "earnings_yield_month",
    "real_price_year",
    "real_price_month",
    "inflation_adjusted_price_year",
    "inflation_adjusted_price_month",
    "sales_year",
    "sales_quarter",
    "sales_growth_year",
    "sales_growth_quarter",
    "real_sales_year",
    "real_sales_quarter",
    "real_sales_growth_year",
    "real_sales_growth_quarter",
    "price_to_sales_year",
    "price_to_sales_quarter",
    "price_to_book_value_year",
    "price_to_book_value_quarter",
    "book_value_year",
    "book_value_quarter",
]


class SP500MultiplesQueryParams(QueryParams):
    """SP500 Multiples Query."""

    series_name: SERIES_NAMES = Field(
        description="The name of the series. Defaults to 'pe_month'.",
        default="pe_month",
    )
    start_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("start_date", ""), default=None
    )
    end_date: Optional[dateType] = Field(
        description=QUERY_DESCRIPTIONS.get("end_date", ""), default=None
    )


class SP500MultiplesData(Data):
    """SP500 Multiples Data."""

    date: dateType = Field(description=DATA_DESCRIPTIONS.get("date", ""))
