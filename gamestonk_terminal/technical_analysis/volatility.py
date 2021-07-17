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


def bbands(l_args, s_ticker, s_interval, df_stock):
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="bbands",
        description="""
            Bollinger Bands consist of three lines. The middle band is a simple
            moving average (generally 20 periods) of the typical price (TP). The upper and lower
            bands are F standard deviations (generally 2) above and below the middle band.
            The bands widen and narrow when the volatility of the price is higher or lower,
            respectively. \n \nBollinger Bands do not, in themselves, generate buy or sell signals;
            they are an indicator of overbought or oversold conditions. When the price is near the
            upper or lower band it indicates that a reversal may be imminent. The middle band
            becomes a support or resistance level. The upper and lower bands can also be
            interpreted as price targets. When the price bounces off of the lower band and crosses
            the middle band, then the upper band becomes the price target.
        """,
    )

    parser.add_argument(
        "-l",
        "--length",
        action="store",
        dest="n_length",
        type=check_positive,
        default=5,
        help="length",
    )
    parser.add_argument(
        "-s",
        "--std",
        action="store",
        dest="n_std",
        type=check_positive,
        default=2,
        help="std",
    )
    parser.add_argument(
        "-m", "--mamode", action="store", dest="s_mamode", default="sma", help="mamode"
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
            df_ta = ta.bbands(
                close=df_stock["Adj Close"],
                length=ns_parser.n_length,
                std=ns_parser.n_std,
                mamode=ns_parser.s_mamode,
                offset=ns_parser.n_offset,
            ).dropna()

        # Intraday
        else:
            df_ta = ta.bbands(
                close=df_stock["Close"],
                length=ns_parser.n_length,
                std=ns_parser.n_std,
                mamode=ns_parser.s_mamode,
                offset=ns_parser.n_offset,
            ).dropna()

        plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)
        if s_ticker == "1440min":
            plt.plot(df_stock.index, df_stock["Adj Close"].values, color="k", lw=3)
        else:
            plt.plot(df_stock.index, df_stock["Close"].values, color="k", lw=3)
        plt.plot(df_ta.index, df_ta.iloc[:, 0].values, "r", lw=2)
        plt.plot(df_ta.index, df_ta.iloc[:, 1].values, "b", lw=1.5, ls="--")
        plt.plot(df_ta.index, df_ta.iloc[:, 2].values, "g", lw=2)
        plt.title(f"Bollinger Band (BBands) on {s_ticker}")
        plt.xlim(df_stock.index[0], df_stock.index[-1])
        plt.xlabel("Time")
        plt.ylabel("Share Price ($)")
        plt.legend([s_ticker, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
        plt.gca().fill_between(
            df_ta.index,
            df_ta.iloc[:, 0].values,
            df_ta.iloc[:, 2].values,
            alpha=0.1,
            color="b",
        )
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except Exception as e:
        print(e, "\n")
