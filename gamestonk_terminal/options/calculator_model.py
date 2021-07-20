"""Calculator Model"""
___docformat__ = "numpy"

import argparse
from typing import List

import numpy as np
from matplotlib import pyplot as plt

from gamestonk_terminal.helper_funcs import parse_known_args_and_warn, plot_autoscale
from gamestonk_terminal import config_plot as cfp
from gamestonk_terminal import feature_flags as gtff


def pnl_calculator(other_args: List[str]):
    """Plot profit/loss for different option variables

    Parameters
    ----------
    other_args: List[str]
        Argparse arguments
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="calc",
        description="Calculate profit or loss for given option settings.",
    )

    parser.add_argument(
        "--put",
        action="store_true",
        default=False,
        dest="put",
        help="Flag to calculate put option",
    )

    parser.add_argument(
        "-s",
        "--strike",
        type=float,
        dest="strike",
        help="Option strike price",
        default=10,
    )

    parser.add_argument(
        "-p", "--premium", type=float, dest="premium", help="Premium price", default=1
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        strike = ns_parser.strike
        premium = ns_parser.premium

        price_at_expiry = np.linspace(ns_parser.strike / 2, 1.5 * ns_parser.strike, 301)

        if ns_parser.put:
            break_even = strike - premium
            pnl = strike - premium - price_at_expiry
            pnl = 100 * np.where(price_at_expiry < strike, pnl, -premium)

        else:
            break_even = strike + premium
            pnl = price_at_expiry - strike - premium
            pnl = 100 * np.where(price_at_expiry > strike, pnl, -premium)

        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)
        ax.plot(price_at_expiry, pnl, alpha=0.1, c="k")
        ax.fill_between(
            price_at_expiry, 0, pnl, where=(pnl > 0), facecolor="green", alpha=0.5
        )
        ax.fill_between(
            price_at_expiry, 0, pnl, where=(pnl < 0), facecolor="red", alpha=0.5
        )
        ax.axvline(x=break_even, c="black")
        ax.set_xlabel("Price at Expiry")
        ax.set_ylabel("Profit")
        ax.set_title(f"Profit for {['Call', 'Put'][ns_parser.put]} option")
        ax.grid("on")

        if gtff.USE_ION:
            plt.ion()

        fig.tight_layout(pad=1)
        plt.show()
        print(f"Strike: ${strike}")
        print(f"Premium: ${premium}")
        print(f"Breakeven price: ${break_even}")
        print(f"Max loss is: ${-100*premium}")
        print("")

    except Exception as e:
        print(e, "\n")
        return

    except SystemExit:
        return
