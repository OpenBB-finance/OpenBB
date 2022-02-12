import io

import matplotlib.pyplot as plt
from PIL import Image
import numpy as np

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.helpers import image_border
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.technical_analysis import finviz_model


def view_command(ticker=""):
    """Displays image from Finviz [Finviz]"""

    # Debug
    if cfg.DEBUG:
        logger.debug("!stocks.ta.view %s", ticker)

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")
    image_data = finviz_model.get_finviz_image(ticker)
    dataBytesIO = io.BytesIO(image_data)
    im = Image.open(dataBytesIO)

    fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
    ax.set_axis_off()
    fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

    plt.imshow(im)
    imagefile = f"ta_view.png{np.random.randint(70000)}"
    plt.savefig(imagefile)

    imagefile = image_border(imagefile)

    return {
        "title": f"Stocks: [Finviz] Trendlines & Data {ticker}",
        "imagefile": imagefile,
    }
