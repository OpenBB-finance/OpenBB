import logging

import pandas as pd

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.economy import finviz_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def metals_command():
    """Displays metals futures data [Finviz]"""
    # Debug user input
    if imps.DEBUG:
        logger.debug("econ-metals")

    # Retrieve data
    d_futures = finviz_model.get_futures()
    df = pd.DataFrame(d_futures["Metals"])

    # Check for argument
    if df.empty:
        raise Exception("No available data found")

    formats = {"last": "${:.2f}", "prevClose": "${:.2f}", "change": "<b>{:.2f}%</b>"}
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    # Debug user output
    if imps.DEBUG:
        logger.debug(df)

    df = df.sort_values(by="ticker", ascending=False)
    df = df.fillna("")
    df.set_index("label", inplace=True)

    df = df[
        [
            "prevClose",
            "last",
            "change",
        ]
    ]

    df.index.names = [""]
    df = df.rename(
        columns={"prevClose": "PrevClose", "last": "Last", "change": "Change"}
    )

    font_color = ["white"] * 3 + [imps.in_decreasing_color_list(df["Change"])]

    fig = imps.plot_df(
        df,
        fig_size=(570, (40 + (40 * len(df.index)))),
        col_width=[5, 3, 3],
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
    imagefile = imps.save_image("econ-metals.png", fig)
    return {
        "title": "Economy: [WSJ] Metals Futures",
        "imagefile": imagefile,
    }
