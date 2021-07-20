"""Main helper"""
__docformat__ = "numpy"
import argparse
from typing import List
import os
import sys
import subprocess
import random
from datetime import datetime, timedelta
import hashlib
import requests
from colorama import Fore, Style
import matplotlib.pyplot as plt
from numpy.core.fromnumeric import transpose
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import quandl
import mplfinance as mpf
import yfinance as yf
from coinmarketcapapi import CoinMarketCapAPI, CoinMarketCapAPIError
import pytz
import pyEX
from pyEX.common.exception import PyEXception
from tabulate import tabulate
import praw
from prawcore.exceptions import ResponseException

# import git

# pylint: disable=no-member,too-many-branches,C0302

from gamestonk_terminal.helper_funcs import (
    valid_date,
    plot_view_stock,
    parse_known_args_and_warn,
    plot_autoscale,
)

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal import thought_of_the_day as thought
from gamestonk_terminal.technical_analysis import trendline_api as trend


def clear(other_args: List[str], s_ticker, s_start, s_interval, df_stock):
    """Clears loaded stock and returns empty variables

    Parameters
    ----------
    other_args : List[str]
        Argparse arguments
    s_ticker : str
        Ticker
    s_start : str
        Start date
    s_interval : str
        Interval to get data for
    df_stock : pd.DataFrame
        Preloaded dataframe

    Returns
    -------
    str
        Ticker
    str
        Start date
    str
        Interval
    pd.DataFrame
        Dataframe of data
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="clear",
        description="""Clear previously loaded stock ticker.""",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return "", "", "", pd.DataFrame()

        print("Clearing stock ticker to be used for analysis\n")
        return "", "", "", pd.DataFrame()

    except SystemExit:
        print("")
        return s_ticker, s_start, s_interval, df_stock


def load(other_args: List[str], s_ticker, s_start, s_interval, df_stock):
    """Load selected ticker

    Parameters
    ----------
    other_args : List[str]
        Argparse arguments
    s_ticker : str
        Ticker
    s_start : str
        Start date
    s_interval : str
        Interval to get data for
    df_stock : pd.DataFrame
        Preloaded dataframe

    Returns
    -------
    str
        Ticker
    str
        Start date
    str
        Interval
    pd.DataFrame
        Dataframe of data.
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="load",
        description="Load stock ticker to perform analysis on. When the data source is 'yf', an Indian ticker can be"
        " loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in"
        " https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html.",
    )
    parser.add_argument(
        "-t",
        "--ticker",
        action="store",
        dest="s_ticker",
        required="-h" not in other_args,
        help="Stock ticker",
    )
    parser.add_argument(
        "-s",
        "--start",
        type=valid_date,
        default="2019-01-01",
        dest="s_start_date",
        help="The starting date (format YYYY-MM-DD) of the stock",
    )
    parser.add_argument(
        "-i",
        "--interval",
        action="store",
        dest="n_interval",
        type=int,
        default=1440,
        choices=[1, 5, 15, 30, 60],
        help="Intraday stock minutes",
    )
    parser.add_argument(
        "--source",
        action="store",
        dest="source",
        choices=["yf", "av", "iex"],
        default="yf",
        help="Source of historical data.",
    )
    parser.add_argument(
        "-p",
        "--prepost",
        action="store_true",
        default=False,
        dest="b_prepost",
        help="Pre/After market hours. Only works for 'yf' source, and intraday data",
    )

    try:
        # For the case where a user uses: 'load BB'
        if other_args:
            if "-t" not in other_args and "-h" not in other_args:
                other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return [s_ticker, s_start, s_interval, df_stock]

        # Daily
        if ns_parser.n_interval == 1440:

            # Alpha Vantage Source
            if ns_parser.source == "av":
                ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas")
                # pylint: disable=unbalanced-tuple-unpacking
                df_stock_candidate, _ = ts.get_daily_adjusted(
                    symbol=ns_parser.s_ticker, outputsize="full"
                )

                df_stock_candidate.columns = [
                    val.split(". ")[1].capitalize()
                    for val in df_stock_candidate.columns
                ]

                df_stock_candidate = df_stock_candidate.rename(
                    columns={
                        "Adjusted close": "Adj Close",
                    }
                )

                # Check that loading a stock was not successful
                # pylint: disable=no-member
                if df_stock_candidate.empty:
                    print("")
                    return [s_ticker, s_start, s_interval, df_stock]

                # pylint: disable=no-member
                df_stock_candidate.sort_index(ascending=True, inplace=True)

                # Slice dataframe from the starting date YYYY-MM-DD selected
                df_stock_candidate = df_stock_candidate[ns_parser.s_start_date :]

            # Yahoo Finance Source
            elif ns_parser.source == "yf":
                df_stock_candidate = yf.download(
                    ns_parser.s_ticker, start=ns_parser.s_start_date, progress=False
                )

                # Check that loading a stock was not successful
                if df_stock_candidate.empty:
                    print("")
                    return [s_ticker, s_start, s_interval, df_stock]

                df_stock_candidate.index.name = "date"

            # IEX Cloud Source
            elif ns_parser.source == "iex":
                client = pyEX.Client(api_token=cfg.API_IEX_TOKEN, version="v1")

                df_stock_candidate = client.chartDF(ns_parser.s_ticker)

                # Check that loading a stock was not successful
                if df_stock_candidate.empty:
                    print("")
                    return [s_ticker, s_start, s_interval, df_stock]

                df_stock_candidate = df_stock_candidate[
                    ["uClose", "uHigh", "uLow", "uOpen", "fClose", "volume"]
                ]
                df_stock_candidate = df_stock_candidate.rename(
                    columns={
                        "uClose": "Close",
                        "uHigh": "High",
                        "uLow": "Low",
                        "uOpen": "Open",
                        "fClose": "Adj Close",
                        "volume": "Volume",
                    }
                )

                df_stock_candidate.sort_index(ascending=True, inplace=True)

                # Slice dataframe from the starting date YYYY-MM-DD selected
                df_stock_candidate = df_stock_candidate[ns_parser.s_start_date :]

            # Check if start time from dataframe is more recent than specified
            if df_stock_candidate.index[0] > pd.to_datetime(ns_parser.s_start_date):
                s_start = df_stock_candidate.index[0]
            else:
                s_start = ns_parser.s_start_date

        # Intraday
        else:

            # Alpha Vantage Source
            if ns_parser.source == "av":
                ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas")
                # pylint: disable=unbalanced-tuple-unpacking
                df_stock_candidate, _ = ts.get_intraday(
                    symbol=ns_parser.s_ticker,
                    outputsize="full",
                    interval=str(ns_parser.n_interval) + "min",
                )

                df_stock_candidate.columns = [
                    val.split(". ")[1].capitalize()
                    for val in df_stock_candidate.columns
                ]

                df_stock_candidate = df_stock_candidate.rename(
                    columns={
                        "Adjusted close": "Adj Close",
                    }
                )

                s_interval = str(ns_parser.n_interval) + "min"
                # Check that loading a stock was not successful
                # pylint: disable=no-member
                if df_stock_candidate.empty:
                    print("")
                    return [s_ticker, s_start, s_interval, df_stock]

                # pylint: disable=no-member
                df_stock_candidate.sort_index(ascending=True, inplace=True)

                # Slice dataframe from the starting date YYYY-MM-DD selected
                df_stock_candidate = df_stock_candidate[ns_parser.s_start_date :]

                # Check if start time from dataframe is more recent than specified
                if df_stock_candidate.index[0] > pd.to_datetime(ns_parser.s_start_date):
                    s_start = df_stock_candidate.index[0]
                else:
                    s_start = ns_parser.s_start_date

            # Yahoo Finance Source
            elif ns_parser.source == "yf":
                s_int = str(ns_parser.n_interval) + "m"
                s_interval = s_int + "in"
                d_granularity = {"1m": 6, "5m": 59, "15m": 59, "30m": 59, "60m": 729}

                s_start_dt = datetime.utcnow() - timedelta(days=d_granularity[s_int])
                s_date_start = s_start_dt.strftime("%Y-%m-%d")

                if s_start_dt > ns_parser.s_start_date:
                    # Using Yahoo Finance with granularity {s_int} the starting date is set to: {s_date_start}

                    df_stock_candidate = yf.download(
                        ns_parser.s_ticker,
                        start=s_date_start,
                        progress=False,
                        interval=s_int,
                        prepost=ns_parser.b_prepost,
                    )

                else:
                    df_stock_candidate = yf.download(
                        ns_parser.s_ticker,
                        start=ns_parser.s_start_date.strftime("%Y-%m-%d"),
                        progress=False,
                        interval=s_int,
                        prepost=ns_parser.b_prepost,
                    )

                # Check that loading a stock was not successful
                if df_stock_candidate.empty:
                    print("")
                    return [s_ticker, s_start, s_interval, df_stock]

                if s_start_dt > ns_parser.s_start_date:
                    s_start = pytz.utc.localize(s_start_dt)
                else:
                    s_start = ns_parser.s_start_date

                df_stock_candidate.index.name = "date"

            # IEX Cloud Source
            elif ns_parser.source == "iex":

                s_interval = str(ns_parser.n_interval) + "min"
                client = pyEX.Client(api_token=cfg.API_IEX_TOKEN, version="v1")

                df_stock_candidate = client.chartDF(ns_parser.s_ticker)

                df_stock_candidate = client.intradayDF(ns_parser.s_ticker).iloc[
                    0 :: ns_parser.n_interval
                ]

                df_stock_candidate = df_stock_candidate[
                    ["close", "high", "low", "open", "volume", "close"]
                ]
                df_stock_candidate.columns = [
                    x.capitalize() for x in df_stock_candidate.columns
                ]

                df_stock_candidate.columns = list(df_stock_candidate.columns[:-1]) + [
                    "Adj Close"
                ]

                df_stock_candidate.sort_index(ascending=True, inplace=True)

                new_index = list()
                for idx in range(len(df_stock_candidate)):
                    dt_time = datetime.strptime(
                        df_stock_candidate.index[idx][1], "%H:%M"
                    )
                    new_index.append(
                        df_stock_candidate.index[idx][0]
                        + timedelta(hours=dt_time.hour, minutes=dt_time.minute)
                    )

                df_stock_candidate.index = pd.DatetimeIndex(new_index)
                df_stock_candidate.index.name = "date"

                # Slice dataframe from the starting date YYYY-MM-DD selected
                df_stock_candidate = df_stock_candidate[ns_parser.s_start_date :]

                # Check if start time from dataframe is more recent than specified
                if df_stock_candidate.index[0] > pd.to_datetime(ns_parser.s_start_date):
                    s_start = df_stock_candidate.index[0]
                else:
                    s_start = ns_parser.s_start_date

        s_intraday = (f"Intraday {s_interval}", "Daily")[ns_parser.n_interval == 1440]

        print(
            f"Loading {s_intraday} {ns_parser.s_ticker.upper()} stock "
            f"with starting period {s_start.strftime('%Y-%m-%d')} for analysis.\n"
        )

        return [
            ns_parser.s_ticker.upper(),
            s_start,
            str(ns_parser.n_interval) + "min",
            df_stock_candidate,
        ]

    except Exception as e:
        print(e, "\nEither the ticker or the API_KEY are invalids. Try again!\n")
        return [s_ticker, s_start, s_interval, df_stock]

    except SystemExit:
        print("")
        return [s_ticker, s_start, s_interval, df_stock]


