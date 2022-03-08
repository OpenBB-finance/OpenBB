import os

import df2img
import disnake

import bots.config_discordbot as cfg
from bots import helpers
from bots.config_discordbot import gst_imgur, logger
from bots.menus.menu import Menu
from gamestonk_terminal.etf.discovery import wsj_model


def etfs_command(sort=""):
    """Display Upcoming Earnings. [Source: Seeking Alpha]"""

    # Debug
    if cfg.DEBUG:
        logger.debug("etfs")

    df_etfs = wsj_model.etf_movers(sort)

    if df_etfs.empty:
        raise Exception("No available data found")

    df_etfs.set_index(" ", inplace=True)
    prfx = "Top"
    if sort == "active":
        prfx = "Most"
    title = f"ETF Movers ({prfx} {sort.capitalize()})"

    dindex = len(df_etfs.index)
    if dindex > 15:
        embeds: list = []
        # Output
        i, i2, end = 0, 0, 15
        df_pg = []
        embeds_img = []
        dindex = len(df_etfs.index)
        while i < dindex:
            df_pg = df_etfs.iloc[i:end]
            df_pg.append(df_pg)
            fig = df2img.plot_dataframe(
                df_pg,
                fig_size=(1200, (40 + (40 * dindex))),
                col_width=[1, 9, 1.5, 1.5, 1.5, 1.5],
                tbl_header=cfg.PLT_TBL_HEADER,
                tbl_cells=cfg.PLT_TBL_CELLS,
                font=cfg.PLT_TBL_FONT,
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            fig.update_traces(cells=(dict(align=["left"])))
            imagefile = "disc-etfs.png"
            imagefile = helpers.save_image(imagefile, fig)

            if cfg.IMAGES_URL:
                image_link = cfg.IMAGES_URL + imagefile
            else:
                imagefile_save = cfg.IMG_DIR + imagefile
                uploaded_image = gst_imgur.upload_image(
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

        output = {
            "view": Menu,
            "title": title,
            "embed": embeds,
            "choices": choices,
            "embeds_img": embeds_img,
        }
    else:
        fig = df2img.plot_dataframe(
            df_etfs,
            fig_size=(1200, (40 + (40 * dindex))),
            col_width=[1, 9, 1.5, 1.5, 1.5, 1.5],
            tbl_header=cfg.PLT_TBL_HEADER,
            tbl_cells=cfg.PLT_TBL_CELLS,
            font=cfg.PLT_TBL_FONT,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(cells=(dict(align=["left", "center"])))
        imagefile = helpers.save_image("disc-etfs.png", fig)

        output = {
            "title": title,
            "imagefile": imagefile,
        }

    return output
