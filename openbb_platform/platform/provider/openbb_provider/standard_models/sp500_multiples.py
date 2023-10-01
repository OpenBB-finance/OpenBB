"""SP500 Multiples  data model."""

from typing import Literal, Optional

from pydantic import Field

from openbb_provider.abstract.data import Data
from openbb_provider.abstract.query_params import QueryParams


class SP500MultiplesQueryParams(QueryParams):
    """Gets historical S&P 500 levels, ratios, and multiples."""

    series_name: Literal[
        "Shiller PE Ratio by Month",
        "Shiller PE Ratio by Year",
        "PE Ratio by Year",
        "PE Ratio by Month",
        "Dividend by Year",
        "Dividend by Month",
        "Dividend Growth by Quarter",
        "Dividend Growth by Year",
        "Dividend Yield by Year",
        "Dividend Yield by Month",
        "Earnings by Year",
        "Earnings by Month",
        "Earnings Growth by Year",
        "Earnings Growth by Quarter",
        "Real Earnings Growth by Year",
        "Real Earnings Growth by Quarter",
        "Earnings Yield by Year",
        "Earnings Yield by Month",
        "Real Price by Year",
        "Real Price by Month",
        "Inflation Adjusted Price by Year",
        "Inflation Adjusted Price by Month",
        "Sales by Year",
        "Sales by Quarter",
        "Sales Growth by Year",
        "Sales Growth by Quarter",
        "Real Sales by Year",
        "Real Sales by Quarter",
        "Real Sales Growth by Year",
        "Real Sales Growth by Quarter",
        "Price to Sales Ratio by Year",
        "Price to Sales Ratio by Quarter",
        "Price to Book Value Ratio by Year",
        "Price to Book Value Ratio by Quarter",
        "Book Value per Share by Year",
        "Book Value per Share by Quarter",
    ] = Field(
        description="The name of the series. Defaults to 'PE Ratio by Month'.",
        default="PE Ratio by Month",
    )
    start_date: Optional[str] = Field(
        description="The start date of the time series. Format: YYYY-MM-DD", default=""
    )
    end_date: Optional[str] = Field(
        description="The end date of the time series. Format: YYYY-MM-DD", default=""
    )
    collapse: Optional[
        Literal["daily", "weekly", "monthly", "quarterly", "annual"]
    ] = Field(
        description="Collapse the frequency of the time series.",
        default="monthly",
    )
    transform: Optional[Literal["diff", "rdiff", "cumul", "normalize"]] = Field(
        description="The transformation of the time series.",
        default=None,
    )


class SP500MultiplesData(Data):
    """SP500 Multiples Data."""

    date: str = Field(description="The date data for the time series.")
    value: float = Field(description="The data value for the time series.")
