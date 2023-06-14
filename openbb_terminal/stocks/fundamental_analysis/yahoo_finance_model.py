"""Yahoo Finance Model"""
__docformat__ = "numpy"

import logging
import ssl
from datetime import datetime
from typing import Optional, Tuple
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import lambda_long_number_format
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis.fa_helper import clean_df_index

logger = logging.getLogger(__name__)
# pylint: disable=W0212
ssl._create_default_https_context = ssl._create_unverified_context


@log_start_end(log=logger)
def get_info(symbol: str) -> pd.DataFrame:
    """Gets ticker symbol info

    Parameters
    ----------
    symbol: str
        Stock ticker symbol

    Returns
    -------
    pd.DataFrame
        DataFrame of yfinance information
    """
    stock = yf.Ticker(symbol)
    df_info = pd.DataFrame(stock.fast_info.items(), columns=["Metric", "Value"])
    df_info = df_info.set_index("Metric")

    clean_df_index(df_info)

    if "Last split date" in df_info.index and df_info.loc["Last split date"].values[0]:
        df_info.loc["Last split date"].values[0] = datetime.fromtimestamp(
            df_info.loc["Last split date"].values[0]
        ).strftime("%Y-%m-%d")

    df_info = df_info.mask(df_info["Value"].astype(str).eq("[]")).dropna()
    df_info[df_info.index != "Zip"] = df_info[df_info.index != "Zip"].applymap(
        lambda x: lambda_long_number_format(x)
    )

    df_info = df_info.rename(
        index={
            "Address1": "Address",
            "Average daily volume10 day": "Average daily volume 10 day",
            "Average volume10days": "Average volume 10 days",
            "Price to sales trailing12 months": "Price to sales trailing 12 months",
        }
    )
    df_info.index = df_info.index.str.replace("eps", "EPS")
    df_info.index = df_info.index.str.replace("p e", "PE")
    df_info.index = df_info.index.str.replace("Peg", "PEG")
    return df_info


@log_start_end(log=logger)
def get_shareholders(symbol: str, holder: str = "institutional") -> pd.DataFrame:
    """Get shareholders from yahoo

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    holder : str
        Which holder to get table for

    Returns
    -------
    pd.DataFrame
        Major holders
    """
    stock = yf.Ticker(symbol)

    # Major holders
    df_major_holders = stock.major_holders
    df_major_holders[1] = df_major_holders[1].apply(
        lambda x: x.replace("%", "Percentage")
    )

    # Institutional holders
    df_institutional_shareholders = stock.institutional_holders
    df_institutional_shareholders.columns = (
        df_institutional_shareholders.columns.str.replace("% Out", "Stake")
    )
    df_institutional_shareholders["Shares"] = df_institutional_shareholders[
        "Shares"
    ].apply(lambda x: lambda_long_number_format(x))
    df_institutional_shareholders["Value"] = df_institutional_shareholders[
        "Value"
    ].apply(lambda x: lambda_long_number_format(x))
    df_institutional_shareholders["Stake"] = df_institutional_shareholders[
        "Stake"
    ].apply(lambda x: str(f"{100 * x:.2f}") + " %")

    # Mutualfunds holders
    df_mutualfund_shareholders = stock.mutualfund_holders
    df_mutualfund_shareholders.columns = df_mutualfund_shareholders.columns.str.replace(
        "% Out", "Stake"
    )
    df_mutualfund_shareholders["Shares"] = df_mutualfund_shareholders["Shares"].apply(
        lambda x: lambda_long_number_format(x)
    )
    df_mutualfund_shareholders["Value"] = df_mutualfund_shareholders["Value"].apply(
        lambda x: lambda_long_number_format(x)
    )
    df_mutualfund_shareholders["Stake"] = df_mutualfund_shareholders["Stake"].apply(
        lambda x: str(f"{100 * x:.2f}") + " %"
    )

    if holder == "major":
        return df_major_holders
    if holder == "institutional":
        return df_institutional_shareholders
    if holder == "mutualfund":
        return df_mutualfund_shareholders
    return pd.DataFrame()


