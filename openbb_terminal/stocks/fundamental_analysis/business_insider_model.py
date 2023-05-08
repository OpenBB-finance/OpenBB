"""Business Insider Model"""
__docformat__ = "numpy"

import json
import logging
from typing import Tuple

import pandas as pd
from bs4 import BeautifulSoup

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
    df_management = df_management.set_index("Name")

    for s_name in df_management.index:
        df_management.loc[s_name][
            "Info"
        ] = f"http://www.google.com/search?q={s_name} {symbol.upper()}".replace(
            " ", "%20"
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

    # Get all tables and convert them to list of pandas dataframes
    tables = text_soup_market_business_insider.find_all("table")
    list_df = pd.read_html(str(tables))

    # Get year estimates
    df_year_estimates = list_df[3]
    l_year_estimates_columns = df_year_estimates.columns.tolist()
    l_year_estimates_columns[0] = "YEARLY ESTIMATES"
    df_year_estimates.columns = l_year_estimates_columns
    df_year_estimates.set_index("YEARLY ESTIMATES", inplace=True)

    df_quarter = list_df[4]
    date_row = dict()

    # Get quarter earnings estimates
    df_quarter_earnings = df_quarter.iloc[0:5, :].reset_index(drop=True).copy()
    df_quarter_earnings.drop(index=0, inplace=True)
    l_quarter_earnings_columns = df_quarter_earnings.columns.tolist()
    l_quarter_earnings_columns[0] = "QUARTER EARNINGS ESTIMATES"
    date_row["QUARTER EARNINGS ESTIMATES"] = "Date"

    # Adding Date info to add to dataframe
    for col in l_quarter_earnings_columns[1:]:
        key = col.split("ending")[0].strip()
        value = col[col.find("ending") :].strip()
        date_row[key] = value

    df_quarter_earnings.columns = date_row.keys()
    date_row = pd.DataFrame(date_row, index=[0])
    df_quarter_earnings = pd.concat([date_row, df_quarter_earnings]).reset_index(
        drop=True
    )
    df_quarter_earnings.set_index("QUARTER EARNINGS ESTIMATES", inplace=True)

    # Setting date_row to empty dict object
    date_row = dict()

    # Get quarter revenues estimates
    df_quarter_revenues = df_quarter.iloc[5:, :].reset_index(drop=True).copy()
    df_quarter_revenues.drop(index=0, inplace=True)
    l_quarter_revenues_columns = df_quarter_revenues.columns.tolist()
    l_quarter_revenues_columns[0] = "QUARTER REVENUES ESTIMATES"
    date_row["QUARTER REVENUES ESTIMATES"] = "Date"

    # Adding Date info to add to dataframe
    for col in l_quarter_revenues_columns[1:]:
        key = col.split("ending")[0].strip()
        value = col[col.find("ending") :].strip()
        date_row[key] = value

    df_quarter_revenues.columns = date_row.keys()
    date_row = pd.DataFrame(date_row, index=[0])
    df_quarter_revenues = pd.concat([date_row, df_quarter_revenues]).reset_index(
        drop=True
    )
    df_quarter_revenues.set_index("QUARTER REVENUES ESTIMATES", inplace=True)

    return df_year_estimates, df_quarter_earnings, df_quarter_revenues
