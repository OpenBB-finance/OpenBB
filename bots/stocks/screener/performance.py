import difflib
import logging
import os

import df2img
import disnake
import pandas as pd

import bots.config_discordbot as cfg
from bots import helpers
from bots.config_discordbot import gst_imgur
from bots.menus.menu import Menu
from bots.stocks.screener import screener_options as so
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import lambda_long_number_format
from gamestonk_terminal.stocks.screener.finviz_model import get_screener_data

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def performance_command(
    preset: str = "template", sort: str = "", limit: int = 5, ascend: bool = False
):
    """Displays stocks and sort by performance categories [Finviz]"""

    # Check for argument
    if preset == "template" or preset not in so.all_presets:
        raise Exception("Invalid preset selected!")

    # Debug
    if cfg.DEBUG:
        logger.debug("scr-performance %s %s %s %s", preset, sort, limit, ascend)

    # Check for argument
    if limit < 0:
        raise Exception("Number has to be above 0")

    # Output Data
    df_screen = get_screener_data(
        preset,
        "performance",
        limit,
        ascend,
    )

    d_cols_to_sort = {
        "performance": [
            "Ticker",
            "Perf Week",
            "Perf Month",
            "Perf Quart",
            "Perf Half",
            "Perf Year",
            "Perf YTD",
            "Volatility W",
            "Volatility M",
            "Recom",
            "Avg Volume",
            "Rel Volume",
            "Price",
            "Change",
            "Volume",
        ],
    }
    title = "Stocks: [Finviz] Performance Screener"
    if isinstance(df_screen, pd.DataFrame):
        if df_screen.empty:
            raise Exception("No data found.")

        df_screen = df_screen.dropna(axis="columns", how="all")

        if sort:
            if sort in d_cols_to_sort["performance"]:
                df_screen = df_screen.sort_values(
                    by=sort,
                    ascending=ascend,
                    na_position="last",
                )
            else:
                similar_cmd = difflib.get_close_matches(
                    " ".join(sort),
                    d_cols_to_sort["performance"],
                    n=1,
                    cutoff=0.7,
                )
                if similar_cmd:
                    df_screen = df_screen.sort_values(
                        by=[similar_cmd[0]],
                        ascending=ascend,
                        na_position="last",
                    )
                else:
                    raise ValueError(
                        "Wrong sort column provided! Provide one of these:"
                        f"{', '.join(d_cols_to_sort['performance'])}"
                    )

    df_screen.set_index("Ticker", inplace=True)
    df_screen = df_screen.head(n=limit)
    df_screen = df_screen.fillna("-")
    dindex = len(df_screen.index)
    df_screen = df_screen.applymap(lambda x: lambda_long_number_format(x, 2))

    if dindex > 5:
        embeds: list = []
        # Output
        i, i2, end = 0, 0, 5
        df_pg, embeds_img, images_list = pd.DataFrame(), [], []
        while i < dindex:
            df_pg = df_screen.iloc[i:end]
            df_pg.append(df_pg)
            fig = df2img.plot_dataframe(
                df_pg.transpose(),
                fig_size=(800, 720),
                col_width=[2, 1.5],
                tbl_header=cfg.PLT_TBL_HEADER,
                tbl_cells=cfg.PLT_TBL_CELLS,
                font=cfg.PLT_TBL_FONT,
                row_fill_color=cfg.PLT_TBL_ROW_COLORS,
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            fig.update_traces(cells=(dict(align=["center", "right"])))
            imagefile = "scr_performance.png"
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
            i += 5
            end += 5

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
            df_screen.transpose(),
            fig_size=(800, 720),
            col_width=[2, 1.5],
            tbl_header=cfg.PLT_TBL_HEADER,
            tbl_cells=cfg.PLT_TBL_CELLS,
            font=cfg.PLT_TBL_FONT,
            row_fill_color=cfg.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(cells=(dict(align=["center", "right"])))
        imagefile = helpers.save_image("scr_performance.png", fig)

        output = {
            "title": title,
            "imagefile": imagefile,
        }

    return output
