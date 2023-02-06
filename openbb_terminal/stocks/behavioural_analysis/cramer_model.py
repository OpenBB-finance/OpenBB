"""Cramer Model"""
__docformat__ = "numpy"

import logging
import os
import re

import certifi
import numpy as np
import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import request

logger = logging.getLogger(__name__)

# Necessary only for installer to identify where SSL certs are
os.environ["REQUESTS_CA_BUNDLE"] = certifi.where()
os.environ["SSL_CERT_FILE"] = certifi.where()


@log_start_end(log=logger)
def get_cramer_daily(inverse: bool = True) -> pd.DataFrame:
    """Scrape the daily recommendations of Jim Cramer

    Parameters
    ----------
    inverse: bool
        Whether to include inverse

    Returns
    -------
    pd.DataFrame
        Datafreme of daily Cramer recommendations
    """

    link = (
        "https://madmoney.thestreet.com/screener/index.cfm?showview=stocks&showrows=500"
    )
    r = request(
        link,
        method="POST",
        headers={
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
        },
    )
    if r.status_code != 200:
        return pd.DataFrame()
    soup = BeautifulSoup(r.text, "html.parser")
    table = soup.find_all("table")[0]
    trs = table.find_all("tr")
    recs = {
        "1": "Sell",
        "2": "Sell",
        "3": "Hold",
        "4": "Buy",
        "5": "Buy",
    }

    rec = [recs[tr.find_all("td")[3].find("img")["src"][-5]] for tr in trs[1:]]

    df = pd.read_html(r.text)[0]
    df["Symbol"] = df.Company.apply(lambda x: re.findall(r"[\w]+", x)[-1])
    last_price = [
        round(
            yf.download(ticker, period="1d", interval="1h", progress=False)["Close"][
                -1
            ],
            2,
        )
        for ticker in df.Symbol
    ]

    df["LastPrice"] = last_price
    df["Price"] = df.Price.apply(lambda x: float(x.strip("$")))
    df = df.drop(columns=["Segment", "Call", "Portfolio"])
    df["Change (%)"] = 100 * np.round((df["LastPrice"] - df["Price"]) / df.LastPrice, 4)
    df["Recommendation"] = rec
    df["Company"] = df.apply(lambda x: x.Company.replace(f"({x.Symbol})", ""), axis=1)
    cols = [
        "Date",
        "Company",
        "Symbol",
        "Price",
        "LastPrice",
        "Change (%)",
        "Recommendation",
    ]
    if inverse:
        df["InverseCramer"] = df["Recommendation"].apply(
            lambda x: ["Buy", "Sell"][x == "Buy"]
        )
        cols.append("InverseCramer")
    return df[cols]


@log_start_end(log=logger)
def get_cramer_ticker(symbol: str) -> pd.DataFrame:
    """Get cramer recommendations from beginning of year for given ticker

    Parameters
    ----------
    symbol: str
        Ticker to get recommendations for

    Returns
    -------
    pd.DataFrame
        Dataframe with dates and recommendations
    """

    link = "https://raw.githubusercontent.com/jmaslek/InverseCramer/main/AllRecommendations.csv"
    df = pd.read_csv(link, index_col=0)
    df["Date"] = pd.to_datetime(df["Date"].apply(lambda x: x + "/2022"))
    return df[df.Symbol == symbol].reset_index(drop=True)
