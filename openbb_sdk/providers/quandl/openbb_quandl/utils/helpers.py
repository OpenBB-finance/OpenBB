"""Quandl Helpers Module"""

from typing import Literal, Optional

import pandas as pd
import quandl

SP500MULTIPLES = {
    "Shiller PE Ratio by Month": "MULTPL/SHILLER_PE_RATIO_MONTH",
    "Shiller PE Ratio by Year": "MULTPL/SHILLER_PE_RATIO_YEAR",
    "PE Ratio by Year": "MULTPL/SP500_PE_RATIO_YEAR",
    "PE Ratio by Month": "MULTPL/SP500_PE_RATIO_MONTH",
    "Dividend by Year": "MULTPL/SP500_DIV_YEAR",
    "Dividend by Month": "MULTPL/SP500_DIV_MONTH",
    "Dividend Growth by Quarter": "MULTPL/SP500_DIV_GROWTH_QUARTER",
    "Dividend Growth by Year": "MULTPL/SP500_DIV_GROWTH_YEAR",
    "Dividend Yield by Year": "MULTPL/SP500_DIV_YIELD_YEAR",
    "Dividend Yield by Month": "MULTPL/SP500_DIV_YIELD_MONTH",
    "Earnings by Year": "MULTPL/SP500_EARNINGS_YEAR",
    "Earnings by Month": "MULTPL/SP500_EARNINGS_MONTH",
    "Earnings Growth by Year": "MULTPL/SP500_EARNINGS_GROWTH_YEAR",
    "Earnings Growth by Quarter": "MULTPL/SP500_EARNINGS_GROWTH_QUARTER",
    "Real Earnings Growth by Year": "MULTPL/SP500_REAL_EARNINGS_GROWTH_YEAR",
    "Real Earnings Growth by Quarter": "MULTPL/SP500_REAL_EARNINGS_GROWTH_QUARTER",
    "Earnings Yield by Year": "MULTPL/SP500_EARNINGS_YIELD_YEAR",
    "Earnings Yield by Month": "MULTPL/SP500_EARNINGS_YIELD_MONTH",
    "Real Price by Year": "MULTPL/SP500_REAL_PRICE_YEAR",
    "Real Price by Month": "MULTPL/SP500_REAL_PRICE_MONTH",
    "Inflation Adjusted Price by Year": "MULTPL/SP500_INFLADJ_YEAR",
    "Inflation Adjusted Price by Month": "MULTPL/SP500_INFLADJ_MONTH",
    "Sales by Year": "MULTPL/SP500_SALES_YEAR",
    "Sales by Quarter": "MULTPL/SP500_SALES_QUARTER",
    "Sales Growth by Year": "MULTPL/SP500_SALES_GROWTH_YEAR",
    "Sales Growth by Quarter": "MULTPL/SP500_SALES_GROWTH_Quarter",
    "Real Sales by Year": "MULTPL/SP500_REAL_SALES_YEAR",
    "Real Sales by Quarter": "MULTPL/SP500_REAL_SALES_QUARTER",
    "Real Sales Growth by Year": "MULTPL/SP500_REAL_SALES_GROWTH_YEAR",
    "Real Sales Growth by Quarter": "MULTPL/SP500_REAL_SALES_GROWTH_QUARTER",
    "Price to Sales Ratio by Year": "MULTPL/SP500_PSR_YEAR",
    "Price to Sales Ratio by Quarter": "MULTPL/SP500_PSR_QUARTER",
    "Price to Book Value Ratio by Year": "MULTPL/SP500_PBV_RATIO_YEAR",
    "Price to Book Value Ratio by Quarter": "MULTPL/SP500_PBV_RATIO_QUARTER",
    "Book Value per Share by Year": "MULTPL/SP500_BVPS_YEAR",
    "Book Value per Share by Quarter": "MULTPL/SP500_BVPS_QUARTER",
}


def get_sp500_multiples(
    series_name: str = "PE Ratio by Month",
    start_date: Optional[str] = "",
    end_date: Optional[str] = "",
    collapse: Optional[
        Literal["daily", "weekly", "monthly", "quarterly", "annual"]
    ] = "monthly",
    transform: Optional[Literal["diff", "rdiff", "cumul", "normalize"]] = None,
    api_key: Optional[str] = "",
    **kwargs
) -> pd.DataFrame:
    """Gets historical S&P 500 levels, ratios, and multiples.

    Parameters
    ----------
    series_name : str
        Name of the series. Defaults to "PE Ratio by Month".
    start_date : Optional[dateType]
        The start date of the time series. Defaults to all.
    end_date : Optional[dateType]
        The end date of the time series. Defaults to the most recent data.
    collapse : Optional[Literal["daily", "weekly", "monthly", "quarterly", "annual"]]
        The frequency of the time series. Defaults to "monthly".
    transform : Optional[Literal["diff", "rdiff", "cumul", "normalize"]]
    """

    if series_name not in SP500MULTIPLES:
        print("Invalid series name, choose from: ", list(SP500MULTIPLES.keys()))
        return pd.DataFrame()
    if "Year" in series_name:
        collapse = "annual"
    if "Quarter" in series_name:
        collapse = "quarterly"

    data = (
        quandl.get(
            SP500MULTIPLES[series_name],
            start_date=start_date,
            end_date=end_date,
            collapse=collapse,
            transform=transform,
            api_key=api_key,
            **kwargs
        )
        .reset_index()
        .rename(columns={"Date": "date", "Value": "value"})
    )

    data["date"] = data["date"].dt.strftime("%Y-%m-%d")

    return data
