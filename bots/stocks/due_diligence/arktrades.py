import os

import df2img
import disnake
import pandas as pd

import bots.config_discordbot as cfg
from bots.config_discordbot import gst_imgur, logger
from bots.helpers import save_image
from bots.menus.menu import Menu
from gamestonk_terminal.stocks.due_diligence import ark_model


def arktrades_command(ticker: str = "", num: int = 10):
    """Displays trades made by ark [cathiesark.com]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("dd-arktrades %s", ticker)

    if ticker:
        ark_holdings = ark_model.get_ark_trades_by_ticker(ticker)

    if ark_holdings.empty:
        raise Exception(
            "Issue getting data from cathiesark.com. Likely no trades found.\n"
        )

    ark_holdings["Total"] = ark_holdings["Total"] / 1_000_000
    ark_holdings.rename(columns={"direction": "B/S", "weight": "F %"}, inplace=True)
    ark_holdings = ark_holdings.drop(
        columns=["ticker", "everything.profile.companyName"]
    )

    ark_holdings.index = pd.Series(ark_holdings.index).apply(
        lambda x: x.strftime("%Y-%m-%d")
    )

    df = ark_holdings.head(num)
    df = df.fillna(0)
    dindex = len(df.head(num).index)
    formats = {"Close": "{:.2f}", "Total": "{:.2f}"}
    for col, f in formats.items():
        df[col] = df[col].map(lambda x: f.format(x))  # pylint: disable=W0640

    title = f"Stocks: [cathiesark.com] {ticker.upper()} Trades by Ark"

    embeds: list = []

    i, i2, end = 0, 0, 20
    df_pg = []
    embeds_img = []
    dindex = len(df.index)
    while i < dindex:
        df_pg = df.iloc[i:end]
        df_pg.append(df_pg)
        fig = df2img.plot_dataframe(
            df_pg,
            fig_size=(900, (40 + (40 * 20))),
            col_width=[5, 10, 4, 4, 3, 4, 5],
            tbl_cells=dict(
                height=35,
            ),
            font=dict(
                family="Consolas",
                size=20,
            ),
            template="plotly_dark",
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        imagefile = save_image(f"dd-arktrades{i}.png", fig)

        uploaded_image = gst_imgur.upload_image(imagefile, title="something")
        image_link = uploaded_image.link
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
        i += 20
        end += 20
        os.remove(imagefile)

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

    return {
        "view": Menu,
        "title": title,
        "embed": embeds,
        "choices": choices,
        "embeds_img": embeds_img,
    }
