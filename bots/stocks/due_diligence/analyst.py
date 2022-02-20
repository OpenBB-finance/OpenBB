import df2img
import numpy as np

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.helpers import save_image
from gamestonk_terminal.stocks.due_diligence import finviz_model


def analyst_command(ticker=""):
    """Displays analyst recommendations [Finviz]"""

    # Debug
    if cfg.DEBUG:
        logger.debug("dd-analyst %s", ticker)

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
        fig_size=(1500, (40 + (40 * dindex))),
        col_width=[5, 5, 8, 14, 5, 5, 5],
        tbl_cells=dict(
            height=35,
        ),
        font=dict(
            family="Consolas",
            size=20,
        ),
        template="plotly_dark",
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = save_image("dd-analyst.png", fig)

    return {
        "title": f"Stocks: [Finviz] Analyst Recommendations {ticker.upper()}",
        "imagefile": imagefile,
    }
