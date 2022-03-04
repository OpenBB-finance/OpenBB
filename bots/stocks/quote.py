import df2img

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.helpers import quote, save_image


def quote_command(ticker: str = None):
    """Ticker Quote"""

    # Debug
    if cfg.DEBUG:
        logger.debug("quote %s", ticker)

    # Check for argument
    if ticker is None:
        raise Exception("Stock ticker is required")

    df = quote(ticker)
    fig = df2img.plot_dataframe(
        df,
        fig_size=(600, 1500),
        col_width=[2, 3],
        tbl_header=cfg.PLT_TBL_HEADER,
        tbl_cells=cfg.PLT_TBL_CELLS,
        font=cfg.PLT_TBL_FONT,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    fig.update_traces(cells=(dict(align="left")))
    imagefile = save_image("quote.png", fig)

    return {
        "title": f"{ticker.upper()} Quote",
        "imagefile": imagefile,
    }
