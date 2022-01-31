""" CNN View """
__docformat__ = "numpy"

import logging
import os

import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.economy import cnn_model
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def fear_and_greed_index(indicator: str, export: str):
    """Display CNN Fear And Greed Index. [Source: CNN Business]

    Parameters
    ----------
    indicator : str
        CNN Fear And Greed indicator or index. From Junk Bond Demand, Market Volatility,
        Put and Call Options, Market Momentum Stock Price Strength, Stock Price Breadth,
        Safe Heaven Demand, and Index.
    export : str
        Export plot to png,jpg,pdf file
    """
    fig = plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    report, im = cnn_model.get_feargreed_report(indicator, fig)

    console.print(report)

    if indicator:
        plt.imshow(im)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "feargreed",
    )

    if gtff.USE_ION:
        plt.ion()
    plt.show()
