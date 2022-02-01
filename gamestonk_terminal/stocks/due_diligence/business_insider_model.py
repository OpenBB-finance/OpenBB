""" Business Insider Model """
__docformat__ = "numpy"

import json
import logging
import re
from typing import Tuple

import pandas as pd
import requests
from bs4 import BeautifulSoup

from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import get_user_agent

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def get_price_target_from_analysts(ticker: str) -> pd.DataFrame:
    """Get analysts' price targets for a given stock. [Source: Business Insider]

    Parameters
    ----------
    ticker : str
        Ticker symbol

    Returns
    -------
    pd.DataFrame
        Analysts data
    """
    url_market_business_insider = (
        f"https://markets.businessinsider.com/stocks/{ticker.lower()}-stock"
    )
    text_soup_market_business_insider = BeautifulSoup(
        requests.get(
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

    df_analyst_data = pd.DataFrame.from_dict(d_analyst_data["Markers"])  # type: ignore
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
def get_estimates(ticker: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Get analysts' estimates for a given ticker. [Source: Business Insider]

    Parameters
    ----------
    ticker : str
        Ticker to get analysts' estimates

    Returns
    -------
    df_year_estimates : pd.DataFrame
        Year estimates
    df_quarter_earnings : pd.DataFrame
        Quarter earnings estimates
    df_quarter_revenues : pd.DataFrame
        Quarter revenues estimates
    """
    url_market_business_insider = (
        f"https://markets.businessinsider.com/stocks/{ticker.lower()}-stock"
    )
    text_soup_market_business_insider = BeautifulSoup(
        requests.get(
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

    l_quarter = list()
    l_date = list()
    for quarter_title in df_quarter_earnings.columns:
        l_quarter.append(re.split("  ending", quarter_title)[0])
        if len(re.split("  ending", quarter_title)) == 2:
            l_date.append("ending " + re.split("  ending", quarter_title)[1].strip())
        else:
            l_date.append("-")

    df_quarter_earnings.index.name = "QUARTER EARNINGS ESTIMATES"
    df_quarter_earnings.columns = l_quarter
    df_quarter_earnings.loc["Date"] = l_date
    df_quarter_earnings = df_quarter_earnings.reindex(
        ["Date", "No. of Analysts", "Average Estimate", "Year Ago", "Publish Date"]
    )

    df_quarter_revenues.index.name = "QUARTER REVENUES ESTIMATES"
    df_quarter_revenues.columns = l_quarter
    df_quarter_revenues.loc["Date"] = l_date
    df_quarter_revenues = df_quarter_revenues.reindex(
        ["Date", "No. of Analysts", "Average Estimate", "Year Ago", "Publish Date"]
    )

    return df_year_estimates, df_quarter_earnings, df_quarter_revenues