def candle(s_ticker: str, other_args: List[str]):
    """Shows candle plot of loaded ticker

    Parameters
    ----------
    s_ticker: str
        Ticker to display
    other_args: str
        Argparse arguments
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="candle",
        description="Displays candle chart of loaded ticker",
    )

    parser.add_argument(
        "-s",
        "--start_date",
        dest="s_start",
        type=valid_date,
        default=(datetime.now() - timedelta(days=180)).strftime("%Y-%m-%d"),
        help="Start date for candle data",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return
        if not s_ticker:
            print("No ticker loaded.  First use `load {ticker}`", "\n")
            return

        df_stock = trend.load_ticker(s_ticker, ns_parser.s_start)
        df_stock = trend.find_trendline(df_stock, "OC_High", "high")
        df_stock = trend.find_trendline(df_stock, "OC_Low", "low")

        mc = mpf.make_marketcolors(
            up="green", down="red", edge="black", wick="black", volume="in", ohlc="i"
        )

        s = mpf.make_mpf_style(marketcolors=mc, gridstyle=":", y_on_right=True)

        ap0 = []

        if "OC_High_trend" in df_stock.columns:
            ap0.append(
                mpf.make_addplot(df_stock["OC_High_trend"], color="g"),
            )

        if "OC_Low_trend" in df_stock.columns:
            ap0.append(
                mpf.make_addplot(df_stock["OC_Low_trend"], color="b"),
            )

        if gtff.USE_ION:
            plt.ion()

        mpf.plot(
            df_stock,
            type="candle",
            mav=(20, 50),
            volume=True,
            title=f"\n{s_ticker} - Starting {ns_parser.s_start.strftime('%Y-%m-%d')}",
            addplot=ap0,
            xrotation=10,
            style=s,
            figratio=(10, 7),
            figscale=1.10,
            figsize=(plot_autoscale()),
            update_width_config=dict(
                candle_linewidth=1.0, candle_width=0.8, volume_linewidth=1.0
            ),
        )
        print("")

    except Exception as e:
        print(e, "\n")


def quote(other_args: List[str], s_ticker: str):
    """Ticker quote

    Parameters
    ----------
    other_args : List[str]
        Argparse arguments
    s_ticker : str
        Ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="quote",
        description="Current quote for stock ticker",
    )

    if s_ticker:
        parser.add_argument(
            "-t",
            "--ticker",
            action="store",
            dest="s_ticker",
            default=s_ticker,
            help="Stock ticker",
        )
    else:
        parser.add_argument(
            "-t",
            "--ticker",
            action="store",
            dest="s_ticker",
            required=True,
            help="Stock ticker",
        )

    try:
        # For the case where a user uses: 'quote BB'
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

    except SystemExit:
        print("")
        return

    ticker = yf.Ticker(ns_parser.s_ticker)

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
            lambda x: "{:.2f}%".format((x["Change"] / x["Previous Close"]) * 100),
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

        quote_data = transpose(quote_df)

        print(
            tabulate(
                quote_data,
                headers=quote_data.columns,
                tablefmt="fancy_grid",
                stralign="right",
            )
        )
    except KeyError:
        print(f"Invalid stock ticker: {ns_parser.s_ticker}")

    print("")
    return


