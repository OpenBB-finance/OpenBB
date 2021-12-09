"""Yahoo Finance Model"""
__docformat__ = "numpy"

from datetime import datetime
from typing import Tuple
import yfinance as yf
import pandas as pd
from gamestonk_terminal.helper_funcs import (
    long_number_format,
)
from gamestonk_terminal.stocks.fundamental_analysis.fa_helper import clean_df_index


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
        ).strftime("%d/%m/%Y")

    df_info = df_info.mask(df_info["Value"].astype(str).eq("[]")).dropna()
    df_info[df_info.index != "Zip"] = df_info[df_info.index != "Zip"].applymap(
        lambda x: long_number_format(x)
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
    ].apply(lambda x: long_number_format(x))
    df_institutional_shareholders["Value"] = df_institutional_shareholders[
        "Value"
    ].apply(lambda x: long_number_format(x))
    df_institutional_shareholders["Stake"] = df_institutional_shareholders[
        "Stake"
    ].apply(lambda x: str(f"{100 * x:.2f}") + " %")

    # Mutualfunds holders
    df_mutualfund_shareholders = stock.mutualfund_holders
    df_mutualfund_shareholders.columns = df_mutualfund_shareholders.columns.str.replace(
        "% Out", "Stake"
    )
    df_mutualfund_shareholders["Shares"] = df_mutualfund_shareholders["Shares"].apply(
        lambda x: long_number_format(x)
    )
    df_mutualfund_shareholders["Value"] = df_mutualfund_shareholders["Value"].apply(
        lambda x: long_number_format(x)
    )
    df_mutualfund_shareholders["Stake"] = df_mutualfund_shareholders["Stake"].apply(
        lambda x: str(f"{100 * x:.2f}") + " %"
    )

    return df_major_holders, df_institutional_shareholders, df_mutualfund_shareholders


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
        lambda x: long_number_format(x)
    )

    return df_calendar


def get_website(ticker: str) -> str:
    """Gets website of company from yfinance"""
    stock = yf.Ticker(ticker)
    df_info = pd.DataFrame(stock.info.items(), columns=["Metric", "Value"])
    return df_info[df_info["Metric"] == "website"]["Value"].values[0]


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
