import logging

import disnake
import numpy as np
import pandas as pd

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.stocks.options import yfinance_model

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
    if imps.DEBUG:
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
    df.columns = df.columns.str.capitalize()
    df.set_index("Strike", inplace=True)

    title = (
        f"Stocks: {opt_type} Option Chain for {ticker.upper()} on\n{expiry} [yfinance]"
    )

    embeds: list = []
    # Output
    i, i2, end = 0, 0, 20
    df_pg, embeds_img, images_list = [], [], []
    while i < len(df.index):
        df_pg = df.iloc[i:end]
        df_pg.append(df_pg)
        fig = imps.plot_df(
            df_pg,
            fig_size=(570, (40 + (40 * 20))),
            col_width=[3.1, 3.1, 3.1, 3.5],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(cells=(dict(align=["center", "right"])))
        imagefile = "opt-chain.png"
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
        i += 20
        end += 20

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
