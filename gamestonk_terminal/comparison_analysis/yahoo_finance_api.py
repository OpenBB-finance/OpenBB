import argparse
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
    if (
        type_candles == "o"
        or type_candles == "h"
        or type_candles == "l"
        or type_candles == "c"
        or type_candles == "a"
    ):
        return type_candles
    raise argparse.ArgumentTypeError("The type of candles specified is not recognized")


def historical(l_args, df_stock, s_ticker, s_start, s_interval, similar):
    parser = argparse.ArgumentParser(
        add_help=False,
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
        if s_interval != "1440min":
            print("Intraday historical data analysis comparison is not yet available.")
            # Alpha Vantage only supports 5 calls per minute, we need another API to get intraday data
        else:
            ns_parser = parse_known_args_and_warn(parser, l_args)
            if not ns_parser:
                return

            if ns_parser.l_similar:
                similar = ns_parser.l_similar

            similar += ns_parser.l_also

            plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
            plt.title(f"Similar companies to {s_ticker}")
            df_stock = yf.download(s_ticker, start=s_start, progress=False, threads=False)
            plt.plot(
                df_stock.index, df_stock[d_candle_types[ns_parser.type_candle]].values
            )
            # plt.plot(df_stock.index, df_stock["5. adjusted close"].values, lw=2)
            l_min = [df_stock.index[0]]
            l_leg = [s_ticker]

            l_stocks = similar[:]

            while l_stocks:
                l_parsed_stocks = list()
                for symbol in l_stocks:
                    try:
                        df_similar_stock = yf.download(symbol, start=s_start, progress=False, threads=False)
                        if not df_similar_stock.empty:
                            plt.plot(
                                df_similar_stock.index,
                                df_similar_stock[d_candle_types[ns_parser.type_candle]].values,
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


def correlation(l_args, df_stock, s_ticker, s_start, s_interval, similar):
    parser = argparse.ArgumentParser(
        add_help=False,
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
        if s_interval != "1440min":
            print("Intraday historical data analysis comparison is not yet available.")
            # Alpha Vantage only supports 5 calls per minute, we need another API to get intraday data
        else:
            ns_parser = parse_known_args_and_warn(parser, l_args)
            if not ns_parser:
                return

            if ns_parser.l_similar:
                similar = ns_parser.l_similar

            similar += ns_parser.l_also

            if not similar:
                print("Provide at least a similar company for correlation")
            else:
                d_stock = {}
                d_stock[s_ticker] = yf.download(s_ticker, start=s_start, progress=False)
                l_min = [d_stock[s_ticker].index[0]]

                for symbol in similar:
                    d_stock[symbol] = yf.download(symbol, start=s_start, progress=False)
                    if not d_stock[symbol].empty:
                        l_min.append(d_stock[symbol].index[0])

                min_start_date = max(l_min)

                df_stock = d_stock[s_ticker][
                    d_candle_types[ns_parser.type_candle]
                ].rename(s_ticker)
                for symbol in d_stock:
                    if symbol != s_ticker:
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
