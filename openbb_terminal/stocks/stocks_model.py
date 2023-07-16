import logging
import os
from datetime import datetime
from typing import List
from urllib.error import HTTPError

import fundamentalanalysis as fa  # Financial Modeling Prep
import intrinio_sdk as intrinio
import pandas as pd
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key, log_start_end
from openbb_terminal.helper_funcs import lambda_long_number_format, request
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.fundamental_analysis.fa_helper import clean_df_index

# pylint: disable=unsupported-assignment-operation,no-member

logger = logging.getLogger(__name__)


def load_stock_intrinio(
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    weekly: bool = False,
    monthly: bool = False,
) -> pd.DataFrame:
    intrinio.ApiClient().set_api_key(get_current_user().credentials.API_INTRINIO_KEY)
    api = intrinio.SecurityApi()
    frequency: str = "daily"
    if weekly is True:
        frequency = "weekly"
    if monthly is True:
        frequency = "monthly"
    stock = api.get_security_stock_prices(
        symbol.upper(),
        start_date=start_date,
        end_date=end_date,
        frequency=frequency,
        page_size=10000,
    )
    data = stock
    while stock.next_page:
        stock = api.get_security_stock_prices(
            symbol.upper(),
            next_page=stock.next_page,
            page_size=10000,
        )
        data.stock_prices.extend(stock.stock_prices)
    data = data.to_dict()
    data = pd.DataFrame(data["stock_prices"])
    df = pd.DataFrame(data)[
        [
            "adj_open",
            "adj_high",
            "adj_low",
            "close",
            "adj_close",
            "date",
            "adj_volume",
            "dividend",
            "split_ratio",
            "change",
            "percent_change",
            "fifty_two_week_high",
            "fifty_two_week_low",
        ]
    ]
    df["date"] = pd.DatetimeIndex(df["date"])
    df["close"] = df["adj_close"]
    df = df.set_index("date").rename(
        columns={
            "adj_close": "Adj Close",
            "adj_open": "Open",
            "close": "Close",
            "adj_high": "High",
            "adj_low": "Low",
            "adj_volume": "Volume",
            "dividend": "Dividend",
            "split_ratio": "Split Ratio",
            "change": "Change",
            "percent_change": "Percent Change",
            "fifty_two_week_high": "52 Week High",
            "fifty_two_week_low": "52 Week Low",
        }
    )[::-1]

    return df


def load_stock_av(
    symbol: str,
    interval: str,
    start_date: datetime,
    end_date: datetime,
    interval_min: str = "1min",
) -> pd.DataFrame:
    try:
        ts = TimeSeries(
            key=get_current_user().credentials.API_KEY_ALPHAVANTAGE,
            output_format="pandas",
        )
        if interval == "Minute":
            df_stock_candidate: pd.DataFrame = ts.get_intraday(
                symbol=symbol, interval=interval_min, outputsize="full"
            )[0]
        elif interval == "Daily":
            df_stock_candidate = ts.get_daily_adjusted(
                symbol=symbol, outputsize="full"
            )[0]
        elif interval == "Weekly":
            df_stock_candidate = ts.get_weekly_adjusted(symbol=symbol)[0]
        elif interval == "Monthly":
            df_stock_candidate = ts.get_monthly_adjusted(symbol=symbol)[0]
        else:
            console.print("Invalid interval specified")
            return pd.DataFrame()
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

    df_stock_candidate.sort_index(ascending=True, inplace=True)

    df_stock_candidate.index = df_stock_candidate.index.tz_localize(None)

    df_stock_candidate = df_stock_candidate[
        (df_stock_candidate.index >= start_date)
        & (df_stock_candidate.index <= end_date)
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

    # add 1 day to end_date to include the last day
    end_date = end_date + pd.Timedelta(days=1)

    # Adding a dropna for weekly and monthly because these include weird NaN columns.
    df_stock_candidate = yf.download(
        symbol,
        start=start_date,
        end=end_date,
        progress=False,
        auto_adjust=True,
        actions=True,
        interval=int_,
        ignore_tz=True,
    ).dropna(axis=0)

    # Check that loading a stock was not successful
    if df_stock_candidate.empty:
        return pd.DataFrame()
    df_stock_candidate_cols = [
        "Open",
        "High",
        "Low",
        "Close",
        "Adj Close",
        "Volume",
        "Dividends",
        "Stock Splits",
    ]
    df_stock_candidate.index.name = "date", int_string
    df_stock_candidate["Adj Close"] = df_stock_candidate["Close"].copy()
    df_stock_candidate = pd.DataFrame(
        data=df_stock_candidate, columns=df_stock_candidate_cols
    )
    return df_stock_candidate


def load_stock_eodhd(
    symbol: str,
    start_date: datetime,
    end_date: datetime,
    weekly: bool,
    monthly: bool,
    intraday: bool = False,
) -> pd.DataFrame:
    request_url = "https://eodhistoricaldata.com/api/eod/"

    int_ = "d"
    if weekly:
        int_ = "w"
    elif monthly:
        int_ = "m"
    elif intraday:
        int_ = "1m"
        request_url = "https://eodhistoricaldata.com/api/intraday/"

    request_url = (
        f"{request_url}"
        f"{symbol.upper()}?"
        f"from={start_date.strftime('%Y-%m-%d')}&"
        f"to={end_date.strftime('%Y-%m-%d')}&"
        f"period={int_}&"
        f"api_token={get_current_user().credentials.API_EODHD_KEY}&"
        f"fmt=json&"
        f"order=d"
    )

    r = request(request_url)
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
        f"&sort=desc&limit=49999&apiKey={get_current_user().credentials.API_POLYGON_KEY}"
    )
    r = request(request_url)
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


