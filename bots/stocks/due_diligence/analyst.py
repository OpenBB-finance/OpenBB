import logging

import df2img
import numpy as np

import bots.config_discordbot as cfg
from bots.helpers import save_image
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.due_diligence import finviz_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def analyst_command(ticker=""):
    """Displays analyst recommendations [Finviz]"""

    # Debug
    if cfg.DEBUG:
        logger.debug("dd analyst %s", ticker)

    # Check for argument
    if not ticker:
        raise Exception("Stock ticker is required")

    df = finviz_model.get_analyst_data(ticker)
    df = df.replace(np.nan, 0)
    df.index.names = ["Date"]
    df = df.rename(
        columns={
            "category": "Category",
            "analyst": "Analyst",
            "rating": "Rating",
            "target": "Target",
            "target_from": "Target From",
            "target_to": "Target To",
        }
    )

    dindex = len(df.index)
    fig = df2img.plot_dataframe(
        df,
        fig_size=(900, (40 + (40 * dindex))),
        col_width=[5, 5, 9, 8, 5, 6, 5],
        tbl_header=cfg.PLT_TBL_HEADER,
        tbl_cells=cfg.PLT_TBL_CELLS,
        font=cfg.PLT_TBL_FONT,
        row_fill_color=cfg.PLT_TBL_ROW_COLORS,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = save_image("dd-analyst.png", fig)

    return {
        "title": f"Stocks: [Finviz] Analyst Recommendations {ticker.upper()}",
        "imagefile": imagefile,
    }
