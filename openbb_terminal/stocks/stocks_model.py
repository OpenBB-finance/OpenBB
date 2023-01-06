import os
from datetime import datetime

import logging
import pyEX
import requests
import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries

from openbb_terminal.decorators import check_api_key
from openbb_terminal.rich_config import console
from openbb_terminal import config_terminal as cfg

# pylint: disable=unsupported-assignment-operation,no-member

logger = logging.getLogger(__name__)


def load_stock_av(
    symbol: str, start_date: datetime, end_date: datetime
) -> pd.DataFrame:
    try:
        ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas")
        df_stock_candidate: pd.DataFrame = ts.get_daily_adjusted(
            symbol=symbol, outputsize="full"
        )[0]
    except Exception as e:
        console.print(e)
        return pd.DataFrame()

    df_stock_candidate.columns = [
        val.split(". ")[1].capitalize() for val in df_stock_candidate.columns
    ]

    df_stock_candidate = df_stock_candidate.rename(
        columns={"Adjusted close": "Adj Close"}
    )

    # Check that loading a stock was not successful
    if df_stock_candidate.empty:
        console.print("No data found.")
        return pd.DataFrame()

    df_stock_candidate.index = df_stock_candidate.index.tz_localize(None)

    df_stock_candidate.sort_index(ascending=True, inplace=True)

    # Slice dataframe from the starting date YYYY-MM-DD selected
    df_stock_candidate = df_stock_candidate[
        (df_stock_candidate.index >= start_date.strftime("%Y-%m-%d"))
        & (df_stock_candidate.index <= end_date.strftime("%Y-%m-%d"))
    ]
    return df_stock_candidate


def load_stock_yf(
    symbol: str, start_date: datetime, end_date: datetime, weekly: bool, monthly: bool
) -> pd.DataFrame:
    # TODO: Better handling of interval with week/month
    int_ = "1d"
    int_string = "Daily"
    if weekly:
        int_ = "1wk"
        int_string = "Weekly"
    if monthly:
        int_ = "1mo"
        int_string = "Monthly"

    # Win10 version of mktime cannot cope with dates before 1970
    if os.name == "nt" and start_date < datetime(1970, 1, 1):
        start_date = datetime(
            1970, 1, 2
        )  # 1 day buffer in case of timezone adjustments

    # Adding a dropna for weekly and monthly because these include weird NaN columns.
    df_stock_candidate = yf.download(
        symbol, start=start_date, end=end_date, progress=False, interval=int_
    ).dropna(axis=0)

    # Check that loading a stock was not successful
    if df_stock_candidate.empty:
        return pd.DataFrame()

    df_stock_candidate.index.name = "date", int_string
    return df_stock_candidate


def load_stock_eodhd(
    symbol: str, start_date: datetime, end_date: datetime, weekly: bool, monthly: bool
) -> pd.DataFrame:

    int_ = "d"
    if weekly:
        int_ = "w"
    elif monthly:
        int_ = "m"

    request_url = (
        f"https://eodhistoricaldata.com/api/eod/"
        f"{symbol.upper()}?"
        f"{start_date.strftime('%Y-%m-%d')}&"
        f"to={end_date.strftime('%Y-%m-%d')}&"
        f"period={int_}&"
        f"api_token={cfg.API_EODHD_KEY}&"
        f"fmt=json&"
        f"order=d"
    )

    r = requests.get(request_url)
    if r.status_code != 200:
        console.print("[red]Invalid API Key for eodhistoricaldata [/red]")
        console.print(
            "Get your Key here: https://eodhistoricaldata.com/r/?ref=869U7F4J"
        )
        return pd.DataFrame()

    r_json = r.json()

    df_stock_candidate = pd.DataFrame(r_json).dropna(axis=0)

    # Check that loading a stock was not successful
    if df_stock_candidate.empty:
        console.print("No data found from End Of Day Historical Data.")
        return df_stock_candidate

    df_stock_candidate = df_stock_candidate[
        ["date", "open", "high", "low", "close", "adjusted_close", "volume"]
    ]

    df_stock_candidate = df_stock_candidate.rename(
        columns={
            "date": "Date",
            "close": "Close",
            "high": "High",
            "low": "Low",
            "open": "Open",
            "adjusted_close": "Adj Close",
            "volume": "Volume",
        }
    )
    df_stock_candidate["Date"] = pd.to_datetime(df_stock_candidate.Date)
    df_stock_candidate.set_index("Date", inplace=True)
    df_stock_candidate.sort_index(ascending=True, inplace=True)
    return df_stock_candidate


