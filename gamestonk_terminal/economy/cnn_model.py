""" CNN Model """
__docformat__ = "numpy"

from typing import Tuple
from fear_greed_index.CNNFearAndGreedIndex import CNNFearAndGreedIndex
from pandas.plotting import register_matplotlib_converters
import matplotlib.pyplot as plt

register_matplotlib_converters()


def get_feargreed_report(indicator: str, fig: plt.figure) -> Tuple[str, plt.figure]:
    """Display CNN Fear And Greed Index.

    Parameters
    ----------
    indicator : str
        CNN Fear And Greed indicator or index. From Junk Bond Demand, Market Volatility,
        Put and Call Options, Market Momentum Stock Price Strength, Stock Price Breadth,
        Safe Heaven Demand, and Index.
    plt.figure
        matplotlib figure initialized if indicator 'all' is selected

    Returns
    ----------
    str
        String output with respect to indicator chosen
    plt.figure
        matplotlib figure with indicator
    """
    cnn_fg = CNNFearAndGreedIndex()

    if indicator:
        if indicator == "index":
            return cnn_fg.index_summary, cnn_fg.index_chart

        d_indicator_match = {
            "jbd": "Junk Bond Demand",
            "mv": "Market Volatility",
            "pco": "Put and Call Options",
            "mm": "Market Momentum",
            "sps": "Stock Price Strength",
            "spb": "Stock Price Breadth",
            "shd": "Safe Heaven Demand",
        }
        indicator_name = d_indicator_match[indicator]

        for ind in cnn_fg.all_indicators:
            if indicator_name == ind.type_indicator:
                return ind.get_report(), ind.chart

        return "", plt.figure()

    return cnn_fg.get_complete_report(), cnn_fg.plot_all_charts(fig)
