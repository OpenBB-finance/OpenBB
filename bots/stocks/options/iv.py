import df2img

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.helpers import save_image
from gamestonk_terminal.stocks.options import barchart_model


def iv_command(ticker: str = None):
    """Options IV"""

    # Debug
    if cfg.DEBUG:
        logger.debug("opt-iv %s", ticker)

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
    df.set_index(" ", inplace=True)
    fig = df2img.plot_dataframe(
        df,
        fig_size=(600, 1500),
        col_width=[3, 3],
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
    imagefile = save_image("opt-iv.png", fig)

    return {
        "title": f"{ticker.upper()} Options: IV",
        "imagefile": imagefile,
    }
