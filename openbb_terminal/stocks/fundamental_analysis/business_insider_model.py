"""Business Insider Model"""
__docformat__ = "numpy"

import json
import logging
import re
from typing import Tuple

import pandas as pd
from bs4 import BeautifulSoup
from rapidfuzz import fuzz

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent, request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_management(symbol: str) -> pd.DataFrame:
    """Get company managers from Business Insider

    Parameters
    ----------
    symbol : str
        Stock ticker symbol

    Returns
    -------
    pd.DataFrame
        Dataframe of managers
    """
    url_market_business_insider = (
        f"https://markets.businessinsider.com/stocks/{symbol.lower()}-stock"
    )
    text_soup_market_business_insider = BeautifulSoup(
        request(
            url_market_business_insider, headers={"User-Agent": get_user_agent()}
        ).text,
        "lxml",
    )

    found_h2s = {}

    for next_h2 in text_soup_market_business_insider.findAll(
        "h2", {"class": "header-underline"}
    ):
        next_table = next_h2.find_next_sibling("table", {"class": "table"})

        if next_table:
            found_h2s[next_h2.text] = next_table

    # Business Insider changed management display convention from 'Management' to
    # 'Ticker Management'. These next few lines simply find 'Ticker Management'
    # header key and copy it to a 'Management' key as to not alter the rest of
    # the function
    ticker_management_to_be_deleted = ""
    management_data_available = False
    for key in found_h2s:
        if "Management" in key:
            ticker_management_to_be_deleted = key
            management_data_available = True
    if management_data_available:
        found_h2s["Management"] = found_h2s[ticker_management_to_be_deleted]
        del found_h2s[ticker_management_to_be_deleted]

    if found_h2s.get("Management") is None:
        console.print(
            f"[red]No management information in Business Insider for {symbol}[/red]"
        )
        return pd.DataFrame()

    l_titles = [
        s_title.text.strip()
        for s_title in found_h2s["Management"].findAll(
            "td", {"class": "table__td text-right"}
        )
        if any(c.isalpha() for c in s_title.text.strip())
        and ("USD" not in s_title.text.strip())
    ]

    l_names = [
        s_name.text.strip()
        for s_name in found_h2s["Management"].findAll(
            "td", {"class": "table__td table--allow-wrap"}
        )
    ]

    df_management = pd.DataFrame(
        {"Name": l_names[-len(l_titles) :], "Title": l_titles},  # noqa: E203
        columns=["Name", "Title"],
    )

    df_management["Info"] = "-"
    df_management["Insider Activity"] = "-"
    df_management = df_management.set_index("Name")

    for s_name in df_management.index:
        df_management.loc[s_name][
            "Info"
        ] = f"http://www.google.com/search?q={s_name} {symbol.upper()}".replace(
            " ", "%20"
        )

    s_url_base = "https://markets.businessinsider.com"
    for insider in text_soup_market_business_insider.findAll(
        "a", {"onclick": "silentTrackPI()"}
    ):
        for s_name in df_management.index:
            if fuzz.token_set_ratio(s_name, insider.text.strip()) > 70:  # type: ignore
                df_management.loc[s_name]["Insider Activity"] = (
                    s_url_base + insider.attrs["href"]
                )
    return df_management


@log_start_end(log=logger)
def get_price_target_from_analysts(symbol: str) -> pd.DataFrame:
    """Get analysts' price targets for a given stock. [Source: Business Insider]

    Parameters
    ----------
    symbol : str
        Ticker symbol

    Returns
    -------
    pd.DataFrame
        Analysts data

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> df = openbb.stocks.fa.pt(symbol="AAPL")
    """
    url_market_business_insider = (
        f"https://markets.businessinsider.com/stocks/{symbol.lower()}-stock"
    )
    text_soup_market_business_insider = BeautifulSoup(
        request(
            url_market_business_insider, headers={"User-Agent": get_user_agent()}
        ).text,
        "lxml",
    )

    d_analyst_data = None
    for script in text_soup_market_business_insider.find_all("script"):
        # Get Analyst data
        if "window.analyseChartConfigs.push" in str(script):
            # Extract config data:
            s_analyst_data = str(script).split("config: ", 1)[1].split(",\r\n", 1)[0]
            d_analyst_data = json.loads(s_analyst_data.split(",\n")[0])
            break

    try:
        df_analyst_data = pd.DataFrame.from_dict(d_analyst_data["Markers"])  # type: ignore
    except TypeError:
        return pd.DataFrame()
    df_analyst_data = df_analyst_data[
        ["DateLabel", "Company", "InternalRating", "PriceTarget"]
    ]
    df_analyst_data.columns = ["Date", "Company", "Rating", "Price Target"]
    # df_analyst_data
    df_analyst_data["Rating"].replace(
        {"gut": "BUY", "neutral": "HOLD", "schlecht": "SELL"}, inplace=True
    )
    df_analyst_data["Date"] = pd.to_datetime(df_analyst_data["Date"])
    df_analyst_data = df_analyst_data.set_index("Date")

    return df_analyst_data


