"""Portfolio Helper"""
__docformat__ = "numpy"

import csv
import logging
import os
from datetime import date, datetime
from pathlib import Path
from typing import List

import pandas as pd
import yfinance as yf
from dateutil.relativedelta import relativedelta

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.portfolio.statics import REGIONS
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


# pylint: disable=too-many-return-statements, too-many-lines, too-many-statements, consider-iterating-dictionary
# pylint: disable=C0302


now = datetime.now()
PERIODS_DAYS = {
    "mtd": (now - datetime(now.year, now.month, 1)).days,
    "qtd": (
        now
        - datetime(
            now.year,
            1 if now.month < 4 else 4 if now.month < 7 else 7 if now.month < 10 else 10,
            1,
        )
    ).days,
    "ytd": (now - datetime(now.year, 1, 1)).days,
    "all": 1,
    "3m": 3 * 21,
    "6m": 6 * 21,
    "1y": 12 * 21,
    "3y": 3 * 12 * 21,
    "5y": 5 * 12 * 21,
    "10y": 10 * 12 * 21,
}

DEFAULT_HOLDINGS_PATH = (
    get_current_user().preferences.USER_PORTFOLIO_DATA_DIRECTORY / "holdings"
)


def is_ticker(ticker: str) -> bool:
    """Determine whether a string is a valid ticker

    Parameters
    ----------
    ticker : str
        The string to be tested

    Returns
    -------
    bool
        Whether the string is a ticker
    """
    item = yf.Ticker(ticker)
    return "previousClose" in item.fast_info


# TODO: Is this being used anywhere?
def beta_word(beta: float) -> str:
    """Describe a beta

    Parameters
    ----------
    beta : float
        The beta for a portfolio

    Returns
    -------
    str
        The description of the beta
    """
    if abs(1 - beta) > 3:
        part = "extremely "
    elif abs(1 - beta) > 2:
        part = "very "
    elif abs(1 - beta) > 1:
        part = ""
    else:
        part = "moderately "

    return part + "high" if beta > 1 else "low"


def clean_name(name: str) -> str:
    """Clean a name to a ticker

    Parameters
    ----------
    name : str
        The value to be cleaned

    Returns
    -------
    str
        A cleaned value
    """
    return name.replace("beta_", "").upper()


def filter_df_by_period(df: pd.DataFrame, period: str = "all") -> pd.DataFrame:
    """Filter dataframe by selected period

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe to be filtered in terms of time
    period : str
        Period in which to filter dataframe.
        Possible choices are: mtd, qtd, ytd, 3m, 6m, 1y, 3y, 5y, 10y, all

    Returns
    -------
    pd.DataFrame
        A cleaned value
    """
    if period == "mtd":
        return df[df.index.strftime("%Y-%m") == datetime.now().strftime("%Y-%m")]
    if period == "qtd":
        if datetime.now().month < 4:
            return df[
                df.index.strftime("%Y-%m") < f"{datetime.now().strftime('%Y')}-04"
            ]
        if datetime.now().month < 7:
            return df[
                (df.index.strftime("%Y-%m") >= f"{datetime.now().strftime('%Y')}-04")
                & (df.index.strftime("%Y-%m") < f"{datetime.now().strftime('%Y')}-07")
            ]
        if datetime.now().month < 10:
            return df[
                (df.index.strftime("%Y-%m") >= f"{datetime.now().strftime('%Y')}-07")
                & (df.index.strftime("%Y-%m") < f"{datetime.now().strftime('%Y')}-10")
            ]
        return df[df.index.strftime("%Y-%m") >= f"{datetime.now().strftime('%Y')}-10"]
    if period == "ytd":
        return df[df.index.strftime("%Y") == datetime.now().strftime("%Y")]
    if period == "3m":
        return df[df.index >= (datetime.now() - relativedelta(months=3))]
    if period == "6m":
        return df[df.index >= (datetime.now() - relativedelta(months=6))]
    if period == "1y":
        return df[df.index >= (datetime.now() - relativedelta(years=1))]
    if period == "3y":
        return df[df.index >= (datetime.now() - relativedelta(years=3))]
    if period == "5y":
        return df[df.index >= (datetime.now() - relativedelta(years=5))]
    if period == "10y":
        return df[df.index >= (datetime.now() - relativedelta(years=10))]
    return df


