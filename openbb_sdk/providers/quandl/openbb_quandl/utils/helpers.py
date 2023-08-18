"""Quandl Helpers Module"""

from typing import Literal, Optional

import pandas as pd
import quandl

from .series_ids import SP500MULTIPLES


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
    api_key : Optional[str]
        Quandl API key.

    Returns
    -------
    pd.DataFrame
        Pandas DataFrame with the results.
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
