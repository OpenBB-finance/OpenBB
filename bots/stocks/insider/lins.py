import logging

import disnake
import pandas as pd

from bots import imps
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.insider import finviz_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def lins_command(ticker: str = "", num: int = 30):
    """Display insider activity for a given stock ticker. [Source: Finviz]

    Parameters
    ----------
    ticker : Stock Ticker
    num : Number of latest insider activity to display
    """

    # Debug
    if imps.DEBUG:
        logger.debug("disc-lins %s", num)

    d_finviz_insider = finviz_model.get_last_insider_activity(ticker)

    df = pd.DataFrame.from_dict(d_finviz_insider)
    df.set_index("Date", inplace=True)

    df = df[
        [
            "Relationship",
            "Transaction",
            "#Shares",
            "Cost",
            "Value ($)",
            "#Shares Total",
            "Insider Trading",
            "SEC Form 4",
        ]
    ]

    df = df.head(num)
    df = df.replace(to_replace="Option Exercise", value="Opt Ex.", regex=True)

    title = f"Insider Trading for {ticker.upper()}"

    embeds: list = []

    i, i2, end = 0, 0, 15
    df_pg, embeds_img, images_list = [], [], []

    while i < len(df.index):
        df_pg = df.iloc[i:end]
        df_pg.append(df_pg)
        fig = imps.plot_df(
            df_pg,
            fig_size=(1400, (40 + (45 * 20))),
            col_width=[4, 10, 4, 4, 3.5, 5.3, 6, 8, 7],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(
            cells=(
                dict(
                    align=[
                        "center",
                        "center",
                        "center",
                        "right",
                        "right",
                        "right",
                        "right",
                        "center",
                    ]
                )
            )
        )
        imagefile = imps.save_image("disc-insider.png", fig)

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

    return {
        "view": imps.Menu,
        "title": title,
        "embed": embeds,
        "choices": choices,
        "embeds_img": embeds_img,
        "images_list": images_list,
    }
