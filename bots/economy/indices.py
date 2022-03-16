import logging

import df2img
import pandas as pd

import bots.config_discordbot as cfg
from bots.helpers import save_image
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.economy import wsj_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
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

    df["Last Price"] = pd.to_numeric(df["Price"].astype(float))
    df["Change"] = pd.to_numeric(df["Chg"].astype(float))
    df["% Change"] = pd.to_numeric(df["%Chg"].astype(float))
    df = df.drop(columns=["Price", "Chg", "%Chg"])

    # Debug user output
    if cfg.DEBUG:
        logger.debug(df.to_string())

    formats = {"Last Price": "${:.2f}", "Change": "${:.2f}", "% Change": "{:.2f}%"}
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    df = df.fillna("")
    df.set_index(" ", inplace=True)
    font_color = (
        ["white"] * 2
        + [
            [
                "#e4003a" if boolv else "#00ACFF"
                for boolv in df["Change"].str.contains("-")
            ]
        ]
        + [
            [
                "#e4003a" if boolv else "#00ACFF"
                for boolv in df["% Change"].str.contains("-")
            ]
        ]
    )
    fig = df2img.plot_dataframe(
        df,
        fig_size=(720, (40 + (40 * len(df.index)))),
        col_width=[8, 3, 3],
        tbl_header=cfg.PLT_TBL_HEADER,
        tbl_cells=cfg.PLT_TBL_CELLS,
        font=cfg.PLT_TBL_FONT,
        row_fill_color=cfg.PLT_TBL_ROW_COLORS,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    fig.update_traces(
        cells=(
            dict(
                align=["center", "right"],
                font=dict(color=font_color),
            )
        )
    )
    imagefile = save_image("econ-indices.png", fig)
    return {
        "title": "Economy: [WSJ] US Indices",
        "imagefile": imagefile,
    }
