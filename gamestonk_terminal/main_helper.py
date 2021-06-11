"""Main helper"""
__docformat__ = "numpy"
import argparse
from typing import List
from sys import stdout
import random
from datetime import datetime, timedelta
import subprocess
import hashlib
import matplotlib.pyplot as plt
from numpy.core.fromnumeric import transpose
import pandas as pd
from alpha_vantage.timeseries import TimeSeries
import mplfinance as mpf
import yfinance as yf
import pytz
from tabulate import tabulate

from gamestonk_terminal.helper_funcs import (
    valid_date,
    plot_view_stock,
    parse_known_args_and_warn,
    check_ohlc,
    lett_to_num,
    check_sources,
    plot_autoscale,
)

from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.technical_analysis import trendline_api as trend


def print_help(s_ticker, s_start, s_interval, b_is_market_open):
    """Print help"""
    print("What do you want to do?")
    print("   help        help to see this menu again")
    print("   update      update terminal from remote")
    print("   reset       reset terminal and reload configs")
    print("   quit        to abandon the program")
    print("")
    print("   clear       clear a specific stock ticker from analysis")
    print("   load        load a specific stock ticker for analysis")
    print("   quote       view the current price for a specific stock ticker")
    print("   candle      view a candle chart for a specific stock ticker")
    print("   view        view and load a specific stock ticker for technical analysis")
    if s_ticker:
        print(
            "   export      export the currently loaded dataframe to a file or stdout"
        )

    s_intraday = (f"Intraday {s_interval}", "Daily")[s_interval == "1440min"]
    if s_ticker and s_start:
        print(f"\n{s_intraday} Stock: {s_ticker} (from {s_start.strftime('%Y-%m-%d')})")
    elif s_ticker:
        print(f"\n{s_intraday} Stock: {s_ticker}")
    else:
        print("\nStock: ?")
    print(f"Market {('CLOSED', 'OPEN')[b_is_market_open]}.\n")

    print(
        "   > disc        discover trending stocks, \t e.g. map, sectors, high short interest"
    )
    print(
        "   > scr         screener stocks, \t\t e.g. overview/performance, using preset filters"
    )
    print("   > mill        papermill menu, \t\t menu to generate notebook reports")
    print("   > econ        economic data, \t\t e.g.: FRED, events")
    print(
        "   > pa          portfolio analysis, \t\t supports: robinhood, alpaca, ally "
    )
    print(
        "   > crypto      cryptocurrencies, \t\t from: coingecko, coinmarketcap, binance"
    )
    print(
        "   > po          portfolio optimization, \t optimal portfolio weights from pyportfolioopt"
    )
    print("   > gov         government menu, \t\t congress, senate, house trading")
    print("   > etf         etf menu, \t\t\t from: StockAnalysis.com")
    print("   > fx          forex menu, \t\t\t forex support through Oanda")
    print("   > rc          resource collection, \t\t e.g. hf letters")

    if s_ticker:
        print(
            "   > ba          behavioural analysis,    \t from: reddit, stocktwits, twitter, google"
        )
        print(
            "   > res         research web page,       \t e.g.: macroaxis, yahoo finance, fool"
        )
        print(
            "   > ca          comparison analysis,     \t e.g.: historical, correlation, financials"
        )
        print(
            "   > fa          fundamental analysis,    \t e.g.: income, balance, cash, earnings"
        )
        print(
            "   > ta          technical analysis,      \t e.g.: ema, macd, rsi, adx, bbands, obv"
        )
        print(
            "   > bt          strategy backtester,      \t e.g.: simple ema, ema cross, rsi strategies"
        )
        print(
            "   > dd          in-depth due-diligence,  \t e.g.: news, analyst, shorts, insider, sec"
        )
        print(
            "   > eda         exploratory data analysis,\t e.g.: decompose, cusum, residuals analysis"
        )
        print(
            "   > pred        prediction techniques,   \t e.g.: regression, arima, rnn, lstm, prophet"
        )
        print(
            "   > ra          residuals analysis,      \t e.g.: model fit, qqplot, hypothesis test"
        )
        print(
            "   > op          options info,            \t e.g.: volume and open interest"
        )
    print("")


