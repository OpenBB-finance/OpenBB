import logging
import os

import disnake
import pandas as pd

from bots import imps
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.etf.discovery import wsj_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def etfs_disc_command(sort=""):
    """Displays ETF's Top Gainers/Decliners, Most Active  [Wall Street Journal]"""

    # Debug
    if imps.DEBUG:
        logger.debug("etfs")

    df_etfs = wsj_model.etf_movers(sort, export=True)

    if df_etfs.empty:
        raise Exception("No available data found")

    prfx = "Most" if sort == "active" else "Top"
    title = f"ETF Movers ({prfx} {sort.capitalize()})"

    df_etfs["Price"] = pd.to_numeric(df_etfs["Price"].astype(float))

    df_etfs["Price"] = df_etfs.apply(lambda x: f"${x['Price']:.2f}", axis=1)
    df_etfs["Change"] = df_etfs.apply(
        lambda x: f"${x['Chg']:.2f} (<b>{x['%Chg']:.2f}%</b>)", axis=1
    )

    df_etfs.set_index(" ", inplace=True)
    df_etfs = df_etfs.drop(columns=["Chg", "%Chg"])

    df_etfs = df_etfs[
        [
            "Name",
            "Price",
            "Change",
            "Vol",
        ]
    ]

    dindex = len(df_etfs.index)
    if dindex > 15:
        embeds: list = []
        # Output
        i, i2, end = 0, 0, 15
        df_pg, embeds_img, images_list = [], [], []
        while i < dindex:
            df_pg = df_etfs.iloc[i:end]
            df_pg.append(df_pg)
            fig = imps.plot_df(
                df_pg,
                fig_size=(820, (40 + (40 * dindex))),
                col_width=[1.1, 9, 1.5, 3, 1.5],
                tbl_header=imps.PLT_TBL_HEADER,
                tbl_cells=imps.PLT_TBL_CELLS,
                font=imps.PLT_TBL_FONT,
                row_fill_color=imps.PLT_TBL_ROW_COLORS,
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            fig.update_traces(cells=(dict(align=["center", "center", "right"])))
            imagefile = "disc-etfs.png"
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

        output = {
            "view": imps.Menu,
            "title": title,
            "embed": embeds,
            "choices": choices,
            "embeds_img": embeds_img,
            "images_list": images_list,
        }
    else:
        fig = imps.plot_df(
            df_etfs,
            fig_size=(820, (40 + (40 * dindex))),
            col_width=[1, 9, 1.5, 3, 1.5],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(cells=(dict(align=["center", "center", "right"])))
        imagefile = imps.save_image("disc-etfs.png", fig)

        output = {
            "title": title,
            "imagefile": imagefile,
        }

    return output