@log_start_end(log=logger)
def get_calendar_earnings(symbol: str) -> pd.DataFrame:
    """Get calendar earnings for ticker symbol

    Parameters
    ----------
    symbol: str
        Stock ticker symbol

    Returns
    -------
    pd.DataFrame
        Dataframe of calendar earnings
    """
    stock = yf.Ticker(symbol)
    df_calendar = stock.calendar

    if df_calendar.empty:
        return pd.DataFrame()

    df_calendar.iloc[0, :] = df_calendar.iloc[0, :].apply(
        lambda x: x.date().strftime("%m/%d/%Y")
    )

    df_calendar.iloc[1:, :] = df_calendar.iloc[1:, :].applymap(
        lambda x: lambda_long_number_format(x)
    )

    return df_calendar.T


@log_start_end(log=logger)
def get_dividends(symbol: str) -> pd.DataFrame:
    """Get historical dividend for ticker

    Parameters
    ----------
    symbol: str
        Ticker symbol to get dividend for

    Returns
    -------
    pd.DataFrame
        Dataframe of dividends and dates

    Examples
    --------
    >>> from openbb_terminal.sdk import openbb
    >>> openbb.fa.divs("AAPL")
    """
    df = pd.DataFrame(yf.Ticker(symbol).dividends)

    if df.empty:
        console.print("No dividends found.\n")
        return pd.DataFrame()

    df["Change"] = df.diff()
    df = df[::-1]

    return df


@log_start_end(log=logger)
def get_mktcap(
    symbol: str,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
) -> Tuple[pd.DataFrame, str]:
    """Get market cap over time for ticker. [Source: Yahoo Finance]

    Parameters
    ----------
    symbol: str
        Ticker to get market cap over time
    start_date: Optional[str]
        Initial date (e.g., 2021-10-01). Defaults to 3 years back

    Returns
    -------
    pd.DataFrame
        Dataframe of estimated market cap over time
    str:
        Currency of ticker
    """
    if start_date is None:
        # Set data far in the past to ensure all data is returned
        start_date = "1900-01-01"
    if end_date is None:
        end_date = datetime.now()  # type: ignore

    currency = ""
    df_data = yf.download(
        symbol,
        start=start_date,
        end=end_date,
        progress=False,
        threads=False,
        ignore_tz=True,
    )
    if not df_data.empty:
        data = yf.Ticker(symbol).fast_info
        if data:
            df_data["Adj Close"] = df_data["Adj Close"] * data["shares"]
            df_data = df_data["Adj Close"]

            currency = data["currency"] if data["currency"] else ""

    return df_data, currency


@log_start_end(log=logger)
def get_splits(symbol: str) -> pd.DataFrame:
    """Get splits and reverse splits events. [Source: Yahoo Finance]

    Parameters
    ----------
    symbol: str
        Ticker to get forward and reverse splits

    Returns
    -------
    pd.DataFrame
        Dataframe of forward and reverse splits
    """
    data = yf.Ticker(symbol).splits
    if not data.empty:
        return data.to_frame()
    return pd.DataFrame()


