import df2img

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.helpers import save_image
from gamestonk_terminal.stocks.discovery import fidelity_model


def ford_command():
    """Display Orders by Fidelity Customers. [Source: Fidelity]"""

    # Debug
    if cfg.DEBUG:
        logger.debug("disc-ford")
    order_header, df_orders = fidelity_model.get_orders()

    df_orders = df_orders.head(n=30).iloc[:, :-1]
    df_orders = df_orders.applymap(str)

    font_color = (
        ["white"] * 2
        + [
            [
                "#ad0000" if boolv else "#0d5700"
                for boolv in df_orders["Price Change"].str.contains("-")
            ]
        ]
        + [["white"] * 3]
    )

    df_orders.set_index("Symbol", inplace=True)
    df_orders = df_orders.apply(lambda x: x.str.slice(0, 20))

    dindex = len(df_orders.index)
    fig = df2img.plot_dataframe(
        df_orders,
        fig_size=(1500, (40 + (40 * dindex))),
        col_width=[1, 3, 2.2, 3, 2, 2],
        tbl_cells=dict(
            align=["left", "center", "left", "left", "center"],
            font=dict(color=font_color),
            height=35,
        ),
        template="plotly_dark",
        font=dict(
            family="Consolas",
            size=20,
        ),
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = save_image("disc-ford.png", fig)

    return {
        "title": "Fidelity Customer Orders",
        "imagefile": imagefile,
    }