def make_equal_length(df1: pd.DataFrame, df2: pd.DataFrame):
    """Filter dataframe by selected period

    Parameters
    ----------
    df1: pd.DataFrame
        The first DataFrame that needs to be compared.
    df2: pd.DataFrame
        The second DataFrame that needs to be compared.

    Returns
    -------
    df1 and df2
         Both DataFrames returned
    """
    # Match the DataFrames so they share a similar length
    if isinstance(df1, pd.Series):
        df1 = df1.to_frame()
    if isinstance(df2, pd.Series):
        df2 = df2.to_frame()
    df2.columns = [str(i) + "2" for i in df2.columns]
    df_merged = df1.join(df2, how="outer")
    df_merged = df_merged.fillna(0)

    df1 = df_merged[df1.columns]
    df2 = df_merged[df2.columns]

    df2.columns = [i[:-1] for i in df2.columns]

    return df1.iloc[:, 0], df2.iloc[:, 0]


def get_region_from_country(country: str) -> str:
    """Get region from country

    Parameters
    ----------
    country: str
        The country to assign region.

    Returns
    -------
    str
        Region to which country belongs.
    """
    return REGIONS[country]


def get_info_update_file(ticker: str, file_path: Path, writemode: str) -> List[str]:
    """Get info (Sector, Industry, Country and Region) from ticker and save information in file to access later.

    Parameters
    ----------
    ticker: str
        The ticker to get information.
    file_path: str
        The file to save information.
    writemode: str
        The mode to write into the file, 'w' or 'a'.

    Returns
    -------
    List[str]
        List with ticker information.
    """

    # Pull ticker info from yf
    yf_ticker_info = yf.Ticker(ticker).info

    if "sector" in yf_ticker_info:
        # Ticker has valid sector
        # Replace the dash to UTF-8 readable
        ticker_info_list = [
            yf_ticker_info["sector"],
            yf_ticker_info["industry"].replace("—", "-"),
            yf_ticker_info["country"],
            get_region_from_country(yf_ticker_info["country"]),
        ]

        with open(file_path, writemode, newline="") as f:
            writer = csv.writer(f)

            if writemode == "a":
                # file already has data, so just append
                writer.writerow([ticker] + ticker_info_list)
            else:
                # file did not exist or as empty, so write headers first
                writer.writerow(["Ticker", "Sector", "Industry", "Country", "Region"])
                writer.writerow([ticker] + ticker_info_list)
            f.close()
        return ticker_info_list
    # Ticker does not have a valid sector
    console.print(f"F:{ticker}", end="")
    return ["", "", "", ""]


def get_info_from_ticker(ticker: str) -> list:
    """Get info (Sector, Industry, Country and Region) from ticker.

    Parameters
    ----------
    ticker: str
        The ticker to get information.

    Returns
    -------
    List[str]
        List with ticker information.
    """

    filename = "tickers_info.csv"

    file_path = Path(
        str(get_current_user().preferences.USER_PORTFOLIO_DATA_DIRECTORY), filename
    )

    if file_path.is_file() and os.stat(file_path).st_size > 0:
        # file exists and is not empty, so append if necessary
        ticker_info_df = pd.read_csv(file_path)
        df_row = ticker_info_df.loc[ticker_info_df["Ticker"] == ticker]

        if len(df_row) > 0:
            # ticker is in file, just return it
            ticker_info_list = list(df_row.iloc[0].drop("Ticker"))
            return ticker_info_list
        # ticker is not in file, go get it
        ticker_info_list = get_info_update_file(ticker, file_path, "a")
        return ticker_info_list
    # file does not exist or is empty, so write it
    ticker_info_list = get_info_update_file(ticker, file_path, "w")

    return ticker_info_list


def get_start_date_from_period(period: str) -> date:
    """Get start date of a time period based on the period string.

    Parameters
    ----------
    period: str
        Period to get start date from (e.g. 10y, 3m, etc.)

    Returns
    -------
    date
        Start date of the period.
    """
    if period == "10y":
        start_date = date.today() + relativedelta(years=-10)
    elif period == "5y":
        start_date = date.today() + relativedelta(years=-5)
    elif period == "3y":
        start_date = date.today() + relativedelta(years=-3)
    elif period == "1y":
        start_date = date.today() + relativedelta(years=-1)
    elif period == "6m":
        start_date = date.today() + relativedelta(months=-6)
    elif period == "3m":
        start_date = date.today() + relativedelta(months=-3)
    elif period == "ytd":
        start_date = date(date.today().year, 1, 1)
    elif period == "qtd":
        cm = date.today().month
        if 3 >= cm >= 1:
            start_date = date(date.today().year, 1, 1)
        elif 6 >= cm >= 4:
            start_date = date(date.today().year, 4, 1)
        elif 9 >= cm >= 7:
            start_date = date(date.today().year, 7, 1)
        elif 12 >= cm >= 10:
            start_date = date(date.today().year, 10, 1)
        else:
            print("Error")
    elif period == "mtd":
        cur_month = date.today().month
        cur_year = date.today().year
        start_date = date(cur_year, cur_month, 1)

    return start_date
