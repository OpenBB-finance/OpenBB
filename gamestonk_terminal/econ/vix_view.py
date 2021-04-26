""" VIX View """
__docformat__ = "numpy"
import argparse

from typing import List
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
import yfinance as yf
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    valid_date,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()


def view_vix(other_args: List[str]):
    """
    Plot vix from a starting date using yfinance
    Parameters
    ----------
    other_args: List[str]
        List of argparse arguments
    Returns
    -------
    Plots VIX historical data
    """
    parser = argparse.ArgumentParser(prog="vix_plot", add_help=False)
    parser.add_argument(
        "-s",
        "--start",
        type=valid_date,
        default="2020-01-01",
        dest="start_date",
        help="The starting date (format YYYY-MM-DD) of the plot",
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        vix = yf.download("^VIX", start=ns_parser.start_date, progress=False)
        _, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        vix.plot(y="Adj Close", ax=ax)
        plt.ylabel("VIX")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.minorticks_on()
        plt.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        plt.title("Historical VIX Data")

        print("")

        if gtff.USE_ION:
            plt.ion()
        plt.show()

    except Exception as e:
        print(e)
        print("")
