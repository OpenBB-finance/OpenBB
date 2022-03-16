import logging

import df2img
import pandas as pd

import bots.config_discordbot as cfg
from bots.helpers import save_image
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.economy import wsj_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def usbonds_command():
    """US bonds overview [Wall St. Journal]"""

    # Debug user input
    if cfg.DEBUG:
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
        "Yld Chg (%)": "{:.2f}%",
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

    fig = df2img.plot_dataframe(
        df,
        fig_size=(800, (40 + (40 * len(df.index)))),
        col_width=[8, 3, 3],
        tbl_header=cfg.PLT_TBL_HEADER,
        tbl_cells=cfg.PLT_TBL_CELLS,
        font=cfg.PLT_TBL_FONT,
        row_fill_color=cfg.PLT_TBL_ROW_COLORS,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    fig.update_traces(cells=(dict(align="left")))

    imagefile = save_image("econ-usbonds.png", fig)
    return {
        "title": "Economy: [WSJ] US Bonds",
        "imagefile": imagefile,
    }