@log_start_end(log=logger)
def get_estimates(symbol: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Get analysts' estimates for a given ticker. [Source: Business Insider]

    Parameters
    ----------
    symbol : str
        Ticker to get analysts' estimates

    Returns
    -------
    df_year_estimates : pd.DataFrame
        Year estimates
    df_quarter_earnings : pd.DataFrame
        Quarter earnings estimates
    df_quarter_revenues : pd.DataFrame
        Quarter revenues estimates

    Returns
    -------
    Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        Year estimates, quarter earnings estimates, quarter revenues estimates
    """
    url_market_business_insider = (
        f"https://markets.businessinsider.com/stocks/{symbol.lower()}-stock"
    )
    text_soup_market_business_insider = BeautifulSoup(
        request(
            url_market_business_insider, headers={"User-Agent": get_user_agent()}
        ).text,
        "lxml",
    )

    l_estimates_year_header = list()
    l_estimates_quarter_header = list()
    for estimates_header in text_soup_market_business_insider.findAll(
        "th", {"class": "table__th text-right"}
    ):
        s_estimates_header = estimates_header.text.strip()
        if s_estimates_header.isdigit():
            l_estimates_year_header.append(s_estimates_header)
        elif ("in %" not in s_estimates_header) and ("Job" not in s_estimates_header):
            l_estimates_quarter_header.append(s_estimates_header)

    l_estimates_year_metric = list()
    for estimates_year_metric in text_soup_market_business_insider.findAll(
        "td", {"class": "table__td black"}
    ):
        l_estimates_year_metric.append(estimates_year_metric.text)

    l_estimates_quarter_metric = list()
    for estimates_quarter_metric in text_soup_market_business_insider.findAll(
        "td", {"class": "table__td font-color-dim-gray"}
    ):
        l_estimates_quarter_metric.append(estimates_quarter_metric.text)

    d_metric_year = dict()
    d_metric_quarter_earnings = dict()
    d_metric_quarter_revenues = dict()
    l_metrics = list()
    n_metrics = 0
    b_year = True
    for idx, metric_value in enumerate(
        text_soup_market_business_insider.findAll(
            "td", {"class": "table__td text-right"}
        )
    ):
        if b_year:
            # YEAR metrics
            l_metrics.append(metric_value.text.strip())

            # Check if we have processed all year metrics
            if n_metrics > len(l_estimates_year_metric) - 1:
                b_year = False
                n_metrics = 0
                l_metrics = list()
                idx_y = idx

            # Add value to dictionary
            if (idx + 1) % len(l_estimates_year_header) == 0:
                d_metric_year[l_estimates_year_metric[n_metrics]] = l_metrics
                l_metrics = list()
                n_metrics += 1

        if not b_year:
            # QUARTER metrics
            l_metrics.append(metric_value.text.strip())

            # Check if we have processed all quarter metrics
            if n_metrics > len(l_estimates_quarter_metric) - 1:
                break

            # Add value to dictionary
            if (idx - idx_y + 1) % len(l_estimates_quarter_header) == 0:
                if n_metrics < 4:
                    d_metric_quarter_earnings[
                        l_estimates_quarter_metric[n_metrics]
                    ] = l_metrics
                else:
                    d_metric_quarter_revenues[
                        l_estimates_quarter_metric[n_metrics - 4]
                    ] = l_metrics
                l_metrics = list()
                n_metrics += 1

    df_year_estimates = pd.DataFrame.from_dict(
        d_metric_year, orient="index", columns=l_estimates_year_header
    )
    df_year_estimates.index.name = "YEARLY ESTIMATES"
    df_quarter_earnings = pd.DataFrame.from_dict(
        d_metric_quarter_earnings,
        orient="index",
        columns=l_estimates_quarter_header,
    )
    # df_quarter_earnings.index.name = 'Earnings'
    df_quarter_revenues = pd.DataFrame.from_dict(
        d_metric_quarter_revenues,
        orient="index",
        columns=l_estimates_quarter_header,
    )
    # df_quarter_revenues.index.name = 'Revenues'

    if not df_quarter_earnings.empty:
        l_quarter = list()
        l_date = list()
        for quarter_title in df_quarter_earnings.columns:
            l_quarter.append(re.split("  ending", quarter_title)[0])
            if len(re.split("  ending", quarter_title)) == 2:
                l_date.append(
                    "ending " + re.split("  ending", quarter_title)[1].strip()
                )
            else:
                l_date.append("-")

        df_quarter_earnings.index.name = "QUARTER EARNINGS ESTIMATES"
        df_quarter_earnings.columns = l_quarter
        df_quarter_earnings.loc["Date"] = l_date
        df_quarter_earnings = df_quarter_earnings.reindex(
            ["Date", "No. of Analysts", "Average Estimate", "Year Ago", "Publish Date"]
        )

    if not df_quarter_revenues.empty:
        df_quarter_revenues.index.name = "QUARTER REVENUES ESTIMATES"
        df_quarter_revenues.columns = l_quarter
        df_quarter_revenues.loc["Date"] = l_date
        df_quarter_revenues = df_quarter_revenues.reindex(
            ["Date", "No. of Analysts", "Average Estimate", "Year Ago", "Publish Date"]
        )

    return df_year_estimates, df_quarter_earnings, df_quarter_revenues
