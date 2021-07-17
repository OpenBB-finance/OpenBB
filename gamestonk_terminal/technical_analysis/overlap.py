import argparse
import matplotlib.pyplot as plt
import pandas_ta as ta
from pandas.plotting import register_matplotlib_converters
from gamestonk_terminal.helper_funcs import (
    check_positive,
    parse_known_args_and_warn,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()


def ema(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="ema",
        description="""
            The Exponential Moving Average is a staple of technical
            analysis and is used in countless technical indicators. In a Simple Moving
            Average, each value in the time period carries equal weight, and values outside
            of the time period are not included in the average. However, the Exponential
            Moving Average is a cumulative calculation, including all data. Past values have
            a diminishing contribution to the average, while more recent values have a greater
            contribution. This method allows the moving average to be more responsive to changes
            in the data.
        """,
    )

    parser.add_argument(
        "-l",
        "--length",
        action="store",
        dest="n_length",
        type=check_positive,
        default=20,
        help="length",
    )
    parser.add_argument(
        "-o",
        "--offset",
        action="store",
        dest="n_offset",
        type=check_positive,
        default=0,
        help="offset",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)
        if not ns_parser:
            return

        # Daily
        if s_interval == "1440min":
            df_ta = ta.ema(
                df_stock["Adj Close"],
                length=ns_parser.n_length,
                offset=ns_parser.n_offset,
            ).dropna()

        # Intraday
        else:
            df_ta = ta.ema(
                df_stock["Close"],
                length=ns_parser.n_length,
                offset=ns_parser.n_offset,
            ).dropna()

        _, _ = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        plt.title(f"{ns_parser.n_length} EMA on {s_ticker}")
        if s_interval == "1440min":
            plt.plot(
                df_stock["Adj Close"].index,
                df_stock["Adj Close"].values,
                "k",
                lw=3,
            )
            plt.xlim(
                df_stock["Adj Close"].index[0],
                df_stock["Adj Close"].index[-1],
            )
        else:
            plt.plot(df_stock["Close"].index, df_stock["Close"].values, "k", lw=3)
            plt.xlim(df_stock["Close"].index[0], df_stock["Close"].index[-1])
        plt.xlabel("Time")
        plt.ylabel(f"Share Price of {s_ticker} ($)")
        plt.plot(df_ta.index, df_ta.values, c="tab:blue")
        l_legend = list()
        l_legend.append(s_ticker)
        # Pandas series
        if len(df_ta.shape) == 1:
            l_legend.append(f"{ns_parser.n_length} EMA")
        # Pandas dataframe
        else:
            l_legend.append(df_ta.columns.tolist())
        plt.legend(l_legend)
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e)
        print("")


def sma(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="sma",
        description="""
            Moving Averages are used to smooth the data in an array to
            help eliminate noise and identify trends. The Simple Moving Average is literally
            the simplest form of a moving average. Each output value is the average of the
            previous n values. In a Simple Moving Average, each value in the time period carries
            equal weight, and values outside of the time period are not included in the average.
            This makes it less responsive to recent changes in the data, which can be useful for
            filtering out those changes.
        """,
    )

    parser.add_argument(
        "-l",
        "--length",
        dest="l_length",
        type=lambda s: [int(item) for item in s.split(",")],
        default=[20, 50],
        help="length of MA window",
    )
    parser.add_argument(
        "-o",
        "--offset",
        action="store",
        dest="n_offset",
        type=check_positive,
        default=0,
        help="offset",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)
        if not ns_parser:
            return

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
        if s_interval == "1440min":
            plt.plot(df_stock.index, df_stock["Adj Close"].values, color="k")
        else:
            plt.plot(df_stock.index, df_stock["Close"].values, color="k")
        l_legend = list()
        l_legend.append(s_ticker)
        for length in ns_parser.l_length:
            if s_interval == "1440min":
                df_ta = ta.sma(
                    df_stock["Adj Close"],
                    length=length,
                    offset=ns_parser.n_offset,
                ).dropna()
            else:
                df_ta = ta.sma(
                    df_stock["Close"], length=length, offset=ns_parser.n_offset
                ).dropna()
            plt.plot(df_ta.index, df_ta.values)
            l_legend.append(f"{length} SMA")
        plt.title(f"SMA on {s_ticker}")
        plt.xlim(df_stock.index[0], df_stock.index[-1])
        plt.xlabel("Time")
        plt.ylabel("Share Price ($)")
        plt.legend(l_legend)
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e)
        print("")


def vwap(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="vwap",
        description="""
            The Volume Weighted Average Price that measures the average typical price
            by volume.  It is typically used with intraday charts to identify general direction.
        """,
    )

    parser.add_argument(
        "-o",
        "--offset",
        action="store",
        dest="n_offset",
        type=check_positive,
        default=0,
        help="offset",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)
        if not ns_parser:
            return

        # Daily
        if s_interval == "1440min":
            df_ta = ta.vwap(
                high=df_stock["High"],
                low=df_stock["Low"],
                close=df_stock["Adj Close"],
                volume=df_stock["Volume"],
                offset=ns_parser.n_offset,
            )

        # Intraday
        else:
            df_ta = ta.vwap(
                high=df_stock["High"],
                low=df_stock["Low"],
                close=df_stock["Close"],
                volume=df_stock["Volume"],
                offset=ns_parser.n_offset,
            )

        _, axPrice = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        if s_interval == "1440min":
            plt.plot(df_stock.index, df_stock["Adj Close"].values, color="k")
        else:
            plt.plot(df_stock.index, df_stock["Close"].values, color="k")
        plt.plot(df_ta.index, df_ta.values)
        plt.title(f"VWAP on {s_ticker}")
        plt.xlim(df_stock.index[0], df_stock.index[-1])
        plt.xlabel("Time")
        plt.ylabel("Share Price ($)")
        plt.legend([s_ticker, "VWAP"])
        _ = axPrice.twinx()

        if s_interval == "1440min":
            plt.bar(
                df_stock.index,
                df_stock["Volume"].values,
                color="k",
                alpha=0.8,
                width=0.3,
            )
        else:
            plt.bar(
                df_stock.index,
                df_stock["Volume"].values,
                color="k",
                alpha=0.8,
                width=0.3,
            )
        plt.ylabel("Volume")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e)
        print("")
