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


def ad(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="ad",
        description="""
            The Accumulation/Distribution Line is similar to the On Balance
            Volume (OBV), which sums the volume times +1/-1 based on whether the close is
            higher than the previous close. The Accumulation/Distribution indicator, however
            multiplies the volume by the close location value (CLV). The CLV is based on the
            movement of the issue within a single bar and can be +1, -1 or zero. \n \n
            The Accumulation/Distribution Line is interpreted by looking for a divergence in
            the direction of the indicator relative to price. If the Accumulation/Distribution
            Line is trending upward it indicates that the price may follow. Also, if the
            Accumulation/Distribution Line becomes flat while the price is still rising (or falling)
            then it signals an impending flattening of the price.
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
    parser.add_argument(
        "--open",
        action="store_true",
        default=False,
        dest="b_use_open",
        help="uses open value of stock",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, l_args)
        if not ns_parser:
            return

        # Daily
        if s_interval == "1440min":
            # Use open stock values
            if ns_parser.b_use_open:
                df_ta = ta.ad(
                    high=df_stock["High"],
                    low=df_stock["Low"],
                    close=df_stock["Adj Close"],
                    volume=df_stock["Volume"],
                    offset=ns_parser.n_offset,
                    open_=df_stock["Open"],
                ).dropna()
            # Do not use open stock values
            else:
                df_ta = ta.ad(
                    high=df_stock["High"],
                    low=df_stock["Low"],
                    close=df_stock["Adj Close"],
                    volume=df_stock["Volume"],
                    offset=ns_parser.n_offset,
                ).dropna()

        # Intraday
        else:
            # Use open stock values
            if ns_parser.b_use_open:
                df_ta = ta.ad(
                    high=df_stock["High"],
                    low=df_stock["Low"],
                    close=df_stock["Close"],
                    volume=df_stock["Volume"],
                    offset=ns_parser.n_offset,
                    open_=df_stock["Open"],
                ).dropna()
            # Do not use open stock values
            else:
                df_ta = ta.ad(
                    high=df_stock["High"],
                    low=df_stock["Low"],
                    close=df_stock["Close"],
                    volume=df_stock["Volume"],
                    offset=ns_parser.n_offset,
                ).dropna()

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
        axPrice = plt.subplot(211)
        if s_interval == "1440min":
            plt.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)
        else:
            plt.plot(df_stock.index, df_stock["Close"].values, "k", lw=2)
        plt.title(f"Accumulation/Distribution Line (AD) on {s_ticker}")
        plt.xlim(df_stock.index[0], df_stock.index[-1])
        plt.ylabel("Share Price ($)")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
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
        plt.subplot(212)
        plt.plot(df_ta.index, df_ta.values, "b", lw=1)
        plt.xlim(df_stock.index[0], df_stock.index[-1])
        plt.axhline(0, linewidth=2, color="k", ls="--")
        plt.legend(["Chaikin Oscillator"])
        plt.xlabel("Time")
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
        return


def obv(l_args, s_ticker, s_interval, df_stock):
    """Technical Analysis with On-Balance Volume indicator"""
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="obv",
        description="""
            The On Balance Volume (OBV) is a cumulative total of the up and
            down volume. When the close is higher than the previous close, the volume is added
            to the running total, and when the close is lower than the previous close, the volume
            is subtracted from the running total. \n \n To interpret the OBV, look for the OBV
            to move with the price or precede price moves. If the price moves before the OBV,
            then it is a non-confirmed move. A series of rising peaks, or falling troughs, in the
            OBV indicates a strong trend. If the OBV is flat, then the market is not trending.
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
            df_ta = ta.obv(
                close=df_stock["Adj Close"],
                volume=df_stock["Volume"],
                offset=ns_parser.n_offset,
            ).dropna()

        # Intraday
        else:
            df_ta = ta.obv(
                close=df_stock["Close"],
                volume=df_stock["Volume"],
                offset=ns_parser.n_offset,
            ).dropna()

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
        axPrice = plt.subplot(211)
        if s_interval == "1440min":
            plt.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)
        else:
            plt.plot(df_stock.index, df_stock["Close"].values, "k", lw=2)
        plt.title(f"On-Balance Volume (OBV) on {s_ticker}")
        plt.xlim(df_stock.index[0], df_stock.index[-1])
        plt.ylabel("Share Price ($)")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
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
        plt.subplot(212)
        plt.plot(df_ta.index, df_ta.values, "b", lw=1)
        plt.xlim(df_stock.index[0], df_stock.index[-1])
        plt.legend(["OBV"])
        plt.xlabel("Time")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
