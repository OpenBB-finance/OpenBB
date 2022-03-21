import logging
import os

import disnake
import pandas as pd

from bots import imps
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import lambda_long_number_format
from gamestonk_terminal.stocks.discovery import yahoofinance_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def gainers_command(num: int = 10):
    """Show top gainers [Yahoo Finance]"""

    # Debug user input
    if imps.DEBUG:
        logger.debug("disc gainers %s", num)

    # Check for argument
    if num < 0:
        raise Exception("Number has to be above 0")

    # Retrieve data
    df = yahoofinance_model.get_gainers().head(num)

    if df.empty:
        raise Exception("No available data found")

    # Debug user output
    if imps.DEBUG:
        logger.debug(df.to_string())

    # Output data
    title = "Stocks: Top Gainers [Yahoo Finance]"
    df.dropna(how="all", axis=1, inplace=True)
    df = df.replace(float("NaN"), "")

    # Convert and format: str into float
    for col in ["Volume", "Avg Vol (3 month)"]:
        df[col] = [imps.unit_finder.sub(imps.unit_replacer, x) for x in df[col]]
        df[col] = pd.to_numeric(df[col].astype(float))
        df[col] = df[col].map(lambda x: lambda_long_number_format(x, 2))

    for col in ["Price (Intraday)", "Change"]:
        df[col] = df[col].apply(lambda x: f"${x:.2f}")

    # Format "%% Change" columns then combine it into "Change"
    df["% Change"] = df.apply(lambda x: f"(<b>{x['% Change']}</b>)", axis=1)
    df["Change"] = df.apply(lambda x: f"{x['Change']} {x['% Change']}", axis=1)

    # Combine "Volume" columns
    df["Volume"] = df.apply(
        lambda x: f"{x['Volume']:>8} (<b>{x['Avg Vol (3 month)']:>8}</b>)",
        axis=1,
    )

    df = df.drop(columns=["PE Ratio (TTM)", "% Change", "Avg Vol (3 month)"])
    df.set_index("Symbol", inplace=True)
    df.columns = [
        "Name",
        "Price",
        "Change",
        "Volume (Avg)",
        "Mkt Cap",
    ]

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
                fig_size=(950, (45 * dindex)),
                col_width=[2.1, 10, 2.5, 5, 5.2, 3],
                tbl_header=imps.PLT_TBL_HEADER,
                tbl_cells=imps.PLT_TBL_CELLS,
                font=imps.PLT_TBL_FONT,
                row_fill_color=imps.PLT_TBL_ROW_COLORS,
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            fig.update_traces(cells=(dict(align=["center", "center", "right"])))
            imagefile = "disc-gainers.png"
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
            fig_size=(950, (45 * dindex)),
            col_width=[2.1, 10, 2.5, 5, 5.2, 3],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(cells=(dict(align=["center", "center", "right"])))
        imagefile = imps.save_image("disc-gainers.png", fig)

        output = {
            "title": title,
            "imagefile": imagefile,
        }

    return output
