import logging

import disnake
import pandas as pd

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.due_diligence import ark_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def arktrades_command(ticker: str = "", num: int = 30):
    """Displays trades made by ark [cathiesark.com]"""

    # Debug user input
    if imps.DEBUG:
        logger.debug("dd arktrades %s", ticker)

    if ticker:
        ark_holdings = ark_model.get_ark_trades_by_ticker(ticker)

    if ark_holdings.empty:
        raise Exception(
            "Issue getting data from cathiesark.com. Likely no trades found.\n"
        )

    ark_holdings["Total"] = ark_holdings["Total"] / 1_000_000
    ark_holdings.rename(
        columns={
            "shares": "Shares",
            "direction": "B/S",
            "weight": "Weight",
            "fund": "Fund",
        },
        inplace=True,
    )
    ark_holdings = ark_holdings.drop(
        columns=["ticker", "everything.profile.companyName"]
    )

    ark_holdings.index = pd.Series(ark_holdings.index).apply(
        lambda x: x.strftime("%Y-%m-%d")
    )

    df = ark_holdings.head(num)
    df = df.fillna(0)
    formats = {"Weight": "{:.2f}", "Close": "${:.2f}", "Total": "{:.2f}M"}
    for col, f in formats.items():
        df[col] = df[col].map(lambda x: f.format(x))  # pylint: disable=W0640

    title = f"Stocks: [cathiesark.com] {ticker.upper()} Trades by Ark"

    embeds: list = []

    i, i2, end = 0, 0, 15
    df_pg, embeds_img, images_list = [], [], []

    while i < len(df.index):
        df_pg = df.iloc[i:end]
        df_pg.append(df_pg)
        fig = imps.plot_df(
            df_pg,
            fig_size=(900, (40 + (40 * 20))),
            col_width=[5, 8, 4, 4, 3, 5, 5],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        imagefile = imps.save_image("dd-arktrades.png", fig)

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
