import df2img
import pandas as pd

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.helpers import save_image
from gamestonk_terminal.economy import wsj_model


def currencies_command():
    """Currencies overview [Wall St. Journal]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("econ-currencies")

    # Retrieve data
    df = wsj_model.global_currencies()
    df = pd.DataFrame.from_dict(df)

    # Check for argument
    if df.empty:
        raise Exception("No available data found")

    df["Last"] = pd.to_numeric(df["Last"].astype(float))
    df["Chng"] = pd.to_numeric(df["Chng"].astype(float))
    df["%Chng"] = pd.to_numeric(df["%Chng"].astype(float))

    formats = {"Last": "{:.2f}", "Chng": "{:.2f}", "%Chng": "{:.2f}%"}
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    df = df.fillna("")
    df.set_index(" ", inplace=True)

    # Debug user output
    if cfg.DEBUG:
        logger.debug(df.to_string())

    df = df[
        [
            "Last",
            "Chng",
            "%Chng",
        ]
    ]
    dindex = len(df.index)
    fig = df2img.plot_dataframe(
        df,
        fig_size=(800, (40 + (40 * dindex))),
        col_width=[8, 3, 3],
        tbl_cells=dict(
            align="left",
            height=35,
        ),
        template="plotly_dark",
        font=dict(
            family="Consolas",
            size=20,
        ),
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = save_image("econ-currencies.png", fig)
    return {
        "title": "Economy: [WSJ] Currencies",
        "imagefile": imagefile,
    }
