import logging

import disnake

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import lambda_long_number_format
from openbb_terminal.stocks.dark_pool_shorts import stockgrid_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def pos_command(sort="dpp_dollar", ascending: bool = False, num: int = 10):
    """Dark pool short position [Stockgrid]"""

    # Debug user input
    if imps.DEBUG:
        logger.debug("dps-pos %s %s", sort, num)

    # Check for argument
    possible_sorts = ("sv", "sv_pct", "nsv", "nsv_dollar", "dpp", "dpp_dollar")

    if sort not in possible_sorts:
        raise Exception(f"The possible sorts are: {', '.join(possible_sorts)}")

    if num < 0:
        raise Exception("Number has to be above 0")

    # Retrieve data
    df = stockgrid_model.get_dark_pool_short_positions(sort, ascending)

    if df.empty:
        raise Exception("No available data found")

    df = df.iloc[:num]

    # Debug user output
    if imps.DEBUG:
        logger.debug(df.to_string())

    # Output data
    title = "Stocks: [Stockgrid] Dark Pool Short Position"
    df = df.applymap(lambda x: lambda_long_number_format(x, 2))
    df = df.drop(columns=["Date"])
    formats = {
        "Short Volume %": "{}%",
        "Net Short Volume $": "${}",
        "Dark Pools Position $": "${}",
    }
    for col, f in formats.items():
        df[col] = df[col].map(lambda x: f.format(x))  # pylint: disable=W0640

    df["Short Volume"] = df.apply(
        lambda x: f"{x['Short Volume']}  (<b>{x['Short Volume %']}</b>)", axis=1
    )
    df["Net Short Volume"] = df.apply(
        lambda x: f"{x['Net Short Volume']:>9} (<b>{x['Net Short Volume $']:>9}</b>)",
        axis=1,
    )
    df["Dark Pools Position"] = df.apply(
        lambda x: f"{x['Dark Pools Position']:>9}  (<b>{x['Dark Pools Position $']:>9}</b>)",
        axis=1,
    )
    df = df.drop(
        columns=["Short Volume %", "Net Short Volume $", "Dark Pools Position $"]
    )
    df.columns = [
        "Ticker",
        "Short Vol.",
        "Net Short Vol.",
        "DP Position",
    ]
    df.set_index("Ticker", inplace=True)
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
                fig_size=(720, (40 * dindex)),
                col_width=[2, 4, 4, 4],
                tbl_header=imps.PLT_TBL_HEADER,
                tbl_cells=imps.PLT_TBL_CELLS,
                font=imps.PLT_TBL_FONT,
                row_fill_color=imps.PLT_TBL_ROW_COLORS,
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            fig.update_traces(cells=(dict(align=["center", "right"])))
            imagefile = "dps-pos.png"
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
            fig_size=(720, (40 * dindex)),
            col_width=[2, 4, 4, 4],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(cells=(dict(align=["center", "right"])))
        imagefile = imps.save_image("dps-pos.png", fig)

        output = {
            "title": title,
            "imagefile": imagefile,
        }

    return output
