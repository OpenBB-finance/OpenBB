import io
import logging

from PIL import Image

from bots import config_discordbot as cfg
from bots.helpers import image_border
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.technical_analysis import finviz_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def view_command(ticker=""):
    """Displays image from Finviz [Finviz]"""

    # Debug
    if cfg.DEBUG:
        logger.debug("ta view %s", ticker)

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    image_data = finviz_model.get_finviz_image(ticker)
    dataBytesIO = io.BytesIO(image_data)
    im = Image.open(dataBytesIO)
    im = im.resize((800, 340), Image.ANTIALIAS)
    imagefile = "ta_view.png"

    im.save(dataBytesIO, "PNG", quality=100)
    dataBytesIO.seek(0)
    imagefile = image_border(imagefile, base64=dataBytesIO)
    im.close()

    return {
        "title": f"Stocks: [Finviz] Trendlines & Data {ticker.upper()}",
        "imagefile": imagefile,
    }
