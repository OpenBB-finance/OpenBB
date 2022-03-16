import logging
import os

import df2img
import disnake

import bots.config_discordbot as cfg
from bots import helpers
from bots.config_discordbot import gst_imgur
from bots.menus.menu import Menu
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.discovery import fidelity_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def ford_command():
    """Display Orders by Fidelity Customers. [Source: Fidelity]"""

    # Debug
    if cfg.DEBUG:
        logger.debug("disc ford")
    order_header, df_orders = fidelity_model.get_orders()

    df_orders = df_orders.head(n=30).iloc[:, :-1]
    df_orders = df_orders.applymap(str)

    font_color = (
        ["white"] * 2
        + [
            [
                "#e4003a" if boolv else "#00ACFF"
                for boolv in df_orders["Price Change"].str.contains("-")
            ]
        ]
        + [["white"] * 3]
    )

    df_orders.set_index("Symbol", inplace=True)
    df_orders = df_orders.apply(lambda x: x.str.slice(0, 30))
    title = "Fidelity Customer Orders"

    dindex = len(df_orders.index)
    embeds: list = []
    # Output
    i, i2, end = 0, 0, 15
    df_pg, embeds_img, images_list = [], [], []
    while i < dindex:
        df_pg = df_orders.iloc[i:end]
        df_pg.append(df_pg)
        fig = df2img.plot_dataframe(
            df_pg,
            fig_size=(1400, (40 + (40 * dindex))),
            col_width=[1, 2.3, 2.2, 4, 2, 2],
            tbl_header=cfg.PLT_TBL_HEADER,
            tbl_cells=cfg.PLT_TBL_CELLS,
            font=cfg.PLT_TBL_FONT,
            row_fill_color=cfg.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(
            cells=(
                dict(
                    align=["center"],
                    font=dict(color=font_color),
                )
            )
        )
        imagefile = "disc-ford.png"
        imagefile = helpers.save_image(imagefile, fig)

        if cfg.IMAGES_URL or cfg.IMGUR_CLIENT_ID != "REPLACE_ME":
            image_link = cfg.IMAGES_URL + imagefile
            images_list.append(imagefile)
        else:
            imagefile_save = cfg.IMG_DIR / imagefile
            uploaded_image = gst_imgur.upload_image(imagefile_save, title="something")
            image_link = uploaded_image.link
            os.remove(imagefile_save)

        embeds_img.append(
            f"{image_link}",
        )
        embeds.append(
            disnake.Embed(
                title=title,
                colour=cfg.COLOR,
            ),
        )
        i2 += 1
        i += 15
        end += 15

    # Author/Footer
    for i in range(0, i2):
        embeds[i].set_author(
            name=cfg.AUTHOR_NAME,
            url=cfg.AUTHOR_URL,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embeds[i].set_footer(
            text=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

    i = 0
    for i in range(0, i2):
        embeds[i].set_image(url=embeds_img[i])

        i += 1
    embeds[0].set_footer(text=f"Page 1 of {len(embeds)}")
    choices = [
        disnake.SelectOption(label="Home", value="0", emoji="🟢"),
    ]

    return {
        "view": Menu,
        "title": title,
        "embed": embeds,
        "choices": choices,
        "embeds_img": embeds_img,
        "images_list": images_list,
    }
