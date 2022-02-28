""" CNN View """
__docformat__ = "numpy"

from typing import Optional, List
import logging
import os

import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters

from gamestonk_terminal.config_terminal import theme
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.economy import cnn_model
from gamestonk_terminal.helper_funcs import export_data, plot_autoscale
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()


@log_start_end(log=logger)
def fear_and_greed_index(
    indicator: str, export: str, external_axes: Optional[List[plt.Axes]] = None
):
    """Display CNN Fear And Greed Index. [Source: CNN Business]

    Parameters
    ----------
    indicator : str
        CNN Fear And Greed indicator or index. From Junk Bond Demand, Market Volatility,
        Put and Call Options, Market Momentum Stock Price Strength, Stock Price Breadth,
        Safe Heaven Demand, and Index.
    export : str
        Export plot to png,jpg,pdf file
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """
    if external_axes is None:
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of 1 axis item./n[/red]")
            return
        (ax,) = external_axes

    report, im = cnn_model.get_feargreed_report(indicator, fig)

    console.print(report)

    # TODO: Reformat to new layout?
    theme.style_primary_axis(ax)
    if external_axes is None:
        theme.visualize_output()
    if indicator:
        ax.imshow(im)

    export_data(
        export,
        os.path.dirname(os.path.abspath(__file__)),
        "feargreed",
    )
