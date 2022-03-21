import logging
import os

import disnake

from bots import imps
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.discovery import fidelity_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def ford_command():
    """Display Orders by Fidelity Customers. [Source: Fidelity]"""

    # Debug
    if imps.DEBUG:
        logger.debug("disc ford")
    order_header, df_orders = fidelity_model.get_orders()  # pylint: disable=W0612

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
    df_orders = df_orders.rename(
        columns={"# Buy Orders": "# Buy's", "# Sell Orders": "# Sell's"}
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
        fig = imps.plot_df(
            df_pg,
            fig_size=(900, (40 + (40 * dindex))),
            col_width=[1, 2.4, 2.35, 4, 1.5, 1.5],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(
            cells=(
                dict(
                    align=["center", "center", "center", "center", "right"],
                    font=dict(color=font_color),
                )
            )
        )
        imagefile = "disc-ford.png"
        imagefile = imps.save_image(imagefile, fig)

        if imps.IMAGES_URL or imps.IMGUR_CLIENT_ID != "REPLACE_ME":
            image_link = imps.IMAGES_URL + imagefile
            images_list.append(imagefile)
        else:
            imagefile_save = imps.IMG_DIR / imagefile
            uploaded_image = imps.gst_imgur.upload_image(
                imagefile_save, title="something"
            )
            image_link = uploaded_image.link
            os.remove(imagefile_save)

        embeds_img.append(
            f"{image_link}",
        )
        embeds.append(
            disnake.Embed(
                title=title,
                colour=imps.COLOR,
            ),
        )
        i2 += 1
        i += 15
        end += 15

    # Author/Footer
    for i in range(0, i2):
        embeds[i].set_author(
            name=imps.AUTHOR_NAME,
            url=imps.AUTHOR_URL,
            icon_url=imps.AUTHOR_ICON_URL,
        )
        embeds[i].set_footer(
            text=imps.AUTHOR_NAME,
            icon_url=imps.AUTHOR_ICON_URL,
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
        "view": imps.Menu,
        "title": title,
        "embed": embeds,
        "choices": choices,
        "embeds_img": embeds_img,
        "images_list": images_list,
    }
