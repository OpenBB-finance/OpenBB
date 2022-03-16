import logging

import df2img

import bots.config_discordbot as cfg
from bots.helpers import quote, save_image
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
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
        row_fill_color=cfg.PLT_TBL_ROW_COLORS,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    fig.update_traces(cells=(dict(align="left")))
    imagefile = save_image("quote.png", fig)

    return {
        "title": f"{ticker.upper()} Quote",
        "imagefile": imagefile,
    }
