import df2img
import pandas as pd

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.helpers import save_image
from gamestonk_terminal.economy import wsj_model


def indices_command():
    """US indices overview [Wall St. Journal]"""
    # Debug user input
    if cfg.DEBUG:
        logger.debug("econ-indices")

    # Retrieve data
    df = wsj_model.us_indices()

    # Check for argument
    if df.empty:
        raise Exception("No available data found")

    df["Price"] = pd.to_numeric(df["Price"].astype(float))
    df["Chg"] = pd.to_numeric(df["Chg"].astype(float))
    df["%Chg"] = pd.to_numeric(df["%Chg"].astype(float))

    formats = {"Price": "${:.2f}", "Chg": "${:.2f}", "%Chg": "{:.2f}%"}
    for col, value in formats.items():
        # pylint: disable=W0640
        df[col] = df[col].map(lambda x: value.format(x))

    # Debug user output
    if cfg.DEBUG:
        logger.debug(df)

    df = df[
        [
            " ",
            "Price",
            "Chg",
            "%Chg",
        ]
    ]

    df = df.fillna("")
    df.set_index(" ", inplace=True)

    dindex = len(df.index)
    fig = df2img.plot_dataframe(
        df,
        fig_size=(800, (40 + (40 * dindex))),
        col_width=[8, 3, 3],
        tbl_cells=dict(
            align=["left", "center"],
            height=35,
        ),
        template="plotly_dark",
        font=dict(
            family="Consolas",
            size=20,
        ),
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = save_image("econ-indices.png", fig)
    return {
        "title": "Economy: [WSJ] US Indices",
        "imagefile": imagefile,
    }
