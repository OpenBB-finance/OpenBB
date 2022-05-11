""" Finviz View """
__docformat__ = "numpy"


import io
import logging
from typing import List, Optional

import matplotlib.pyplot as plt
from PIL import Image

from openbb_terminal.config_terminal import theme
from openbb_terminal.config_plot import PLOT_DPI
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import plot_autoscale
from openbb_terminal.rich_config import console
from openbb_terminal.stocks.technical_analysis import finviz_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def view(ticker: str, external_axes: Optional[List[plt.Axes]] = None):
    """View finviz image for ticker

    Parameters
    ----------
    ticker : str
        Stock ticker
    external_axes : Optional[List[plt.Axes]], optional
        External axes (1 axis is expected in the list), by default None
    """

    image_data = finviz_model.get_finviz_image(ticker)
    dataBytesIO = io.BytesIO(image_data)
    im = Image.open(dataBytesIO)

    # This plot has 1 axis
    if not external_axes:
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    else:
        if len(external_axes) != 1:
            logger.error("Expected list of one axis item.")
            console.print("[red]Expected list of one axis item.\n[/red]")
            return
        (ax,) = external_axes

    ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)
    ax.imshow(im)
    # added for the watermark
    if not external_axes:
        theme.visualize_output()