@log_start_end(log=logger)
@check_api_key(["API_KEY_FINANCIALMODELINGPREP"])
def get_quote(symbols: List[str]) -> pd.DataFrame:
    """Gets ticker quote from FMP

    Parameters
    ----------
    symbols : List[str]
        A list of Stock ticker symbols

    Returns
    -------
    pd.DataFrame
        Dataframe of ticker quote

    Examples
    --------

    A single ticker must be entered as a list.

    >>> df = openbb.stocks.quote(["AAPL"])

    Multiple tickers can be retrieved.

    >>> df = openbb.stocks.quote(["AAPL","MSFT","GOOG","NFLX","META","AMZN","NVDA"])
    """

    symbol = symbols if isinstance(symbols, list) is False else ",".join(symbols)

    df_fa = pd.DataFrame()

    try:
        df_fa = fa.quote(
            symbol, get_current_user().credentials.API_KEY_FINANCIALMODELINGPREP
        ).rename({"yearLow": "52 Week Low", "yearHigh": "52 Week High"})
    # Invalid API Keys
    except ValueError:
        console.print("[red]Invalid API Key[/red]\n")
    # Premium feature, API plan is not authorized
    except HTTPError:
        console.print("[red]API Key not authorized for Premium feature[/red]\n")

    if not df_fa.empty:
        clean_df_index(df_fa)
        for c in df_fa.columns:
            if not get_current_user().preferences.USE_INTERACTIVE_DF:
                df_fa.loc["Market cap"][c] = lambda_long_number_format(
                    df_fa.loc["Market cap"][c]
                )
                df_fa.loc["Shares outstanding"][c] = lambda_long_number_format(
                    df_fa.loc["Shares outstanding"][c]
                )
                df_fa.loc["Volume"][c] = lambda_long_number_format(
                    df_fa.loc["Volume"][c]
                )
            # Check if there is a valid earnings announcement
            if df_fa.loc["Earnings announcement"][c]:
                earning_announcement = datetime.strptime(
                    df_fa.loc["Earnings announcement"][c][0:19], "%Y-%m-%dT%H:%M:%S"
                )
                df_fa.loc["Earnings announcement"][
                    c
                ] = f"{earning_announcement.date()} {earning_announcement.time()}"
            # Check if there is a valid timestamp and convert it to a readable format
            if "Timestamp" in df_fa.index and df_fa.loc["Timestamp"][c]:
                df_fa.loc["Timestamp"][c] = datetime.fromtimestamp(
                    df_fa.loc["Timestamp"][c]
                ).strftime("%Y-%m-%d %H:%M:%S")

        df_fa.columns = df_fa.loc["Symbol"][:]
        df_fa = df_fa.drop("Symbol", axis=0)
        df_fa.index = df_fa.index.str.title()

    return df_fa
