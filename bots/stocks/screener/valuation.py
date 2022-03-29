import difflib
import logging

import disnake
import pandas as pd

from bots import imps
from bots.stocks.screener import screener_options as so
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import lambda_long_number_format
from openbb_terminal.stocks.screener.finviz_model import get_screener_data

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def valuation_command(
    preset: str = "template", sort: str = "", limit: int = 5, ascend: bool = False
):
    """Displays results from chosen preset focusing on valuation metrics [Finviz]"""

    # Check for argument
    if preset == "template" or preset not in so.all_presets:
        raise Exception("Invalid preset selected!")

    # Debug
    if imps.DEBUG:
        logger.debug("scr-valuation %s %s %s %s", preset, sort, limit, ascend)

    # Check for argument
    if limit < 0:
        raise Exception("Number has to be above 0")

    # Output Data
    df_screen = get_screener_data(
        preset,
        "valuation",
        limit,
        ascend,
    )

    title = "Stocks: [Finviz] Valuation Screener"
    if isinstance(df_screen, pd.DataFrame):
        if df_screen.empty:
            raise Exception("No data found.")

        df_screen = df_screen.dropna(axis="columns", how="all")

        if sort:
            if sort in so.d_cols_to_sort["valuation"]:
                df_screen = df_screen.sort_values(
                    by=sort,
                    ascending=ascend,
                    na_position="last",
                )
            else:
                similar_cmd = difflib.get_close_matches(
                    " ".join(sort),
                    so.d_cols_to_sort["valuation"],
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
                        f"Wrong sort column provided! Select from: {', '.join(so.d_cols_to_sort['valuation'])}"
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
            fig = imps.plot_df(
                df_pg.transpose(),
                fig_size=(800, 720),
                col_width=[2, 1.5],
                tbl_header=imps.PLT_TBL_HEADER,
                tbl_cells=imps.PLT_TBL_CELLS,
                font=imps.PLT_TBL_FONT,
                row_fill_color=imps.PLT_TBL_ROW_COLORS,
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            fig.update_traces(cells=(dict(align=["center", "right"])))
            imagefile = "scr_valuation.png"
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
            i += 5
            end += 5

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
            df_screen.transpose(),
            fig_size=(800, 720),
            col_width=[2, 1.5],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(cells=(dict(align=["center", "right"])))
        imagefile = imps.save_image("scr_valuation.png", fig)

        output = {
            "title": title,
            "imagefile": imagefile,
        }

    return output
