import logging

import disnake
import pandas as pd
import requests

from bots import imps
from openbb_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def borrowed_command(ticker: str = ""):
    """Displays borrowed shares available and fee [Stocksera.com]"""

    # Debug user input
    if imps.DEBUG:
        logger.debug("dd borrowed %s", ticker)

    # Check for argument
    if ticker == "":
        raise Exception("Stock ticker is required")

    df = pd.DataFrame(
        requests.get(
            f"https://stocksera.pythonanywhere.com/api/borrowed_shares/{ticker}"
        ).json()
    )

    if df.empty:
        raise Exception("No Data Found")

    title = f"{ticker.upper()} Shares Available to Borrow [Stocksera]"

    df = df.head(200)
    df["changed"] = df["available"].astype(int).diff()
    df = df[df["changed"] != 0.0]
    df = df.drop(columns="changed")

    formats = {"fee": "{:.2f}%", "available": "{:,}"}
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    df = df.rename(columns={"ticker": " ", "date_updated": "Updated"})
    df.set_index(" ", inplace=True)
    df.columns = df.columns.str.capitalize()

    dindex = len(df.index)
    if dindex > 15:
        embeds: list = []
        # Output
        i, i2, end = 0, 0, 15
        df_pg, embeds_img, images_list = pd.DataFrame(), [], []
        while i < dindex:
            df_pg = df.iloc[i:end]
            df_pg.append(df_pg)
            fig = imps.plot_df(
                df_pg,
                fig_size=(550, (40 + (40 * len(df.index)))),
                col_width=[1, 1, 1.5, 2],
                tbl_header=imps.PLT_TBL_HEADER,
                tbl_cells=imps.PLT_TBL_CELLS,
                font=imps.PLT_TBL_FONT,
                row_fill_color=imps.PLT_TBL_ROW_COLORS,
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            fig.update_traces(
                cells=(dict(align=["center", "right", "right", "center"]))
            )
            imagefile = "dd_borrowed.png"
            imagefile = imps.save_image(imagefile, fig)

            if imps.IMAGES_URL or not imps.IMG_HOST_ACTIVE:
                image_link = imps.multi_image(imagefile)
                images_list.append(imagefile)
            else:
                image_link = imps.multi_image(imagefile)

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
            fig_size=(550, (40 + (40 * len(df.index)))),
            col_width=[1, 1, 1.5, 2],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(cells=(dict(align=["center", "right", "right", "center"])))
        imagefile = "dd_borrowed.png"
        imagefile = imps.save_image(imagefile, fig)

        output = {
            "title": title,
            "imagefile": imagefile,
        }

    return output
