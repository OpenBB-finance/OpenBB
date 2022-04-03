import logging

import pandas as pd

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import wsj_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def indices_command():
    """US indices overview [Wall St. Journal]"""
    # Debug user input
    if imps.DEBUG:
        logger.debug("econ-indices")

    # Retrieve data
    df = wsj_model.us_indices()

    # Check for argument
    if df.empty:
        raise Exception("No available data found")

    df["Last Price"] = pd.to_numeric(df["Price"].astype(float))
    df["Change"] = pd.to_numeric(df["Chg"].astype(float))
    df["%Chg"] = pd.to_numeric(df["%Chg"].astype(float))

    # Debug user output
    if imps.DEBUG:
        logger.debug(df.to_string())

    formats = {
        "Last Price": "${:.2f}",
        "Change": "${:.2f}",
        "%Chg": "<b>{:.2f}%</b>",
    }
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    df["Change"] = df.apply(lambda x: f"{x['Change']}  (<b>{x['%Chg']}</b>)", axis=1)

    df = df.fillna("")
    df.set_index(" ", inplace=True)

    font_color = ["white"] * 2 + [
        ["#e4003a" if boolv else "#00ACFF" for boolv in df["%Chg"].str.contains("-")]
    ]

    df = df.drop(columns=["Price", "Chg", "%Chg"])
    fig = imps.plot_df(
        df,
        fig_size=(620, (40 + (40 * len(df.index)))),
        col_width=[4, 2.4, 3],
        tbl_header=imps.PLT_TBL_HEADER,
        tbl_cells=imps.PLT_TBL_CELLS,
        font=imps.PLT_TBL_FONT,
        row_fill_color=imps.PLT_TBL_ROW_COLORS,
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
    imagefile = imps.save_image("econ-indices.png", fig)
    return {
        "title": "Economy: [WSJ] US Indices",
        "imagefile": imagefile,
    }