def clear(other_args: List[str], s_ticker, s_start, s_interval, df_stock):
    """Clears loaded stock and returns empty variables"""
    parser = argparse.ArgumentParser(
        add_help=False,
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
    """
    Load selected ticker
    Parameters
    ----------
    other_args:List[str]
        Argparse arguments
    s_ticker: str
        Ticker
    s_start: str
        Start date
    s_interval: str
        Interval to get data for
    df_stock: pd.DataFrame
        Preloaded dataframe

    Returns
    -------
    ns_parser.s_ticker :
        Ticker
    s_start:
        Start date
    str(ns_parser.n_interval) + "min":
        Interval
    df_stock_candidate
        Dataframe loaded with close and volumes.

    """
    parser = argparse.ArgumentParser(
        add_help=False,
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
        required=True,
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
        type=check_sources,
        default="yf",
        help="Source of historical data. 'yf' and 'av' available.",
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
            if "-" not in other_args[0]:
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

                df_stock_candidate = df_stock_candidate.rename(
                    columns={
                        "Open": "1. open",
                        "High": "2. high",
                        "Low": "3. low",
                        "Close": "4. close",
                        "Adj Close": "5. adjusted close",
                        "Volume": "6. volume",
                    }
                )
                df_stock_candidate.index.name = "date"

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
                s_interval = s_int
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

                df_stock_candidate = df_stock_candidate.rename(
                    columns={
                        "Open": "1. open",
                        "High": "2. high",
                        "Low": "3. low",
                        "Close": "4. close",
                        "Adj Close": "5. adjusted close",
                        "Volume": "6. volume",
                    }
                )
                df_stock_candidate.index.name = "date"

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


def candle(s_ticker: str, s_start: str):
    df_stock = trend.load_ticker(s_ticker, s_start)
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
        title=f"\n{s_ticker} - Last 6 months",
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


def quote(other_args: List[str], s_ticker: str):
    parser = argparse.ArgumentParser(
        add_help=False,
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


def view(other_args: List[str], s_ticker: str, s_start, s_interval, df_stock):
    """
    Plot loaded ticker or load ticker and plot
    Parameters
    ----------
    other_args:List[str]
        Argparse arguments
    s_ticker: str
        Ticker to load
    s_start: str
        Start date
    s_interval: str
        Interval tto get data for
    df_stock: pd.Dataframe
        Preloaded dataframe to plot

    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="view",
        description="Visualize historical data of a stock. An alpha_vantage key is necessary.",
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
    parser.add_argument(
        "-s",
        "--start",
        type=valid_date,
        dest="s_start_date",
        default=s_start,
        help="The starting date (format YYYY-MM-DD) of the stock",
    )
    parser.add_argument(
        "-i",
        "--interval",
        action="store",
        dest="n_interval",
        type=int,
        default=0,
        choices=[1, 5, 15, 30, 60],
        help="Intraday stock minutes",
    )
    parser.add_argument(
        "--type",
        action="store",
        dest="type",
        type=check_ohlc,
        default="a",  # in case it's adjusted close
        help=(
            "ohlc corresponds to types: open; high; low; close; "
            "while oc corresponds to types: open; close"
        ),
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

    except SystemExit:
        print("")
        return

    # Update values:
    if ns_parser.s_ticker != s_ticker:
        if ns_parser.n_interval > 0:
            s_ticker, s_start, s_interval, df_stock = load(
                [
                    "-t",
                    ns_parser.s_ticker,
                    "-s",
                    ns_parser.s_start_date.strftime("%Y-%m-%d"),
                    "-i",
                    ns_parser.n_interval,
                ],
                s_ticker,
                s_start,
                s_interval,
                df_stock,
            )
        else:
            s_ticker, s_start, s_interval, df_stock = load(
                [
                    "-t",
                    ns_parser.s_ticker,
                    "-s",
                    ns_parser.s_start_date.strftime("%Y-%m-%d"),
                ],
                s_ticker,
                s_start,
                s_interval,
                df_stock,
            )

    # A new interval intraday period was given
    if ns_parser.n_interval != 0:
        s_interval = str(ns_parser.n_interval) + "min"

    type_candles = lett_to_num(ns_parser.type)

    df_stock.sort_index(ascending=True, inplace=True)

    # Daily
    if s_interval == "1440min":
        # The default doesn't exist for intradaily data
        ln_col_idx = [int(x) - 1 for x in list(type_candles)]
        # Check that the types given are not bigger than 4, as there are only 5 types (0-4)
        # pylint: disable=len-as-condition
        if len([i for i in ln_col_idx if i > 4]) > 0:
            print("An index bigger than 4 was given, which is wrong. Try again")
            return
        # Append last column of df to be filtered which corresponds to: 6. Volume
        ln_col_idx.append(5)
        # Slice dataframe from the starting date YYYY-MM-DD selected
        df_stock = df_stock[ns_parser.s_start_date :]
    # Intraday
    else:
        # The default doesn't exist for intradaily data
        # JM edit 6-7-21 -- It seems it does
        if ns_parser.type == "a":
            ln_col_idx = [4]
        else:
            ln_col_idx = [int(x) - 1 for x in list(type_candles)]

        # Append last column of df to be filtered which corresponds to: 5. Volume
        ln_col_idx.append(5)
        # Slice dataframe from the starting date YYYY-MM-DD selected
        df_stock = df_stock[ns_parser.s_start_date.strftime("%Y-%m-%d") :]

    # Plot view of the stock
    plot_view_stock(df_stock.iloc[:, ln_col_idx], ns_parser.s_ticker, s_interval)


def export(other_args: List[str], df_stock):
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="export",
        description="Exports the historical data from this ticker to a file or stdout.",
    )
    parser.add_argument(
        "-f",
        "--filename",
        type=str,
        dest="s_filename",
        default=stdout,
        help="Name of file to save the historical data exported (stdout if unspecified)",
    )
    parser.add_argument(
        "-F",
        "--format",
        dest="s_format",
        type=str,
        default="csv",
        help="Export historical data into following formats: csv, json, excel, clipboard",
    )
    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

    except SystemExit:
        print("")
        return

    if df_stock.empty:
        print("No data loaded yet to export.")
        return

    if ns_parser.s_format == "csv":
        df_stock.to_csv(ns_parser.s_filename)

    elif ns_parser.s_format == "json":
        df_stock.to_json(ns_parser.s_filename)

    elif ns_parser.s_format == "excel":
        df_stock.to_excel(ns_parser.s_filename)

    elif ns_parser.s_format == "clipboard":
        df_stock.to_clipboard()

    print("")


def print_goodbye():
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
