""" Fred View """
__docformat__ = "numpy"

import argparse
from typing import List
from fear_greed_index.CNNFearAndGreedIndex import CNNFearAndGreedIndex
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff

register_matplotlib_converters()


def fear_and_greed_index(other_args: List[str]):
    """Display CNN Fear And Greed Index.

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    """

    parser = argparse.ArgumentParser(
        add_help=False,
        prog="feargreed",
        description="""
            Display CNN Fear And Greed Index from https://money.cnn.com/data/fear-and-greed/.
        """,
    )

    parser.add_argument(
        "-i",
        "--indicator",
        dest="indicator",
        required=False,
        type=str,
        choices=["jbd", "mv", "pco", "mm", "sps", "spb", "shd", "index"],
        help="""
            CNN Fear And Greed indicator or index. From Junk Bond Demand, Market Volatility,
            Put and Call Options, Market Momentum Stock Price Strength, Stock Price Breadth,
            Safe Heaven Demand, and Index.
        """,
    )

    try:
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-i")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        cnn_fg = CNNFearAndGreedIndex()

        fig = plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

        if ns_parser.indicator:
            if ns_parser.indicator == "index":
                print(cnn_fg.index_summary)

                im = cnn_fg.index_chart
                plt.imshow(im)

            else:
                d_indicator_match = {
                    "jbd": "Junk Bond Demand",
                    "mv": "Market Volatility",
                    "pco": "Put and Call Options",
                    "mm": "Market Momentum",
                    "sps": "Stock Price Strength",
                    "spb": "Stock Price Breadth",
                    "shd": "Safe Heaven Demand",
                }
                indicator_name = d_indicator_match[ns_parser.indicator]

                for indicator in cnn_fg.all_indicators:
                    if indicator_name == indicator.type_indicator:
                        print(indicator.get_report())
                        im = indicator.chart
                        plt.imshow(im)

        else:
            # print Fear and Greed complete report
            print(cnn_fg.get_complete_report())

            # plot Fear and Greed charts
            cnn_fg.plot_all_charts(fig)

        if gtff.USE_ION:
            plt.ion()

        plt.show()
        print("")

    except SystemExit:
        print("")
    except Exception as e:
        print(e, "\n")
        return