@check_api_key(["API_IEX_TOKEN"])
def load_stock_iex_cloud(symbol: str, iexrange: str) -> pd.DataFrame:
    df_stock_candidate = pd.DataFrame()

    try:
        client = pyEX.Client(api_token=cfg.API_IEX_TOKEN, version="v1")

        df_stock_candidate = client.chartDF(symbol, timeframe=iexrange)

        # Check that loading a stock was not successful
        if df_stock_candidate.empty:
            console.print("No data found.")
            return df_stock_candidate

    except Exception as e:
        if "The API key provided is not valid" in str(e):
            console.print("[red]Invalid API Key[/red]")
        else:
            console.print(e)

        return df_stock_candidate

    df_stock_candidate = df_stock_candidate[
        ["close", "fHigh", "fLow", "fOpen", "fClose", "volume"]
    ]
    df_stock_candidate = df_stock_candidate.rename(
        columns={
            "close": "Close",
            "fHigh": "High",
            "fLow": "Low",
            "fOpen": "Open",
            "fClose": "Adj Close",
            "volume": "Volume",
        }
    )
    df_stock_candidate.sort_index(ascending=True, inplace=True)
    return df_stock_candidate


@check_api_key(["API_POLYGON_KEY"])
def load_stock_polygon(
    symbol: str, start_date: datetime, end_date: datetime, weekly: bool, monthly: bool
) -> pd.DataFrame:
    # Polygon allows: day, minute, hour, day, week, month, quarter, year
    timespan = "day"
    if weekly or monthly:
        timespan = "week" if weekly else "month"

    request_url = (
        f"https://api.polygon.io/v2/aggs/ticker/"
        f"{symbol.upper()}/range/1/{timespan}/"
        f"{start_date.strftime('%Y-%m-%d')}/{end_date.strftime('%Y-%m-%d')}?adjusted=true"
        f"&sort=desc&limit=49999&apiKey={cfg.API_POLYGON_KEY}"
    )
    r = requests.get(request_url)
    if r.status_code != 200:
        console.print("[red]Error in polygon request[/red]")
        return pd.DataFrame()

    r_json = r.json()
    if "results" not in r_json.keys():
        console.print("[red]No results found in polygon reply.[/red]")
        return pd.DataFrame()

    df_stock_candidate = pd.DataFrame(r_json["results"])

    df_stock_candidate = df_stock_candidate.rename(
        columns={
            "o": "Open",
            "c": "Adj Close",
            "h": "High",
            "l": "Low",
            "t": "date",
            "v": "Volume",
            "n": "Transactions",
        }
    )
    df_stock_candidate["date"] = pd.to_datetime(df_stock_candidate.date, unit="ms")
    # TODO: Clean up Close vs Adj Close throughout
    df_stock_candidate["Close"] = df_stock_candidate["Adj Close"]
    df_stock_candidate = df_stock_candidate.sort_values(by="date")
    df_stock_candidate = df_stock_candidate.set_index("date")
    df_stock_candidate.index = df_stock_candidate.index.normalize()
    return df_stock_candidate


def load_quote(symbol: str) -> pd.DataFrame:
    """Ticker quote.  [Source: YahooFinance]

    Parameters
    ----------
    symbol : str
        Ticker
    """
    ticker = yf.Ticker(symbol)

    try:
        quote_df = pd.DataFrame(
            [
                {
                    "Symbol": ticker.info["symbol"],
                    "Name": ticker.info["shortName"],
                    "Price": ticker.info["regularMarketPrice"],
                    "Open": ticker.info["regularMarketOpen"],
                    "High": ticker.info["dayHigh"],
                    "Low": ticker.info["dayLow"],
                    "Previous Close": ticker.info["previousClose"],
                    "Volume": ticker.info["volume"],
                    "52 Week High": ticker.info["fiftyTwoWeekHigh"],
                    "52 Week Low": ticker.info["fiftyTwoWeekLow"],
                }
            ]
        )

        quote_df["Change"] = quote_df["Price"] - quote_df["Previous Close"]
        quote_df["Change %"] = quote_df.apply(
            lambda x: f'{((x["Change"] / x["Previous Close"]) * 100):.2f}%',
            axis="columns",
        )
        for c in [
            "Price",
            "Open",
            "High",
            "Low",
            "Previous Close",
            "52 Week High",
            "52 Week Low",
            "Change",
        ]:
            quote_df[c] = quote_df[c].apply(lambda x: f"{x:.2f}")
        quote_df["Volume"] = quote_df["Volume"].apply(lambda x: f"{x:,}")

        quote_df = quote_df.set_index("Symbol")

        quote_data = quote_df.T

        return quote_data

    except KeyError:
        logger.exception("Invalid stock ticker")
        console.print(f"Invalid stock ticker: {symbol}")
        return pd.DataFrame()
