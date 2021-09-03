"""Main helper"""
__docformat__ = "numpy"
import argparse
from datetime import datetime, timedelta
from typing import List

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import pyEX
import pytz
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from numpy.core.fromnumeric import transpose
from tabulate import tabulate

from gamestonk_terminal import config_plot as cfgPlot
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.common.technical_analysis import trendline_api as trend
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
    valid_date,
)

# pylint: disable=no-member,too-many-branches,C0302


def clear(
    other_args: List[str],
    s_ticker: str,
    s_start,
    s_interval: str,
    df_stock: pd.DataFrame,
):
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


def load(
    other_args: List[str],
    s_ticker: str,
    s_start,
    s_interval: str,
    df_stock: pd.DataFrame,
):
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
        default=(datetime.now() - timedelta(days=366)).strftime("%Y-%m-%d"),
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
        if other_args and "-t" not in other_args and "-h" not in other_args:
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

        elif ns_parser.source == "av":
            ts = TimeSeries(key=cfg.API_KEY_ALPHAVANTAGE, output_format="pandas")
            # pylint: disable=unbalanced-tuple-unpacking
            df_stock_candidate, _ = ts.get_intraday(
                symbol=ns_parser.s_ticker,
                outputsize="full",
                interval=str(ns_parser.n_interval) + "min",
            )

            df_stock_candidate.columns = [
                val.split(". ")[1].capitalize() for val in df_stock_candidate.columns
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

            new_index = []
            for idx in range(len(df_stock_candidate)):
                dt_time = datetime.strptime(df_stock_candidate.index[idx][1], "%H:%M")
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
    # TODO: Add option to customize plot even further

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
        if other_args and "-" not in other_args[0]:
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


def view(other_args: List[str], s_ticker: str, s_interval: str, df_stock: pd.DataFrame):
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


def plot_view_stock(df: pd.DataFrame, symbol: str, interval: str):
    """
    Plot the loaded stock dataframe
    Parameters
    ----------
    df: Dataframe
        Dataframe of prices and volumnes
    symbol: str
        Symbol of ticker
    interval: str
        Stock data resolution for plotting purposes

    """
    df.sort_index(ascending=True, inplace=True)
    bar_colors = ["r" if x[1].Open < x[1].Close else "g" for x in df.iterrows()]

    try:
        fig, ax = plt.subplots(
            2,
            1,
            gridspec_kw={"height_ratios": [3, 1]},
            figsize=plot_autoscale(),
            dpi=cfgPlot.PLOT_DPI,
        )
    except Exception as e:
        print(e)
        print(
            "Encountered an error trying to open a chart window. Check your X server configuration."
        )
        return

    # In order to make nice Volume plot, make the bar width = interval
    if interval == "1440min":
        bar_width = timedelta(days=1)
        title_string = "Daily"
    else:
        bar_width = timedelta(minutes=int(interval.split("m")[0]))
        title_string = f"{int(interval.split('m')[0])} min"

    ax[0].yaxis.tick_right()
    if "Adj Close" in df.columns:
        ax[0].plot(df.index, df["Adj Close"], c=cfgPlot.VIEW_COLOR)
    else:
        ax[0].plot(df.index, df["Close"], c=cfgPlot.VIEW_COLOR)
    ax[0].set_xlim(df.index[0], df.index[-1])
    ax[0].set_xticks([])
    ax[0].yaxis.set_label_position("right")
    ax[0].set_ylabel("Share Price ($)")
    ax[0].grid(axis="y", color="gainsboro", linestyle="-", linewidth=0.5)

    ax[0].spines["top"].set_visible(False)
    ax[0].spines["left"].set_visible(False)
    ax[1].bar(
        df.index, df.Volume / 1_000_000, color=bar_colors, alpha=0.8, width=bar_width
    )
    ax[1].set_xlim(df.index[0], df.index[-1])
    ax[1].yaxis.tick_right()
    ax[1].yaxis.set_label_position("right")
    ax[1].set_ylabel("Volume (1M)")
    ax[1].grid(axis="y", color="gainsboro", linestyle="-", linewidth=0.5)
    ax[1].spines["top"].set_visible(False)
    ax[1].spines["left"].set_visible(False)
    ax[1].set_xlabel("Time")
    fig.suptitle(
        symbol + " " + title_string,
        size=20,
        x=0.15,
        y=0.95,
        fontfamily="serif",
        fontstyle="italic",
    )
    if gtff.USE_ION:
        plt.ion()
    fig.tight_layout(pad=2)
    plt.setp(ax[1].get_xticklabels(), rotation=20, horizontalalignment="right")

    plt.show()
    print("")
