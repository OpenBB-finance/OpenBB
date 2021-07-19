""" Comparison Analysis Yahoo Finance View """
__docformat__ = "numpy"

import argparse
from typing import List
from datetime import datetime
import numpy as np
import pandas as pd
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import yfinance as yf
import seaborn as sns

from gamestonk_terminal.helper_funcs import parse_known_args_and_warn, plot_autoscale
from gamestonk_terminal.config_plot import PLOT_DPI

register_matplotlib_converters()

d_candle_types = {
    "o": "Open",
    "h": "High",
    "l": "Low",
    "c": "Close",
    "a": "Adj Close",
}


def check_one_of_ohlca(type_candles: str) -> str:
    """Convert a candle type

    Parameters
    ----------
    type_candles : str
        OHLCA candle type

    Returns
    -------
    str
        Converted candle type

    Raises
    ------
    argparse.ArgumentTypeError
        Unknown candle type
    """

    if type_candles in ("o", "h", "l", "c", "a"):
        return type_candles

    raise argparse.ArgumentTypeError("The type of candles specified is not recognized")


def historical(
    other_args: List[str],
    df_stock: pd.DataFrame,
    ticker: str,
    start: datetime,
    interval: str,
    similar: List[str],
):
    """Display historical data from Yahoo Finance

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    df_stock : pd.DataFrame
        Stock data
    ticker : str
        Ticker symbol
    start : datetime
        Time start
    interval : str
        Time interval
    similar : List[str]
        List of similar tickers
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="historical",
        description="""Historical price comparison between similar companies [Source: Yahoo Finance]
        """,
    )
    parser.add_argument(
        "-s",
        "--similar",
        dest="l_similar",
        type=lambda s: [str(item) for item in s.split(",")],
        default=[],
        help="similar companies to compare with.",
    )
    parser.add_argument(
        "-a",
        "--also",
        dest="l_also",
        type=lambda s: [str(item) for item in s.split(",")],
        default=[],
        help="apart from loaded similar companies also compare with.",
    )
    parser.add_argument(
        "-t",
        "--type",
        action="store",
        dest="type_candle",
        type=check_one_of_ohlca,
        default="a",  # in case it's adjusted close
        help=("type of candles: o-open, h-high, l-low, c-close, a-adjusted close."),
    )

    try:
        if interval != "1440min":
            print("Intraday historical data analysis comparison is not yet available.")
            # Alpha Vantage only supports 5 calls per minute, we need another API to get intraday data
        else:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            if ns_parser.l_similar:
                similar = ns_parser.l_similar

            similar += ns_parser.l_also

            plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
            plt.title(f"Similar companies to {ticker}")
            df_stock = yf.download(ticker, start=start, progress=False, threads=False)
            plt.plot(
                df_stock.index, df_stock[d_candle_types[ns_parser.type_candle]].values
            )
            # plt.plot(df_stock.index, df_stock["Adj Close"].values, lw=2)
            l_min = [df_stock.index[0]]
            l_leg = [ticker]

            l_stocks = similar[:]

            while l_stocks:
                l_parsed_stocks = list()
                for symbol in l_stocks:
                    try:
                        df_similar_stock = yf.download(
                            symbol, start=start, progress=False, threads=False
                        )
                        if not df_similar_stock.empty:
                            plt.plot(
                                df_similar_stock.index,
                                df_similar_stock[
                                    d_candle_types[ns_parser.type_candle]
                                ].values,
                            )
                            l_min.append(df_similar_stock.index[0])
                            l_leg.append(symbol)

                        l_parsed_stocks.append(symbol)
                    except Exception as e:
                        print("")
                        print(e)
                        print(
                            "Disregard previous error, which is due to API Rate limits from Yahoo Finance."
                        )
                        print(
                            f"Because we like '{symbol}', and we won't leave without getting data from it."
                        )

                for parsed_stock in l_parsed_stocks:
                    l_stocks.remove(parsed_stock)

            plt.xlabel("Time")
            plt.ylabel("Share Price ($)")
            plt.legend(l_leg)
            plt.grid(b=True, which="major", color="#666666", linestyle="-")
            plt.minorticks_on()
            plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
            # ensures that the historical data starts from same datapoint
            plt.xlim([max(l_min), df_stock.index[-1]])
            plt.show()
        print("")

    except SystemExit:
        print("Similar companies need to be provided", "\n")
    except Exception as e:
        print(e, "\n")


def correlation(other_args, df_stock, ticker, start, interval, similar):
    """
    Correlation heatmap based on historical price comparison
    between similar companies. [Source: Yahoo Finance]

    Parameters
    ----------
    other_args : [type]
        Command line arguments to be processed with argparse
    df_stock : pd.DataFrame
        Stock data
    ticker : str
        Ticker symbol
    start : datetime
        Time start
    interval : str
        Time interval
    similar : [type]
        List of similar tickers
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="corr",
        description=""" Correlation heatmap based on historical price comparison between similar
        companies. [Source: Yahoo Finance]
        """,
    )
    parser.add_argument(
        "-s",
        "--similar",
        dest="l_similar",
        type=lambda s: [str(item) for item in s.split(",")],
        default=[],
        help="similar companies to compare with.",
    )
    parser.add_argument(
        "-a",
        "--also",
        dest="l_also",
        type=lambda s: [str(item) for item in s.split(",")],
        default=[],
        help="apart from loaded similar companies also compare with.",
    )
    parser.add_argument(
        "-t",
        "--type",
        action="store",
        dest="type_candle",
        type=check_one_of_ohlca,
        default="a",  # in case it's adjusted close
        help=("type of data: o-open, h-high, l-low, c-close, a-adjusted close"),
    )

    try:
        if interval != "1440min":
            print("Intraday historical data analysis comparison is not yet available.")
            # Alpha Vantage only supports 5 calls per minute, we need another API to get intraday data
        else:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            if ns_parser.l_similar:
                similar = ns_parser.l_similar

            similar += ns_parser.l_also

            if not similar:
                print("Provide at least a similar company for correlation")
            else:
                d_stock = {}
                d_stock[ticker] = yf.download(ticker, start=start, progress=False)
                l_min = [d_stock[ticker].index[0]]

                for symbol in similar:
                    d_stock[symbol] = yf.download(symbol, start=start, progress=False)
                    if not d_stock[symbol].empty:
                        l_min.append(d_stock[symbol].index[0])

                min_start_date = max(l_min)

                df_stock = d_stock[ticker][
                    d_candle_types[ns_parser.type_candle]
                ].rename(ticker)
                for symbol in d_stock.items():
                    if symbol != ticker:
                        if not d_stock[symbol].empty:
                            df_stock = pd.concat(
                                [
                                    df_stock,
                                    d_stock[symbol][
                                        d_candle_types[ns_parser.type_candle]
                                    ].rename(symbol),
                                ],
                                axis=1,
                            )

                mask = np.zeros((df_stock.shape[1], df_stock.shape[1]), dtype=bool)
                mask[np.triu_indices(len(mask))] = True

                sns.heatmap(
                    df_stock[min_start_date:].corr(),
                    cbar_kws={"ticks": [-1.0, -0.5, 0.0, 0.5, 1.0]},
                    cmap="RdYlGn",
                    linewidths=1,
                    annot=True,
                    vmin=-1,
                    vmax=1,
                    mask=mask,
                )
                plt.title("Correlation Heatmap")
                plt.show()
        print("")

    except SystemExit:
        print("Similar companies need to be provided", "\n")
    except Exception as e:
        print(e, "\n")
