import io

from PIL import Image
import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.helpers import image_border
from gamestonk_terminal.stocks.technical_analysis import finviz_model


def view_command(ticker=""):
    """Displays image from Finviz [Finviz]"""

    # Debug
    if cfg.DEBUG:
        logger.debug("ta-view %s", ticker)

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    image_data = finviz_model.get_finviz_image(ticker)
    dataBytesIO = io.BytesIO(image_data)
    im = Image.open(dataBytesIO)
    im = im.resize((800, 340), Image.ANTIALIAS)
    imagefile = "ta_view.png"

    im.save(imagefile, "PNG", quality=100)
    imagefile = image_border(imagefile)

    return {
        "title": f"Stocks: [Finviz] Trendlines & Data {ticker}",
        "imagefile": imagefile,
    }
