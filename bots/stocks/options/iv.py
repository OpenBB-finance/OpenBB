import logging

import df2img

import bots.config_discordbot as cfg
from bots.helpers import save_image
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.options import barchart_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def iv_command(ticker: str = None):
    """Options IV"""

    # Debug
    if cfg.DEBUG:
        logger.debug("opt info %s", ticker)

    # Check for argument
    if ticker is None:
        raise Exception("Stock ticker is required")

    df = barchart_model.get_options_info(ticker)
    df = df.fillna("")
    df = df.set_axis(
        [
            " ",
            "",
        ],
        axis="columns",
    )
    df[""] = df[""].str.lstrip()
    font_color = [["white"]] + [
        ["#e4003a" if "-" in df[""][0] else "#00ACFF"] + ["white"]
    ]
    df.set_index(" ", inplace=True)

    fig = df2img.plot_dataframe(
        df,
        fig_size=(600, 1500),
        col_width=[3, 3],
        tbl_header=cfg.PLT_TBL_HEADER,
        tbl_cells=cfg.PLT_TBL_CELLS,
        font=cfg.PLT_TBL_FONT,
        row_fill_color=cfg.PLT_TBL_ROW_COLORS,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    fig.update_traces(
        header=(
            dict(
                values=[[f"<b>{ticker.upper()}</b>"]],
                align="center",
            )
        ),
        cells=(
            dict(
                align="left",
                font=dict(color=font_color),
            )
        ),
    )
    imagefile = save_image("opt-info.png", fig)

    return {
        "title": f"{ticker.upper()} Options: IV",
        "imagefile": imagefile,
    }
