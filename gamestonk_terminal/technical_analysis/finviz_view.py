""" Finviz View """
__docformat__ = "numpy"

import argparse
import io
from typing import List
import requests
import matplotlib.pyplot as plt
from finvizfinance.quote import finvizfinance
from finvizfinance.util import headers
from PIL import Image

from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    plot_autoscale,
)
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff


def view(other_args: List[str], ticker: str):
    """View historical price with trendlines. [Source: Finviz]

    Parameters
    ----------
    other_args : List[str]
        argparse other args
    ticker: str
        stock ticker
    """
    parser = argparse.ArgumentParser(
        add_help=False,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="view",
        description="""
            View historical price with trendlines. [Source: Finviz]
        """,
    )

    try:
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        stock = finvizfinance(ticker)
        image_url = stock.TickerCharts(urlonly=True)

        r = requests.get(image_url, stream=True, headers=headers, timeout=5)
        r.raise_for_status()
        r.raw.decode_content = True

        dataBytesIO = io.BytesIO(r.content)
        im = Image.open(dataBytesIO)

        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax.set_axis_off()
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        if gtff.USE_ION:
            plt.ion()

        plt.imshow(im)
        plt.show()
        print("")

    except SystemExit:
        print("")
