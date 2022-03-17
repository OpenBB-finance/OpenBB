import logging
import os

import df2img
import disnake
import pandas as pd
import yahoo_fin.stock_info as si

import bots.config_discordbot as cfg
from bots import helpers
from bots.config_discordbot import gst_imgur
from bots.menus.menu import Menu
from gamestonk_terminal.decorators import log_start_end

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def futures_command():
    """Futures [Yahoo Finance]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("futures")

    # Retrieve data
    df = si.get_futures()

    # Check for argument
    if df.empty:
        raise Exception("No available data found")

    title = "Futures [yfinance]"
    df["Last Price"] = pd.to_numeric(df["Last Price"].astype(float))
    df["Change"] = pd.to_numeric(df["Change"].astype(float))

    formats = {"Last Price": "${:.2f}", "Change": "${:.2f}"}
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    df = df.applymap(str)
    df = df.fillna("")

    df.drop(columns="Symbol")
    df = df.rename(columns={"Name": " "})
    df.set_index(" ", inplace=True)

    df = df[["Last Price", "Change", "% Change"]]

    font_color = (
        ["white"] * 2
        + [
            [
                "#e4003a" if boolv else "#00ACFF"
                for boolv in df["Change"].str.contains("-")
            ]
        ]
        + [
            [
                "#e4003a" if boolv else "#00ACFF"
                for boolv in df["% Change"].str.contains("-")
            ]
        ]
    )
    dindex = len(df.index)
    if dindex > 15:
        embeds: list = []
        # Output
        i, i2, end = 0, 0, 15
        df_pg, embeds_img, images_list = pd.DataFrame(), [], []
        while i < dindex:
            df_pg = df.iloc[i:end]
            df_pg.append(df_pg)
            font_color = (
                ["white"] * 2
                + [
                    [
                        "#e4003a" if boolv else "#00ACFF"
                        for boolv in df_pg["Change"].str.contains("-")
                    ]
                ]
                + [
                    [
                        "#e4003a" if boolv else "#00ACFF"
                        for boolv in df_pg["% Change"].str.contains("-")
                    ]
                ]
            )
            fig = df2img.plot_dataframe(
                df_pg,
                fig_size=(720, (40 + (45 * len(df.index)))),
                col_width=[4, 2, 2, 2],
                tbl_header=cfg.PLT_TBL_HEADER,
                tbl_cells=cfg.PLT_TBL_CELLS,
                font=cfg.PLT_TBL_FONT,
                row_fill_color=cfg.PLT_TBL_ROW_COLORS,
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
            imagefile = helpers.save_image(imagefile, fig)

            if cfg.IMAGES_URL or cfg.IMGUR_CLIENT_ID != "REPLACE_ME":
                image_link = cfg.IMAGES_URL + imagefile
                images_list.append(imagefile)
            else:
                imagefile_save = cfg.IMG_DIR / imagefile
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
            "images_list": images_list,
        }
    else:
        fig = df2img.plot_dataframe(
            df,
            fig_size=(720, (40 + (45 * len(df.index)))),
            col_width=[4, 2, 2, 2],
            tbl_header=cfg.PLT_TBL_HEADER,
            tbl_cells=cfg.PLT_TBL_CELLS,
            font=cfg.PLT_TBL_FONT,
            row_fill_color=cfg.PLT_TBL_ROW_COLORS,
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
        imagefile = helpers.save_image(imagefile, fig)

        output = {
            "title": title,
            "imagefile": imagefile,
        }

    return output
