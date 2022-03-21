import logging
import os

import disnake

from bots import imps
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.dark_pool_shorts import yahoofinance_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def shorted_command(num: int = 10):
    """Show most shorted stocks [Yahoo Finance]"""

    # Debug user input
    if imps.DEBUG:
        logger.debug("dps shorted %s", num)

    # Check for argument
    if num < 0:
        raise Exception("Number has to be above 0")

    # Retrieve data
    df = yahoofinance_model.get_most_shorted().head(num)
    if df.empty:
        raise Exception("No available data found")
    # Debug user output
    if imps.DEBUG:
        logger.debug(df.to_string())

    # Output data
    title = "Stocks: [Yahoo Finance] Most Shorted"
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")
    df = df.drop(columns=["PE Ratio (TTM)"])
    df.set_index("Symbol", inplace=True)

    dindex = len(df.index)
    if dindex > 15:
        embeds: list = []
        # Output
        i, i2, end = 0, 0, 15
        df_pg, embeds_img, images_list = [], [], []
        while i < dindex:
            df_pg = df.iloc[i:end]
            df_pg.append(df_pg)
            fig = imps.plot_df(
                df_pg,
                fig_size=(900, (45 * dindex)),
                col_width=[2, 9, 2.5, 2.5, 2.5, 3, 3, 3],
                tbl_header=imps.PLT_TBL_HEADER,
                tbl_cells=imps.PLT_TBL_CELLS,
                font=imps.PLT_TBL_FONT,
                row_fill_color=imps.PLT_TBL_ROW_COLORS,
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            fig.update_traces(cells=(dict(align=["center", "left"])))
            imagefile = "etf-holdings.png"
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
            df,
            fig_size=(900, (45 * dindex)),
            col_width=[2, 9, 2.5, 2.5, 2.5, 3, 3, 3],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(cells=(dict(align=["left", "center"])))
        imagefile = imps.save_image("etf-holdings.png", fig)

        output = {
            "title": title,
            "imagefile": imagefile,
        }

    return output
