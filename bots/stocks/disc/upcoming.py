import logging
import os

import disnake

from bots import imps
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.discovery import seeking_alpha_model

logger = logging.getLogger(__name__)


# pylint: disable=W0612,W0631
@log_start_end(log=logger)
def earnings_command():
    """Display Upcoming Earnings. [Source: Seeking Alpha]"""

    # Debug
    if imps.DEBUG:
        logger.debug("earnings")

    df_earnings = seeking_alpha_model.get_next_earnings(2)
    for n_days, earning_date in enumerate(df_earnings.index.unique()):

        df_earn = df_earnings[earning_date == df_earnings.index][
            ["Ticker", "Name"]
        ].dropna()

        df_earn.index = df_earn["Ticker"].values
        df_earn.drop(columns=["Ticker"], inplace=True)

    title = f"Earnings on {earning_date.date()}"

    dindex = len(df_earn.index)
    if dindex > 15:
        embeds: list = []
        # Output
        i, i2, end = 0, 0, 15
        df_pg, embeds_img, images_list = [], [], []
        while i < dindex:
            df_pg = df_earn.iloc[i:end]
            df_pg.append(df_pg)
            fig = imps.plot_df(
                df_pg,
                fig_size=(800, (40 + (40 * dindex))),
                col_width=[1, 5],
                tbl_header=imps.PLT_TBL_HEADER,
                tbl_cells=imps.PLT_TBL_CELLS,
                font=imps.PLT_TBL_FONT,
                row_fill_color=imps.PLT_TBL_ROW_COLORS,
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            fig.update_traces(cells=(dict(align=["center", "left"])))
            imagefile = "disc-upcoming.png"
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
            df_earn,
            fig_size=(800, (40 + (40 * dindex))),
            col_width=[1, 5],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(cells=(dict(align=["center", "left"])))
        imagefile = imps.save_image("disc-upcoming.png", fig)

        output = {
            "title": title,
            "imagefile": imagefile,
        }

    return output
