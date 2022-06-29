"""Yahoo Finance Model"""
__docformat__ = "numpy"

import logging
from datetime import datetime, timedelta
from typing import Tuple
from urllib.request import Request, urlopen

import ssl
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
def get_info(ticker: str) -> pd.DataFrame:
    """Gets ticker info

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    pd.DataFrame
        DataFrame of yfinance information
    """
    stock = yf.Ticker(ticker)
    df_info = pd.DataFrame(stock.info.items(), columns=["Metric", "Value"])
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
def get_shareholders(ticker: str) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Get shareholders from yahoo

    Parameters
    ----------
    ticker : str
        Stock ticker

    Returns
    -------
    pd.DataFrame
        Major holders
    pd.DataFrame
        Institutional holders
    pd.DataFrame
        Mutual Fund holders
    """
    stock = yf.Ticker(ticker)

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

    return df_major_holders, df_institutional_shareholders, df_mutualfund_shareholders


@log_start_end(log=logger)
def get_sustainability(ticker) -> pd.DataFrame:
    """Get sustainability metrics from yahoo

    Parameters
    ----------
    ticker : [type]
        Stock ticker

    Returns
    -------
    pd.DataFrame
        Dataframe of sustainability metrics
    """
    stock = yf.Ticker(ticker)
    pd.set_option("display.max_colwidth", None)

    df_sustainability = stock.sustainability

    if df_sustainability is None or df_sustainability.empty:
        return pd.DataFrame()

    clean_df_index(df_sustainability)

    df_sustainability = df_sustainability.rename(
        index={
            "Controversialweapons": "Controversial Weapons",
            "Socialpercentile": "Social Percentile",
            "Peercount": "Peer Count",
            "Governancescore": "Governance Score",
            "Environmentpercentile": "Environment Percentile",
            "Animaltesting": "Animal Testing",
            "Highestcontroversy": "Highest Controversy",
            "Environmentscore": "Environment Score",
            "Governancepercentile": "Governance Percentile",
            "Militarycontract": "Military Contract",
        }
    )
    return df_sustainability


@log_start_end(log=logger)
def get_calendar_earnings(ticker: str) -> pd.DataFrame:
    """Get calendar earnings for ticker

    Parameters
    ----------
    ticker : [type]
        Stock ticker

    Returns
    -------
    pd.DataFrame
        Dataframe of calendar earnings
    """
    stock = yf.Ticker(ticker)
    df_calendar = stock.calendar

    if df_calendar.empty:
        return pd.DataFrame()

    df_calendar.iloc[0, :] = df_calendar.iloc[0, :].apply(
        lambda x: x.date().strftime("%m/%d/%Y")
    )

    df_calendar.iloc[1:, :] = df_calendar.iloc[1:, :].applymap(
        lambda x: lambda_long_number_format(x)
    )

    return df_calendar


@log_start_end(log=logger)
def get_website(ticker: str) -> str:
    """Gets website of company from yfinance"""
    stock = yf.Ticker(ticker)
    df_info = pd.DataFrame(stock.info.items(), columns=["Metric", "Value"])
    return df_info[df_info["Metric"] == "website"]["Value"].values[0]


@log_start_end(log=logger)
def get_hq(ticker: str) -> str:
    """Gets google map url for headquarter"""
    stock = yf.Ticker(ticker)
    df_info = pd.DataFrame(stock.info.items(), columns=["Metric", "Value"])
    df_info = df_info.set_index("Metric")

    maps = "https://www.google.com/maps/search/"
    for field in ["address1", "address2", "city", "state", "zip", "country"]:
        if field in df_info.index:
            maps += (
                df_info[df_info.index == field]["Value"].values[0].replace(" ", "+")
                + ","
            )
    return maps[:-1]


@log_start_end(log=logger)
def get_dividends(ticker: str) -> pd.DataFrame:
    """Get historical dividend for ticker

    Parameters
    ----------
    ticker: str
        Ticker to get dividend for

    Returns
    -------
    pd.DataFrame:
        Dataframe of dividends and dates
    """
    return pd.DataFrame(yf.Ticker(ticker).dividends)


@log_start_end(log=logger)
def get_mktcap(
    ticker: str, start: datetime = (datetime.now() - timedelta(days=3 * 366))
) -> Tuple[pd.DataFrame, str]:
    """Get market cap over time for ticker. [Source: Yahoo Finance]

    Parameters
    ----------
    ticker: str
        Ticker to get market cap over time
    start: datetime
        Start date to display market cap

    Returns
    -------
    pd.DataFrame:
        Dataframe of estimated market cap over time
    str:
        Currency of ticker
    """
    currency = ""
    df_data = yf.download(ticker, start=start, progress=False, threads=False)
    if not df_data.empty:

        data = yf.Ticker(ticker).info
        if data:
            df_data["Adj Close"] = df_data["Adj Close"] * data["sharesOutstanding"]
            df_data = df_data["Adj Close"]

            currency = data["currency"]

    return df_data, currency


@log_start_end(log=logger)
def get_splits(ticker: str) -> pd.DataFrame:
    """Get splits and reverse splits events. [Source: Yahoo Finance]

    Parameters
    ----------
    ticker: str
        Ticker to get forward and reverse splits
    start: datetime
        Start date to display market cap

    Returns
    -------
    pd.DataFrame:
        Dataframe of forward and reverse splits
    """
    data = yf.Ticker(ticker).splits
    if not data.empty:
        return data.to_frame()
    return pd.DataFrame()


@log_start_end(log=logger)
def get_financials(ticker: str, financial: str) -> pd.DataFrame:
    """Get cashflow statement for company

    Parameters
    ----------
    ticker : str
        Stock ticker
    financial: str
        can be:
            cash-flow
            financials for Income
            balance-sheet

    Returns
    -------
    pd.DataFrame
        Dataframe of Financial statement
    """
    url = (
        "https://uk.finance.yahoo.com/quote/"
        + ticker
        + "/"
        + financial
        + "?p="
        + ticker
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
    new_headers = []

    if financial == "balance-sheet":
        for dates in headers[1:]:
            read = datetime.strptime(dates, "%d/%m/%Y")
            write = read.strftime("%Y-%m-%d")
            new_headers.append(write)
        new_headers[:0] = ["Breakdown"]
        df.columns = new_headers
        df.set_index("Breakdown", inplace=True)
    elif financial == "financials":
        for dates in headers[2:]:
            read = datetime.strptime(dates, "%d/%m/%Y")
            write = read.strftime("%Y-%m-%d")
            new_headers.append(write)
        new_headers[:0] = ["Breakdown", "ttm"]
        df.columns = new_headers
        df.set_index("Breakdown", inplace=True)
    elif financial == "cash-flow":
        for dates in headers[2:]:
            read = datetime.strptime(dates, "%d/%m/%Y")
            write = read.strftime("%Y-%m-%d")
            new_headers.append(write)
        new_headers[:0] = ["Breakdown", "ttm"]
        df.columns = new_headers
        df.set_index("Breakdown", inplace=True)
    df.replace("", np.nan, inplace=True)
    return df.dropna(how="all")
