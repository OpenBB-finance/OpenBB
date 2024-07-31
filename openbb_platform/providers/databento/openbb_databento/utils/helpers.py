"""Databento Helper Utility Functions"""

import datetime

import databento as db
import pandas as pd


def get_expiration_date(symbol: str, base_symbol: str):
    """Parse GLOBEX futures symbol to get the expiration date.

    The base symbol is required so that underlying symbols ending in
    numbers are handled correctly.
    """
    # Month codes to month numbers
    month_codes = {
        "F": 1,
        "G": 2,
        "H": 3,
        "J": 4,
        "K": 5,
        "M": 6,
        "N": 7,
        "Q": 8,
        "U": 9,
        "V": 10,
        "X": 11,
        "Z": 12,
    }
    symbol = symbol.replace(base_symbol, "")
    # It will either be something like Z4 or Z25
    if symbol[-2:].isdigit():
        symbol = symbol[-3:]
        month = month_codes[symbol[0]]
        year = int(symbol[-2:]) + 2000
        date = datetime.date(year, month, 1)
        return date.strftime("%b-%Y")
    symbol = symbol[-2:]
    year = int(symbol[-1]) + 2020
    month = month_codes[symbol[0]]
    date = datetime.date(year, month, 1)
    return date.strftime("%b-%Y")


def get_futures_curve(symbol: str, date: str, key: str) -> pd.DataFrame:
    """Gets the end of day futures prices for the underlying symbol.

    Parameters
    ----------
    symbol: str
        Underlying symbol to get chains for
    date: str
        Day to get chains for in YYYY-MM-DD format
    key: str
        API key from the fetcher

    Returns
    -------
    pd.DataFrame
    """
    client = db.Historical(key)
    data = client.timeseries.get_range(
        dataset="GLBX.MDP3",
        symbols=f"{symbol}.FUT",
        stype_in="parent",
        start=f"{date}T00:00:00",
        end=f"{date}T23:59:59",
        schema="ohlcv-1d",
    )
    df = data.to_df().reset_index(drop=False)
    df = df[~df["symbol"].str.contains("-")]
    df["expiration"] = df["symbol"].apply(lambda x: get_expiration_date(x, symbol))
    df = df[["expiration", "close"]].rename(columns={"close": "price"})
    df["expiration"] = pd.to_datetime(df["expiration"], format="%b-%Y")

    # Sort the DataFrame by the 'expiration' column
    df = df.sort_values(by="expiration")

    # Convert the 'expiration' column back to string format
    df["expiration"] = df["expiration"].dt.strftime("%b-%Y")
    return df


def parse_symbol(symbol: str) -> tuple:
    """Parse OCC symbol into ticker, expiry, type, and strike."""
    ticker = symbol[:6].strip()
    expiration = symbol[6:12]
    type = "call" if "C" in symbol else "put"
    strike = int(symbol[13:]) / 1000
    expiration_date = datetime.datetime.strptime(expiration, "%y%m%d").strftime(
        "%Y-%m-%d"
    )

    return ticker, expiration_date, type, strike


def get_options_chain(symbol: str, date: str, key: str) -> pd.DataFrame:
    """
    Gets the end of day options chain for a given symbol and date.
    Parameters
    ----------
    symbol: str
        Underlying symbol to get chains for
    date: str
        Day to get chains for in YYYY-MM-DD format
    key: str
        API key from the fetcher

    Returns
    -------
    pd.DataFrame
    """
    client = db.Historical(key)
    data = client.timeseries.get_range(
        dataset="OPRA.PILLAR",
        symbols=[f"{symbol}.OPT"],
        stype_in="parent",
        start=f"{date}T00:00:00",
        end=f"{date}T23:59:59",
        schema="ohlcv-1d",
        limit=1000,
    )
    df = data.to_df()
    df[["ticker", "expiration", "type", "strike"]] = df.apply(
        lambda row: parse_symbol(row["symbol"]), axis=1, result_type="expand"
    )
    df = df.reset_index(drop=False)
    df["eod_date"] = df["ts_event"].dt.strftime("%Y-%m-%d")
    df = df.drop(columns=["rtype", "publisher_id", "ts_event"])
    return df


def last_business_day(date):
    """A chatgpt helper to get the last business day so this works out of the box"""
    while True:
        date -= pd.Timedelta(days=1)
        if len(pd.bdate_range(date, date)) == 1:
            return date
