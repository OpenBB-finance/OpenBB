import logging
import os

import df2img
import disnake
import pandas as pd

import bots.config_discordbot as cfg
from bots.config_discordbot import gst_imgur
from bots.helpers import save_image
from bots.menus.menu import Menu
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.insider import finviz_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def lins_command(ticker: str = "", num: int = 10):
    """Display insider activity for a given stock ticker. [Source: Finviz]

    Parameters
    ----------
    ticker : Stock Ticker
    num : Number of latest insider activity to display
    """

    # Debug
    if cfg.DEBUG:
        logger.debug("disc-lins %s", num)

    d_finviz_insider = finviz_model.get_last_insider_activity(ticker)

    df = pd.DataFrame.from_dict(d_finviz_insider)
    df.set_index("Date", inplace=True)

    df = df[
        [
            "Relationship",
            "Transaction",
            "#Shares",
            "Cost",
            "Value ($)",
            "#Shares Total",
            "Insider Trading",
            "SEC Form 4",
        ]
    ]

    df = df.head(num)
    df = df.replace(to_replace="Option Exercise", value="Opt Ex.", regex=True)

    title = f"Insider Trading for {ticker.upper()}"

    embeds: list = []

    i, i2, end = 0, 0, 20
    df_pg, embeds_img, images_list = [], [], []

    while i < len(df.index):
        df_pg = df.iloc[i:end]
        df_pg.append(df_pg)
        fig = df2img.plot_dataframe(
            df_pg,
            fig_size=(1700, (40 + (45 * 20))),
            col_width=[4, 13, 4, 4, 3.5, 5.3, 6, 8, 7],
            tbl_header=cfg.PLT_TBL_HEADER,
            tbl_cells=cfg.PLT_TBL_CELLS,
            font=cfg.PLT_TBL_FONT,
            row_fill_color=cfg.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(cells=(dict(align=["center", "left"])))
        imagefile = save_image(f"disc-insider{i}.png", fig)

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
        i += 20
        end += 20

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