def view(other_args: List[str], s_ticker: str, s_interval, df_stock):
    """Plot loaded ticker

    Parameters
    ----------
    other_args : List[str]
        Argparse arguments
    s_ticker : str
        Ticker to load
    s_interval : str
        Interval tto get data for
    df_stock : pd.Dataframe
        Preloaded dataframe to plot
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="view",
        description="Visualize historical data of a stock.",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        if not s_ticker:
            print("No ticker loaded.  First use `load {ticker}`", "\n")
            return

        # Plot view of the stock
        plot_view_stock(df_stock, s_ticker, s_interval)

    except Exception as e:
        print("Error in plotting:")
        print(e, "\n")

    except SystemExit:
        print("")
        return


# pylint: disable=too-many-statements


def check_api_keys():
    """Check api keys and if they are supplied"""

    key_dict = {}
    if cfg.API_KEY_ALPHAVANTAGE == "REPLACE_ME":  # pragma: allowlist secret
        key_dict["ALPHA_VANTAGE"] = "Not defined"
    else:
        df = TimeSeries(
            key=cfg.API_KEY.ALPHAVANTAGE, output_format="pandas"
        ).get_intraday(symbol="AAPL")
        if df.empty:
            key_dict["ALPHA_VANTAGE"] = "defined, test failed"
        else:
            key_dict["ALPHA_VANTAGE"] = "defined, test passed"

    if cfg.API_KEY_FINANCIALMODELINGPREP == "REPLACE_ME":  # pragma: allowlist secret
        key_dict["FINANCIAL_MODELING_PREP"] = "Not defined"
    else:
        r = requests.get(
            f"https://financialmodelingprep.com/api/v3/profile/AAPL?apikey={cfg.API_KEY_FINANCIALMODELINGPREP}"
        )
        if r.status_code in [403, 401]:
            key_dict["FINANCIAL_MODELING_PREP"] = "defined, test failed"
        elif r.status_code == 200:
            key_dict["FINANCIAL_MODELING_PREP"] = "defined, test passed"
        else:
            key_dict["FINANCIAL_MODELING_PREP"] = "defined, test inconclusive"

    if cfg.API_KEY_QUANDL == "REPLACE_ME":  # pragma: allowlist secret
        key_dict["QUANDL"] = "Not defined"
    else:
        try:
            quandl.save_key(cfg.API_KEY_QUANDL)
            quandl.get_table(
                "ZACKS/FC",
                paginate=True,
                ticker=["AAPL", "MSFT"],
                per_end_date={"gte": "2015-01-01"},
                qopts={"columns": ["ticker", "per_end_date"]},
            )
            key_dict["QUANDL"] = "defined, test passed"
        except quandl.errors.quandl_error.ForbiddenError:
            key_dict["QUANDL"] = "defined, test failed"

    if cfg.API_POLYGON_KEY == "REPLACE_ME":
        key_dict["POLYGON"] = "Not defined"
    else:
        r = requests.get(
            f"https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2020-06-01/2020-06-17?apiKey={cfg.API_POLYGON_KEY}"
        )
        if r.status_code in [403, 401]:
            key_dict["POLYGON"] = "defined, test failed"
        elif r.status_code == 200:
            key_dict["POLYGON"] = "defined, test passed"
        else:
            key_dict["POLYGON"] = "defined, test inconclusive"

    if cfg.API_FRED_KEY == "REPLACE_ME":
        key_dict["FRED"] = "Not defined"
    else:
        r = requests.get(
            f"https://api.stlouisfed.org/fred/series?series_id=GNPCA&api_key={cfg.API_FRED_KEY}"
        )
        if r.status_code in [403, 401, 400]:
            key_dict["FRED"] = "defined, test failed"
        elif r.status_code == 200:
            key_dict["FRED"] = "defined, test passed"
        else:
            key_dict["FRED"] = "defined, test inconclusive"

    if cfg.API_NEWS_TOKEN == "REPLACE_ME":
        key_dict["NEWSAPI"] = "Not defined"
    else:
        r = requests.get(
            f"https://newsapi.org/v2/everything?q=keyword&apiKey={cfg.API_NEWS_TOKEN}"
        )
        if r.status_code in [401, 403]:
            key_dict["NEWSAPI"] = "defined, test failed"
        elif r.status_code == 200:
            key_dict["NEWSAPI"] = "defined, test passed"
        else:
            key_dict["NEWSAPI"] = "defined, test inconclusive"

    if cfg.TRADIER_TOKEN == "REPLACE_ME":
        key_dict["TRADIER"] = "Not defined"
    else:
        r = requests.get(
            "https://sandbox.tradier.com/v1/markets/quotes",
            params={"symbols": "AAPL"},
            headers={
                "Authorization": f"Bearer {cfg.TRADIER_TOKEN}",
                "Accept": "application/json",
            },
        )
        if r.status_code in [401, 403]:
            key_dict["TRADIER"] = "defined, test failed"
        elif r.status_code == 200:
            key_dict["TRADIER"] = "defined, test passed"
        else:
            key_dict["TRADIER"] = "defined, test inconclusive"

    if cfg.API_CMC_KEY == "REPLACE_ME":
        key_dict["COINMARKETCAP"] = "Not defined"
    else:
        cmc = CoinMarketCapAPI(cfg.API_CMC_KEY)
        try:
            cmc.exchange_info()
            key_dict["COINMARKETCAP"] = "defined, test passed"
        except CoinMarketCapAPIError:
            key_dict["COINMARKETCAP"] = "defined, test failed"

    if cfg.API_FINNHUB_KEY == "REPLACE_ME":
        key_dict["FINNHUB"] = "Not defined"
    else:
        r = r = requests.get(
            f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={cfg.API_FINNHUB_KEY}"
        )
        if r.status_code in [403, 401, 400]:
            key_dict["FINNHUB"] = "defined, test failed"
        elif r.status_code == 200:
            key_dict["FINNHUB"] = "defined, test passed"
        else:
            key_dict["FINNHUB"] = "defined, test inconclusive"

    if cfg.API_IEX_TOKEN == "REPLACE_ME":
        key_dict["IEXCLOUD"] = "Not defined"
    else:
        try:
            pyEX.Client(api_token=cfg.API_IEX_TOKEN, version="v1")
            key_dict["IEXCLOUD"] = "defined, test passed"
        except PyEXception:
            key_dict["IEXCLOUD"] = "defined, test failed"

    # Reddit
    reddit_keys = [
        cfg.API_REDDIT_CLIENT_ID,
        cfg.API_REDDIT_CLIENT_SECRET,
        cfg.API_REDDIT_USERNAME,
        cfg.API_REDDIT_PASSWORD,
        cfg.API_REDDIT_USER_AGENT,
    ]
    if "REPLACE_ME" in reddit_keys:
        key_dict["REDDIT"] = "Not defined"
    else:
        praw_api = praw.Reddit(
            client_id=cfg.API_REDDIT_CLIENT_ID,
            client_secret=cfg.API_REDDIT_CLIENT_SECRET,
            username=cfg.API_REDDIT_USERNAME,
            user_agent=cfg.API_REDDIT_USER_AGENT,
            password=cfg.API_REDDIT_PASSWORD,
        )

        try:
            praw_api.user.me()
            key_dict["REDDIT"] = "defined, test passed"
        except ResponseException:
            key_dict["REDDIT"] = "defined, test failed"

    # Twitter keys
    twitter_keys = [
        cfg.API_TWITTER_KEY,
        cfg.API_TWITTER_SECRET_KEY,
        cfg.API_TWITTER_BEARER_TOKEN,
    ]
    if "REPLACE_ME" in twitter_keys:
        key_dict["TWITTER"] = "Not defined"
    else:
        params = {
            "query": "(\\$AAPL) (lang:en)",
            "max_results": "10",
            "tweet.fields": "created_at,lang",
        }
        r = requests.get(
            "https://api.twitter.com/2/tweets/search/recent",
            params=params,  # type: ignore
            headers={"authorization": "Bearer " + cfg.API_TWITTER_BEARER_TOKEN},
        )
        if r.status_code == 200:
            key_dict["TWITTER"] = "defined, test passed"
        elif r.status_code in [401, 403]:
            key_dict["TWITTER"] = "defined, test failed"
        else:
            key_dict["TWITTER"] = "defined, test inconclusive"

    # Robinhood keys
    rh_keys = [cfg.RH_USERNAME, cfg.RH_PASSWORD]
    if "REPLACE_ME" in rh_keys:
        key_dict["ROBINHOOD"] = "Not defined"
    else:
        key_dict["ROBINHOOD"] = "defined, not tested"
    # Degiro keys
    dg_keys = [cfg.DG_USERNAME, cfg.DG_PASSWORD, cfg.DG_TOTP_SECRET]
    if "REPLACE_ME" in dg_keys:
        key_dict["DEGIRO"] = "Not defined"
    else:
        key_dict["DEGIRO"] = "defined, not tested"
    # OANDA keys
    oanda_keys = [cfg.OANDA_TOKEN, cfg.OANDA_ACCOUNT]
    if "REPLACE_ME" in oanda_keys:
        key_dict["OANDA"] = "Not defined"
    else:
        key_dict["OANDA"] = "defined, not tested"
    # Binance keys
    bn_keys = [cfg.API_BINANCE_KEY, cfg.API_BINANCE_SECRET]
    if "REPLACE_ME" in bn_keys:
        key_dict["BINANCE"] = "Not defined"
    else:
        key_dict["BINANCE"] = "defined, not tested"

    print(
        tabulate(
            pd.DataFrame(key_dict.items()),
            showindex=False,
            headers=[],
            tablefmt="fancy_grid",
        ),
        "\n",
    )


def print_goodbye():
    """Prints a goodbye message when quitting the terminal"""
    goodbye_msg = [
        "An informed ape, is a strong ape. ",
        "Remember that stonks only go up. ",
        "Diamond hands. ",
        "Apes together strong. ",
        "This is our way. ",
        "Keep the spacesuit ape, we haven't reached the moon yet. ",
        "I am not a cat. I'm an ape. ",
        "We like the terminal. ",
    ]

    goodbye_hr = datetime.now().hour
    if goodbye_hr < 5:
        goodbye_msg_time = "Go get some rest soldier!"
    elif goodbye_hr < 11:
        goodbye_msg_time = "Rise and shine baby!"
    elif goodbye_hr < 17:
        goodbye_msg_time = "Enjoy your day!"
    elif goodbye_hr < 23:
        goodbye_msg_time = "Tomorrow's another day!"
    else:
        goodbye_msg_time = "Go get some rest soldier!"

    print(
        goodbye_msg[random.randint(0, len(goodbye_msg) - 1)] + goodbye_msg_time + "\n"
    )


def sha256sum(filename):
    h = hashlib.sha256()
    b = bytearray(128 * 1024)
    mv = memoryview(b)
    with open(filename, "rb", buffering=0) as f:
        for n in iter(lambda: f.readinto(mv), 0):
            h.update(mv[:n])
    return h.hexdigest()


def update_terminal():
    """Updates the terminal by running git pull in the directory.  Runs poetry install if needed"""
    poetry_hash = sha256sum("poetry.lock")

    completed_process = subprocess.run("git pull", shell=True, check=False)
    if completed_process.returncode != 0:
        return completed_process.returncode

    new_poetry_hash = sha256sum("poetry.lock")

    if poetry_hash == new_poetry_hash:
        print("Great, seems like poetry hasn't been updated!")
        return completed_process.returncode
    print(
        "Seems like more modules have been added, grab a coke, this may take a while."
    )

    completed_process = subprocess.run("poetry install", shell=True, check=False)
    if completed_process.returncode != 0:
        return completed_process.returncode

    return 0


def about_us():
    """Prints an about us section"""
    print(
        f"\n{Fore.GREEN}Thanks for using Gamestonk Terminal. This is our way!{Style.RESET_ALL}\n"
        "\n"
        f"{Fore.CYAN}Join our community on discord: {Style.RESET_ALL}https://discord.gg/Up2QGbMKHY\n"
        f"{Fore.CYAN}Follow our twitter for updates: {Style.RESET_ALL}https://twitter.com/gamestonkt\n"
        f"{Fore.CYAN}Access our landing page: {Style.RESET_ALL}https://gamestonkterminal.vercel.app\n"
        "\n"
        f"{Fore.YELLOW}Author:{Style.RESET_ALL} DidierRLopes\n"
        f"{Fore.YELLOW}Main Devs:{Style.RESET_ALL} jmaslek, aia\n"
        "\n"
        f"{Fore.YELLOW}Main Contributors:{Style.RESET_ALL}\n"
        f"{Fore.MAGENTA}Working towards a GUI using Qt:{Style.RESET_ALL} piiq, hinxx\n"
        f"{Fore.MAGENTA}Working on our landing page:{Style.RESET_ALL} jose-donato, crspy, martiaaz\n"
        f"{Fore.MAGENTA}Managing Twitter account:{Style.RESET_ALL} Meghan Hone\n"
        f"{Fore.MAGENTA}Responsible by developing Forex menu:{Style.RESET_ALL} alokan\n"
        f"{Fore.MAGENTA}Degiro's integration:{Style.RESET_ALL} Chavithra, Deel18\n"
        f"{Fore.MAGENTA}Preset screeners:{Style.RESET_ALL} Traceabl3\n"
        "\n"
        f"{Fore.YELLOW}Partnerships:{Style.RESET_ALL}\n"
        f"{Fore.CYAN}FinBrain: {Style.RESET_ALL}https://finbrain.tech\n"
        f"{Fore.CYAN}Quiver Quantitative: {Style.RESET_ALL}https://www.quiverquant.com\n"
        f"{Fore.CYAN}Ops.Syncretism: {Style.RESET_ALL}https://ops.syncretism.io/api.html\n"
        f"\n{Fore.RED}"
        "DISCLAIMER: Trading in financial instruments involves high risks including the risk of losing some, "
        "or all, of your investment amount, and may not be suitable for all investors. Before deciding to trade in "
        "financial instrument you should be fully informed of the risks and costs associated with trading the financial "
        "markets, carefully consider your investment objectives, level of experience, and risk appetite, and seek "
        "professional advice where needed. The data contained in Gamestonk Terminal (GST) is not necessarily accurate. "
        "GST and any provider of the data contained in this website will not accept liability for any loss or damage "
        "as a result of your trading, or your reliance on the information displayed."
        f"\n{Style.RESET_ALL}"
    )


def bootup():
    # Enable VT100 Escape Sequence for WINDOWS 10 Ver. 1607
    if sys.platform == "win32":
        os.system("")

    try:
        if os.name == "nt":
            # pylint: disable=E1101
            sys.stdin.reconfigure(encoding="utf-8")
            # pylint: disable=E1101
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception as e:
        print(e, "\n")

    # Print first welcome message and help
    print("\nWelcome to Gamestonk Terminal Beta")

    # The commit has was commented out because the terminal was crashing due to git import for multiple users
    # ({str(git.Repo('.').head.commit)[:7]})

    if gtff.ENABLE_THOUGHTS_DAY:
        print("-------------------")
        try:
            thought.get_thought_of_the_day()
        except Exception as e:
            print(e)
        print("")


def reset():
    """Resets the terminal.  Allows for checking code or keys without quitting"""
    print("resetting...")
    plt.close("all")
    completed_process = subprocess.run("python terminal.py", shell=True, check=False)
    if completed_process.returncode != 0:
        completed_process = subprocess.run(
            "python3 terminal.py", shell=True, check=False
        )
        if completed_process.returncode != 0:
            print("Unfortunately, resetting wasn't possible!\n")

    return completed_process.returncode
