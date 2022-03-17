import logging

import df2img
import pandas as pd

import bots.config_discordbot as cfg
from bots.helpers import save_image
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.economy import finviz_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def meats_command():
    """Displays meats futures data [Finviz]"""

    # Debug user input
    if cfg.DEBUG:
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

    formats = {"last": "${:.2f}", "prevClose": "${:.2f}"}
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    # Debug user output
    if cfg.DEBUG:
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
    fig = df2img.plot_dataframe(
        df,
        fig_size=(800, (40 + (40 * len(df.index)))),
        col_width=[6, 3, 3],
        tbl_header=cfg.PLT_TBL_HEADER,
        tbl_cells=cfg.PLT_TBL_CELLS,
        font=cfg.PLT_TBL_FONT,
        row_fill_color=cfg.PLT_TBL_ROW_COLORS,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    fig.update_traces(cells=(dict(align="left")))

    imagefile = save_image("econ-meats.png", fig)
    return {
        "title": "Economy: [Finviz] Meats Futures",
        "imagefile": imagefile,
    }
