import logging

import numpy as np

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.due_diligence import finviz_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def analyst_command(ticker=""):
    """Displays analyst recommendations [Finviz]"""

    # Debug
    if imps.DEBUG:
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
    fig = imps.plot_df(
        df,
        fig_size=(900, (40 + (40 * dindex))),
        col_width=[5, 5, 9, 8, 5, 6, 5],
        tbl_header=imps.PLT_TBL_HEADER,
        tbl_cells=imps.PLT_TBL_CELLS,
        font=imps.PLT_TBL_FONT,
        row_fill_color=imps.PLT_TBL_ROW_COLORS,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = imps.save_image("dd-analyst.png", fig)

    return {
        "title": f"Stocks: [Finviz] Analyst Recommendations {ticker.upper()}",
        "imagefile": imagefile,
    }
