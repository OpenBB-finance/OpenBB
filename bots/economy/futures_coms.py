import df2img
import pandas as pd

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.helpers import save_image
from gamestonk_terminal.economy import wsj_model


def futures_coms_command():
    """Futures and commodities overview [Wall St. Journal]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("econ-futures")

    # Retrieve data
    df = wsj_model.top_commodities()

    # Check for argument
    if df.empty:
        raise Exception("No available data found")

    df["Price"] = pd.to_numeric(df["Price"].astype(float))
    df["Chg"] = pd.to_numeric(df["Chg"].astype(float))
    df["%Chg"] = pd.to_numeric(df["%Chg"].astype(float))

    # Debug user output
    if cfg.DEBUG:
        logger.debug(df.to_string())

    formats = {"Price": "${:.2f}", "Chg": "${:.2f}", "%Chg": "{:.2f}%"}
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    df = df.fillna("")
    df.set_index(" ", inplace=True)

    df = df[
        [
            "Price",
            "Chg",
            "%Chg",
        ]
    ]
    dindex = len(df.index)
    fig = df2img.plot_dataframe(
        df,
        fig_size=(800, (40 + (40 * dindex))),
        col_width=[8, 3, 3],
        tbl_header=cfg.PLT_TBL_HEADER,
        tbl_cells=cfg.PLT_TBL_CELLS,
        font=cfg.PLT_TBL_FONT,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    fig.update_traces(cells=(dict(align="left")))
    imagefile = save_image("econ-futures.png", fig)
    return {"title": "Economy: [WSJ] Futures/Commodities", "imagefile": imagefile}
