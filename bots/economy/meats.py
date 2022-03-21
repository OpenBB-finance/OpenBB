import logging

import pandas as pd

from bots import imps
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.economy import finviz_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def meats_command():
    """Displays meats futures data [Finviz]"""

    # Debug user input
    if imps.DEBUG:
        logger.debug("econ-meats")

    # Retrieve data
    d_futures = finviz_model.get_futures()
    df = pd.DataFrame(d_futures["Meats"])

    # Check for argument
    if df.empty:
        raise Exception("No available data found")

    df = df.fillna("")
    df = df.set_index("label")
    df = df.sort_values(by="ticker", ascending=False)

    formats = {"last": "${:.2f}", "prevClose": "${:.2f}", "change": "<b>{:.2f}%</b>"}
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    # Debug user output
    if imps.DEBUG:
        logger.debug(df)

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

    font_color = ["white"] * 3 + [
        ["#e4003a" if boolv else "#00ACFF" for boolv in df["Change"].str.contains("-")]
    ]

    fig = imps.plot_df(
        df,
        fig_size=(500, (40 + (40 * len(df.index)))),
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
    imagefile = imps.save_image("econ-meats.png", fig)
    return {
        "title": "Economy: [Finviz] Meats Futures",
        "imagefile": imagefile,
    }
