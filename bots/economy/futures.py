import logging

import disnake
import pandas as pd
import requests

from bots import imps
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import get_user_agent

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def futures_command():
    """Futures [Yahoo Finance]"""

    # Debug user input
    if imps.DEBUG:
        logger.debug("futures")

    # Retrieve data
    req = pd.read_html(
        requests.get(
            "https://finance.yahoo.com/commodities",
            headers={"User-Agent": get_user_agent()},
        ).text
    )
    df = req[0]

    # Check for argument
    if df.empty:
        raise Exception("No available data found")

    title = "Futures [yfinance]"
    df["Last Price"] = pd.to_numeric(df["Last Price"].astype(float))
    df["Change"] = pd.to_numeric(df["Change"].astype(float))

    formats = {
        "Last Price": "${:.2f}",
        "Change": "${:.2f}",
    }
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    df = df.fillna("")

    df["Change"] = df.apply(
        lambda x: f"{x['Change']}  (<b>{x['% Change']}</b>)", axis=1
    )

    df.drop(columns="Symbol")
    df = df.rename(columns={"Name": " "})
    df.set_index(" ", inplace=True)

    df = df[["Last Price", "Change"]]

    font_color = ["white"] * 2 + [
        ["#e4003a" if boolv else "#00ACFF" for boolv in df["Change"].str.contains("-")]
    ]

    dindex = len(df.index)
    if dindex > 15:
        embeds: list = []
        # Output
        i, i2, end = 0, 0, 15
        df_pg, embeds_img, images_list = pd.DataFrame(), [], []
        while i < dindex:
            df_pg = df[["Last Price", "Change"]].iloc[i:end]
            df_pg.append(df_pg)
            font_color = ["white"] * 2 + [
                [
                    "#e4003a" if boolv else "#00ACFF"
                    for boolv in df_pg["Change"].str.contains("-")
                ]
            ]
            fig = imps.plot_df(
                df_pg,
                fig_size=(620, (40 + (45 * len(df.index)))),
                col_width=[4.2, 1.8, 2.5],
                tbl_header=imps.PLT_TBL_HEADER,
                tbl_cells=imps.PLT_TBL_CELLS,
                font=imps.PLT_TBL_FONT,
                row_fill_color=imps.PLT_TBL_ROW_COLORS,
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            fig.update_traces(
                cells=(
                    dict(
                        align=["center", "right"],
                        font=dict(color=font_color),
                    )
                )
            )
            imagefile = "econ-futures.png"
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
            fig_size=(620, (40 + (45 * len(df.index)))),
            col_width=[4.2, 1.8, 2.5],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(
            cells=(
                dict(
                    align=["center", "right"],
                    font=dict(color=font_color),
                )
            )
        )
        imagefile = "econ-futures.png"
        imagefile = imps.save_image(imagefile, fig)

        output = {
            "title": title,
            "imagefile": imagefile,
        }

    return output
