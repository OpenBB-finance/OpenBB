import logging

import disnake
import pandas as pd
import requests

from bots import imps
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def reverse_repo_command(days: int = 50):
    """Displays Reverse Repo [Stocksera.com]"""

    # Debug user input
    if imps.DEBUG:
        logger.debug("dd repo %s", days)

    df = pd.DataFrame(
        requests.get(
            f"https://stocksera.pythonanywhere.com/api/reverse_repo/?days={str(days)}"
        ).json()
    )

    if df.empty:
        raise Exception("No Data Found")

    title = "Reverse Repo [Stocksera]"

    df["Difference"] = df["Amount"].diff().fillna(0)

    formats = {
        "Amount": "${:.2f}B",
        "Average": "${:.2f}B",
        "Difference": "<b>${:.2f}B</b>",
    }
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    df = df.drop(columns="Moving Avg")
    df = df.sort_values(by="Date", ascending=False)

    font_color = ["white"] * 4 + [
        [
            "#e4003a" if boolv else "#00ACFF"
            for boolv in df["Difference"].str.contains("-")
        ]  # type: ignore
    ]

    df.set_index("Date", inplace=True)
    df.columns = df.columns.str.capitalize()

    dindex = len(df.index)
    if dindex > 15:
        embeds: list = []
        # Output
        i, i2, end = 0, 0, 15
        df_pg, embeds_img, images_list = pd.DataFrame(), [], []
        while i < dindex:
            df_pg = df.iloc[i:end]
            font_color = ["white"] * 4 + [
                [
                    "#e4003a" if boolv else "#00ACFF"
                    for boolv in df_pg["Difference"].str.contains("-")
                ]  # type: ignore
            ]
            df_pg.append(df_pg)
            fig = imps.plot_df(
                df_pg,
                fig_size=(650, (40 + (40 * len(df.index)))),
                col_width=[1.8, 1.5, 1.7, 1.3, 1.8],
                tbl_header=imps.PLT_TBL_HEADER,
                tbl_cells=imps.PLT_TBL_CELLS,
                font=imps.PLT_TBL_FONT,
                row_fill_color=imps.PLT_TBL_ROW_COLORS,
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            fig.update_traces(
                cells=(
                    dict(
                        align=["center", "right", "center", "right"],
                        font=dict(color=font_color),
                    )
                )
            )
            imagefile = "dd_r_repo.png"
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
            fig_size=(650, (40 + (40 * len(df.index)))),
            col_width=[1.8, 1.5, 1.7, 1.3, 1.8],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(
            cells=(
                dict(
                    align=["center", "right", "center", "right"],
                    font=dict(color=font_color),
                )
            )
        )
        imagefile = "dd_r_repo.png"
        imagefile = imps.save_image(imagefile, fig)

        output = {
            "title": title,
            "imagefile": imagefile,
        }
    return output
