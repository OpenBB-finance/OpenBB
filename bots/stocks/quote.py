import logging

from bots import imps
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def quote_command(ticker: str = None):
    """Ticker Quote"""

    # Debug
    if imps.DEBUG:
        logger.debug("quote %s", ticker)

    # Check for argument
    if ticker is None:
        raise Exception("Stock ticker is required")

    df = imps.quote(ticker)
    fig = imps.plot_df(
        df,
        fig_size=(600, 1500),
        col_width=[2, 3],
        tbl_header=imps.PLT_TBL_HEADER,
        tbl_cells=imps.PLT_TBL_CELLS,
        font=imps.PLT_TBL_FONT,
        row_fill_color=imps.PLT_TBL_ROW_COLORS,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    fig.update_traces(cells=(dict(align="left")))
    imagefile = imps.save_image("quote.png", fig)

    return {
        "title": f"{ticker.upper()} Quote",
        "imagefile": imagefile,
    }
