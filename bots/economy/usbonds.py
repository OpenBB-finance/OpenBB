import logging

import pandas as pd

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import wsj_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def usbonds_command():
    """US bonds overview [Wall St. Journal]"""

    # Debug user input
    if imps.DEBUG:
        logger.debug("econ-usbonds")

    # Retrieve data
    df = wsj_model.us_bonds()

    # Check for argument
    if df.empty:
        raise Exception("No available data found")

    df["Rate (%)"] = pd.to_numeric(df["Rate (%)"].astype(float))
    df["Yld (%)"] = pd.to_numeric(df["Yld (%)"].astype(float))
    df["Yld Chg (%)"] = pd.to_numeric(df["Yld Chg (%)"].astype(float))

    formats = {
        "Rate (%)": "{:.2f}%",
        "Yld (%)": "{:.2f}%",
        "Yld Chg (%)": "<b>{:.2f}%</b>",
    }
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    df = df.fillna("")
    df.set_index(" ", inplace=True)

    df = df.set_axis(
        [
            "Rate",
            "Yld",
            "Yld Chg",
        ],
        axis="columns",
    )

    font_color = ["white"] * 3 + [imps.in_decreasing_color_list(df["Yld Chg"])]

    fig = imps.plot_df(
        df,
        fig_size=(550, (40 + (40 * len(df.index)))),
        col_width=[4, 2, 2, 2.1],
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
    fig.update_traces(cells=(dict(align=["center", "right"])))

    imagefile = imps.save_image("econ-usbonds.png", fig)
    return {
        "title": "Economy: [WSJ] US Bonds",
        "imagefile": imagefile,
    }
