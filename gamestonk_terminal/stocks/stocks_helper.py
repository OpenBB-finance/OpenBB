"""Main helper"""
__docformat__ = "numpy"
import argparse
import json
import warnings
from datetime import datetime, timedelta
from typing import List, Union

import matplotlib.pyplot as plt
import mplfinance as mpf
import pandas as pd
import plotly.graph_objects as go
import pyEX
import pytz
import requests
import yfinance as yf
from alpha_vantage.timeseries import TimeSeries
from numpy.core.fromnumeric import transpose
from plotly.subplots import make_subplots
from scipy import stats
from tabulate import tabulate

from gamestonk_terminal import config_plot as cfgPlot
from gamestonk_terminal import config_terminal as cfg
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
    valid_date,
)

warnings.simplefilter("ignore")
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


def search(
    query: str,
    amount: int,
):
    """Search selected query for tickers.

    Parameters
    ----------
    query : str
        The search term used to find company tickers.
    amount : int
        The amount of companies shown.

    Returns
    -------
    tabulate
        Companies that match the query.
    """
    equities_list = (
        "https://raw.githubusercontent.com/JerBouma/FinanceDatabase/master/"
        "Database/Equities/Equities List.json"
    )
    request = requests.get(equities_list)
    equities = json.loads(request.text)

    equities_query = {
        key: value
        for key, value in equities.items()
        if (query in key.lower()) or (query in value.lower())
    }

    equities_dataframe = pd.DataFrame(
        equities_query.items(),
        index=equities_query.values(),
        columns=["Company", "Ticker"],
    )

    if equities_dataframe.empty:
        raise ValueError("No companies found. \n")

    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                equities_dataframe.iloc[:amount],
                showindex=False,
                headers=["Company", "Ticker"],
                tablefmt="fancy_grid",
            ),
            "\n",
        )
    else:
        print(equities_dataframe.iloc[:amount].to_string(), "\n")


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
        "-e",
        "--end",
        type=valid_date,
        default=datetime.now().strftime("%Y-%m-%d"),
        dest="s_end_date",
        help="The ending date (format YYYY-MM-DD) of the stock",
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

                df_stock_candidate.index = df_stock_candidate.index.tz_localize(None)

                # pylint: disable=no-member
                df_stock_candidate.sort_index(ascending=True, inplace=True)

                # Slice dataframe from the starting date YYYY-MM-DD selected
                df_stock_candidate = df_stock_candidate[
                    ns_parser.s_start_date : ns_parser.s_end_date
                ]

            # Yahoo Finance Source
            elif ns_parser.source == "yf":
                df_stock_candidate = yf.download(
                    ns_parser.s_ticker,
                    start=ns_parser.s_start_date,
                    end=ns_parser.s_end_date,
                    progress=False,
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
                df_stock_candidate = df_stock_candidate[
                    ns_parser.s_start_date : ns_parser.s_end_date
                ]

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
            df_stock_candidate = df_stock_candidate[
                ns_parser.s_start_date : ns_parser.s_end_date
            ]

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

            df_stock_candidate.index = df_stock_candidate.index.tz_localize(None)

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
            df_stock_candidate = df_stock_candidate[
                ns_parser.s_start_date : ns_parser.s_end_date
            ]

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


def display_candle(
    s_ticker: str, df_stock: pd.DataFrame, use_matplotlib: bool, intraday: bool = False
):
    """Shows candle plot of loaded ticker. [Source: Yahoo Finance, IEX Cloud or Alpha Vantage]

    Parameters
    ----------
    df_stock: pd.DataFrame
        Stock dataframe
    s_ticker: str
        Ticker name
    use_matplotlib: bool
        Flag to use matplotlib instead of interactive plotly chart
    intraday: bool
        Flag for intraday data for plotly range breaks
    """
    df_stock["ma20"] = df_stock["Close"].rolling(20).mean().fillna(method="bfill")
    df_stock["ma50"] = df_stock["Close"].rolling(50).mean().fillna(method="bfill")

    if (df_stock.index[1] - df_stock.index[0]).total_seconds() >= 86400:
        df_stock = find_trendline(df_stock, "OC_High", "high")
        df_stock = find_trendline(df_stock, "OC_Low", "low")

    if use_matplotlib:
        mc = mpf.make_marketcolors(
            up="green",
            down="red",
            edge="black",
            wick="black",
            volume="in",
            ohlc="i",
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
            title=f"\nStock {s_ticker}",
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
    else:
        fig = make_subplots(
            rows=2,
            cols=1,
            shared_xaxes=True,
            vertical_spacing=0.06,
            subplot_titles=(f"{s_ticker}", "Volume"),
            row_width=[0.2, 0.7],
        )
        fig.add_trace(
            go.Candlestick(
                x=df_stock.index,
                open=df_stock.Open,
                high=df_stock.High,
                low=df_stock.Low,
                close=df_stock.Close,
                name="OHLC",
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df_stock.index,
                y=df_stock["ma20"],
                name="MA20",
                mode="lines",
                line=go.scatter.Line(color="royalblue"),
            ),
            row=1,
            col=1,
        )
        fig.add_trace(
            go.Scatter(
                x=df_stock.index,
                y=df_stock["ma50"],
                name="MA50",
                mode="lines",
                line=go.scatter.Line(color="black"),
            ),
            row=1,
            col=1,
        )

        if "OC_High_trend" in df_stock.columns:
            fig.add_trace(
                go.Scatter(
                    x=df_stock.index,
                    y=df_stock["OC_High_trend"],
                    name="High Trend",
                    mode="lines",
                    line=go.scatter.Line(color="green"),
                ),
                row=1,
                col=1,
            )
        if "OC_Low_trend" in df_stock.columns:
            fig.add_trace(
                go.Scatter(
                    x=df_stock.index,
                    y=df_stock["OC_Low_trend"],
                    name="Low Trend",
                    mode="lines",
                    line=go.scatter.Line(color="red"),
                ),
                row=1,
                col=1,
            )

        fig.add_trace(
            go.Bar(
                x=df_stock.index,
                y=df_stock.Volume,
                name="Volume",
                marker_color="#696969",
            ),
            row=2,
            col=1,
        )
        fig.update_layout(
            yaxis_title="Stock Price ($)",
            xaxis=dict(
                rangeselector=dict(
                    buttons=list(
                        [
                            dict(
                                count=1,
                                label="1m",
                                step="month",
                                stepmode="backward",
                            ),
                            dict(
                                count=3,
                                label="3m",
                                step="month",
                                stepmode="backward",
                            ),
                            dict(count=1, label="YTD", step="year", stepmode="todate"),
                            dict(
                                count=1,
                                label="1y",
                                step="year",
                                stepmode="backward",
                            ),
                            dict(step="all"),
                        ]
                    )
                ),
                rangeslider=dict(visible=False),
                type="date",
            ),
        )
        if intraday:
            fig.update_xaxes(
                rangebreaks=[
                    dict(bounds=["sat", "mon"]),
                    dict(bounds=[16, 9.5], pattern="hour"),
                ]
            )

        fig.show()
    print("")


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

    # Price only option.
    parser.add_argument(
        "-p",
        "--price",
        action="store_true",
        dest="price_only",
        default=False,
        help="Price only",
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

    # If price only option, return immediate market price for ticker.
    if ns_parser.price_only:
        print(f"Price of {ns_parser.s_ticker} {ticker.info['regularMarketPrice']} \n")
        return

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

        quote_data = transpose(quote_df)

        print(
            tabulate(
                quote_data,
                headers=quote_data.columns,  # type: ignore
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


def load_ticker(
    ticker: str, start_date: Union[str, datetime], end_date: Union[str, datetime] = ""
) -> pd.DataFrame:
    """Loads a ticker data from Yahoo Finance, adds a data index column data_id and Open-Close High/Low columns.

    Parameters
    ----------
    ticker : str
        The stock ticker.
    start_date : Union[str,datetime]
        Start date to load stock ticker data formatted YYYY-MM-DD.
    end_date : Union[str,datetime]
        End date to load stock ticker data formatted YYYY-MM-DD.

    Returns
    -------
    DataFrame
        A Panda's data frame with columns Open, High, Low, Close, Adj Close, Volume, date_id, OC-High, OC-Low.
    """
    if end_date:
        df_data = yf.download(ticker, start=start_date, end=end_date, progress=False)
    else:
        df_data = yf.download(ticker, start=start_date, progress=False)

    df_data["date_id"] = (df_data.index.date - df_data.index.date.min()).astype(
        "timedelta64[D]"
    )
    df_data["date_id"] = df_data["date_id"].dt.days + 1

    df_data["OC_High"] = df_data[["Open", "Close"]].max(axis=1)
    df_data["OC_Low"] = df_data[["Open", "Close"]].min(axis=1)

    return df_data


def process_candle(df_data: pd.DataFrame) -> pd.DataFrame:
    """Process DataFrame into candle style plot

    Parameters
    ----------
    df_data : DataFrame
        Stock dataframe.

    Returns
    -------
    DataFrame
        A Panda's data frame with columns Open, High, Low, Close, Adj Close, Volume, date_id, OC-High, OC-Low.
    """
    df_data["date_id"] = (df_data.index.date - df_data.index.date.min()).astype(
        "timedelta64[D]"
    )
    df_data["date_id"] = df_data["date_id"].dt.days + 1

    df_data["OC_High"] = df_data[["Open", "Close"]].max(axis=1)
    df_data["OC_Low"] = df_data[["Open", "Close"]].min(axis=1)

    return df_data


def find_trendline(
    df_data: pd.DataFrame, y_key: str, high_low: str = "high"
) -> pd.DataFrame:
    """Attempts to find a trend line based on y_key column from a given stock ticker data frame.

    Parameters
    ----------
    df_data : DataFrame
        The stock ticker data frame with at least date_id, y_key columns.

    y_key : str
        Column name to base the trend line on.

    high_low: str, optional
        Either "high" or "low". High is the default.

    Returns
    -------
    DataFrame
        If a trend is successfully found,
            An updated Panda's data frame with a trend data {y_key}_trend column.
        If no trend was found,
            An original Panda's data frame
    """

    for iteration in [3, 4, 5, 6, 7]:
        df_temp = df_data.copy()
        while len(df_temp) > iteration:
            reg = stats.linregress(
                x=df_temp["date_id"],
                y=df_temp[y_key],
            )

            if high_low == "high":
                df_temp = df_temp.loc[
                    df_temp[y_key] > reg[0] * df_temp["date_id"] + reg[1]
                ]
            else:
                df_temp = df_temp.loc[
                    df_temp[y_key] < reg[0] * df_temp["date_id"] + reg[1]
                ]

        if len(df_temp) > 1:
            break

    if len(df_temp) == 1:
        return df_data

    reg = stats.linregress(
        x=df_temp["date_id"],
        y=df_temp[y_key],
    )

    df_data[f"{y_key}_trend"] = reg[0] * df_data["date_id"] + reg[1]

    return df_data
