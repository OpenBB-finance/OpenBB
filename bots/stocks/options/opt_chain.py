import logging
import os

import df2img
import disnake
import numpy as np
import pandas as pd

import bots.config_discordbot as cfg
from bots import helpers
from bots.config_discordbot import gst_imgur
from bots.menus.menu import Menu
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.stocks.options import yfinance_model

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def chain_command(
    ticker: str = None,
    expiry: str = None,
    opt_type: str = None,
    min_sp: float = None,
    max_sp: float = None,
):
    """Show calls/puts for given ticker and expiration"""

    # Debug
    if cfg.DEBUG:
        logger.debug(
            "opt chain %s %s %s %s %s", ticker, expiry, opt_type, min_sp, max_sp
        )

    # Check for argument
    if not ticker:
        raise Exception("Stock ticker is required")

    dates = yfinance_model.option_expirations(ticker)

    if not dates:
        raise Exception("Stock ticker is invalid")

    options = yfinance_model.get_option_chain(ticker, str(expiry))
    calls_df = options.calls.fillna(0)
    puts_df = options.puts.fillna(0)

    column_map = {"openInterest": "oi", "volume": "vol", "impliedVolatility": "iv"}
    columns = [
        "strike",
        "bid",
        "ask",
        "volume",
        "openInterest",
        "impliedVolatility",
    ]

    if opt_type == "Calls":
        df = calls_df[columns].rename(columns=column_map)
    if opt_type == "Puts":
        df = puts_df[columns].rename(columns=column_map)

    min_strike = np.percentile(df["strike"], 1)
    max_strike = np.percentile(df["strike"], 100)

    if min_sp:
        min_strike = min_sp
    if max_sp:
        max_strike = max_sp
        if min_sp > max_sp:  # type: ignore
            min_sp, max_sp = max_strike, min_strike

    df = df[df["strike"] >= min_strike]
    df = df[df["strike"] <= max_strike]

    df["iv"] = pd.to_numeric(df["iv"].astype(float))

    formats = {"iv": "{:.2f}"}
    for col, f in formats.items():
        df[col] = df[col].map(lambda x: f.format(x))  # pylint: disable=W0640
    df.set_index("strike", inplace=True)

    title = (
        f"Stocks: {opt_type} Option Chain for {ticker.upper()} on {expiry} [yfinance]"
    )

    embeds: list = []
    # Output
    i, i2, end = 0, 0, 20
    df_pg, embeds_img, images_list = [], [], []
    while i < len(df.index):
        df_pg = df.iloc[i:end]
        df_pg.append(df_pg)
        fig = df2img.plot_dataframe(
            df_pg,
            fig_size=(1000, (40 + (40 * 20))),
            col_width=[3, 3, 3, 3],
            tbl_header=cfg.PLT_TBL_HEADER,
            tbl_cells=cfg.PLT_TBL_CELLS,
            font=cfg.PLT_TBL_FONT,
            row_fill_color=cfg.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        imagefile = "opt-chain.png"
        imagefile = helpers.save_image(imagefile, fig)

        if cfg.IMAGES_URL or cfg.IMGUR_CLIENT_ID != "REPLACE_ME":
            image_link = cfg.IMAGES_URL + imagefile
            images_list.append(imagefile)
        else:
            imagefile_save = cfg.IMG_DIR / imagefile
            uploaded_image = gst_imgur.upload_image(imagefile_save, title="something")
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
        i += 20
        end += 20

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
        "images_list": images_list,
    }