@log_start_end(log=logger)
def get_financials(symbol: str, statement: str, ratios: bool = False) -> pd.DataFrame:
    """Get cashflow statement for company

    Parameters
    ----------
    symbol : str
        Stock ticker symbol
    statement: str
        can be:

        - cash-flow
        - financials for Income
        - balance-sheet

    ratios: bool
        Shows percentage change

    Returns
    -------
    pd.DataFrame
        Dataframe of Financial statement
    """
    url = (
        "https://uk.finance.yahoo.com/quote/"
        + symbol
        + "/"
        + statement
        + "?p="
        + symbol
    )

    # Making the website believe that you are accessing it using a Mozilla browser
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})

    webpage = urlopen(req).read()  # pylint: disable= R1732
    soup = BeautifulSoup(webpage, "html.parser")

    features = soup.find_all("div", class_="D(tbr)")
    headers = []
    temp_list = []
    final = []
    if len(features) == 0:
        return console.print("No data found in Yahoo Finance\n")

    index = 0  # create headers
    for item in features[0].find_all("div", class_="D(ib)"):
        headers.append(item.text)  # statement contents
    while index <= len(features) - 1:
        # filter for each line of the statement
        temp = features[index].find_all("div", class_="D(tbc)")
        for line in temp:
            # each item adding to a temporary list
            temp_list.append(line.text)
        # temp_list added to final list
        final.append(temp_list)
        # clear temp_list
        temp_list = []
        index += 1

    df = pd.DataFrame(final[1:])
    if df.empty:
        return pd.DataFrame()
    new_headers = []

    if statement == "balance-sheet":
        for dates in headers[1:]:
            read = datetime.strptime(dates, "%d/%m/%Y")
            write = read.strftime("%Y-%m-%d")
            new_headers.append(write)
        new_headers[:0] = ["Breakdown"]
        df.columns = new_headers
        df.set_index("Breakdown", inplace=True)
    elif statement == "financials":
        for dates in headers[2:]:
            read = datetime.strptime(dates, "%d/%m/%Y")
            write = read.strftime("%Y-%m-%d")
            new_headers.append(write)
        new_headers[:0] = ["Breakdown", "ttm"]
        df.columns = new_headers
        df.set_index("Breakdown", inplace=True)
    elif statement == "cash-flow":
        for dates in headers[2:]:
            read = datetime.strptime(dates, "%d/%m/%Y")
            write = read.strftime("%Y-%m-%d")
            new_headers.append(write)
        new_headers[:0] = ["Breakdown", "ttm"]
        df.columns = new_headers
        df.set_index("Breakdown", inplace=True)

    df.replace("", np.nan, inplace=True)
    df.replace("-", np.nan, inplace=True)
    df = df.dropna(how="all")
    df = df.replace(",", "", regex=True)
    df = df.replace("k", "", regex=True)
    df = df.astype("float")
    df.index = df.index.str.replace(",", "")

    not_skipped = ~df.reset_index()["Breakdown"].str.contains("EPS", case=False)
    skipped = df.reset_index()["Breakdown"].str.contains("EPS", case=False)
    skipped_df = df.reset_index()[skipped].set_index("Breakdown")
    transformed = df.reset_index()[not_skipped].set_index("Breakdown") * 1000
    df = pd.concat([transformed, skipped_df])

    if ratios:
        types = df.copy().applymap(lambda x: isinstance(x, (float, int)))
        types = types.all(axis=1)

        # For rows with complete data
        valid = []
        i = 0
        for row in types:
            if row:
                valid.append(i)
            i += 1
        df_fa_pc = df.iloc[valid].pct_change(axis="columns", periods=-1).fillna(0)
        j = 0
        for i in valid:
            df.iloc[i] = df_fa_pc.iloc[j]
            j += 1

    return df


@log_start_end(log=logger)
def get_earnings_history(symbol: str) -> pd.DataFrame:
    """Get earning reports

    Parameters
    ----------
    symbol: str
        Symbol to get earnings for

    Returns
    -------
    pd.DataFrame
        Dataframe of historical earnings if present
    """
    df = yf.Ticker(symbol).earnings_dates
    df.reset_index(inplace=True)
    df["Earnings Date"] = df["Earnings Date"].dt.strftime("%Y-%m-%d")
    df.drop_duplicates(inplace=True)
    df = df.fillna("-")
    return df


@log_start_end(log=logger)
def get_currency(symbol) -> str:
    """Quick helper to get currency for financial statements"""
    try:
        ticker_info = yf.Ticker(symbol).info
    except Exception:
        return "Not Specified"

    if "financialCurrency" in ticker_info:
        return ticker_info["financialCurrency"]
    return "Not Specified"
