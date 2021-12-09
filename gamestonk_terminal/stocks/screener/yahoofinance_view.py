"""Yahoo Finance View"""
__docformat__ = "numpy"
import argparse
import configparser
import datetime
import os
import random
from typing import List

from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import yfinance as yf
from finvizfinance.screener import ticker
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
    valid_date,
)
from gamestonk_terminal.stocks.screener import finviz_model

register_matplotlib_converters()

presets_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), "presets/")

d_candle_types = {
    "o": "Open",
    "h": "High",
    "l": "Low",
    "c": "Close",
    "a": "Adj Close",
}


def check_one_of_ohlca(type_candles: str) -> str:
    if type_candles in ("o", "h", "l", "c", "a"):
        return type_candles
    raise argparse.ArgumentTypeError("The type of candles specified is not recognized")


def historical(other_args: List[str], preset_loaded: str) -> List[str]:
    """View historical price of stocks that meet preset

    Parameters
    ----------
    other_args : List[str]
        Command line arguments to be processed with argparse
    ticker : str
        Loaded preset filter

    Returns
    -------
    List[str]
        List of stocks that meet preset criteria
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        prog="historical",
        description="""Historical price comparison between similar companies [Source: Yahoo Finance]
        """,
    )
    parser.add_argument(
        "--start",
        type=valid_date,
        default=datetime.datetime.now() - datetime.timedelta(days=6 * 30),
        dest="start",
        help="The starting date (format YYYY-MM-DD) of the historical price to plot",
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return list()

        screen = ticker.Ticker()
        if preset_loaded in finviz_model.d_signals:
            screen.set_filter(signal=finviz_model.d_signals[preset_loaded])

        else:
            preset_filter = configparser.RawConfigParser()
            preset_filter.optionxform = str  # type: ignore
            preset_filter.read(presets_path + preset_loaded + ".ini")

            d_general = preset_filter["General"]
            d_filters = {
                **preset_filter["Descriptive"],
                **preset_filter["Fundamental"],
                **preset_filter["Technical"],
            }

            d_filters = {k: v for k, v in d_filters.items() if v}

            if d_general["Signal"]:
                screen.set_filter(filters_dict=d_filters, signal=d_general["Signal"])
            else:
                screen.set_filter(filters_dict=d_filters)

        l_min = []
        l_leg = []
        l_stocks = screen.ScreenerView(verbose=0)
        limit_random_stocks = False

        if len(l_stocks) > 10:
            print(
                "\nThe limit of stocks to compare with are 10. Hence, 10 random similar stocks will be displayed.",
                "\nThe selected list will be:",
            )
            random.shuffle(l_stocks)
            l_stocks = sorted(l_stocks[:10])
            print(", ".join(l_stocks))
            limit_random_stocks = True

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        while l_stocks:
            l_parsed_stocks = []
            for symbol in l_stocks:
                try:
                    df_similar_stock = yf.download(
                        symbol,
                        start=datetime.datetime.strftime(ns_parser.start, "%Y-%m-%d"),
                        progress=False,
                        threads=False,
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

        if limit_random_stocks:
            plt.title(
                f"Screener Historical Price using {preset_loaded} on 10 of those stocks"
            )
        else:
            plt.title(f"Screener Historical Price using {preset_loaded}")

        plt.xlabel("Time")
        plt.ylabel("Share Price ($)")
        plt.legend(l_leg)
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        # ensures that the historical data starts from same datapoint
        plt.xlim([max(l_min), df_similar_stock.index[-1]])

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")
        return l_parsed_stocks

    except SystemExit:
        print("Similar companies need to be provided", "\n")
        return []
    except Exception as e:
        print(e, "\n")
        return []
