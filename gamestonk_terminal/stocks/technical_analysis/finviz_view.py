""" Finviz View """
__docformat__ = "numpy"


import io
import matplotlib.pyplot as plt

from PIL import Image

from gamestonk_terminal.helper_funcs import (
    plot_autoscale,
)
from gamestonk_terminal.stocks.technical_analysis import finviz_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal import feature_flags as gtff


def view(ticker: str):
    """View finviz image for ticker

    Parameters
    ----------
    ticker : str
        Stock ticker
    """
    image_data = finviz_model.get_finviz_image(ticker)
    dataBytesIO = io.BytesIO(image_data)
    im = Image.open(dataBytesIO)

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    if gtff.USE_ION:
        plt.ion()

    plt.imshow(im)
    plt.show()
    print("")
