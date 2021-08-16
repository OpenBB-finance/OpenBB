""" CNN View """
__docformat__ = "numpy"

import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.economy import cnn_model
from gamestonk_terminal.helper_funcs import plot_autoscale

register_matplotlib_converters()


def fear_and_greed_index(indicator: str):
    """Display CNN Fear And Greed Index.

    Parameters
    ----------
    indicator : str
        CNN Fear And Greed indicator or index. From Junk Bond Demand, Market Volatility,
        Put and Call Options, Market Momentum Stock Price Strength, Stock Price Breadth,
        Safe Heaven Demand, and Index.
    """
    fig = plt.figure(figsize=plot_autoscale(), dpi=PLOT_DPI)

    report, im = cnn_model.get_feargreed_report(indicator, fig)

    print(report)

    if indicator:
        plt.imshow(im)

    if gtff.USE_ION:
        plt.ion()
    plt.show()
