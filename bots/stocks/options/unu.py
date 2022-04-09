import logging

import disnake
import numpy as np
import pandas as pd
import requests

from bots import imps
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_user_agent

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
def unu_command(num: int = 20):
    """Unusual Options"""

    # Debug
    if imps.DEBUG:
        logger.debug("opt unu %s", num)

    pages = np.arange(0, num // 20 + 1)
    data_list = []
    for page_num in pages:

        r = requests.get(
            f"https://app.fdscanner.com/api2/unusualvolume?p=0&page_size=20&page={int(page_num)}",
            headers={"User-Agent": get_user_agent()},
        )

        if r.status_code != 200:
            logger.debug("Error in fdscanner request")
            return pd.DataFrame(), "request error"

        data_list.append(r.json())

    ticker, expiry, option_strike, option_type, ask, bid, oi, vol, voi = (
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
        [],
    )
    for data in data_list:
        for entry in data["data"]:
            ticker.append(entry["tk"])
            expiry.append(entry["expiry"])
            option_strike.append(float(entry["s"]))
            option_type.append("Put" if entry["t"] == "P" else "Call")
            ask.append(entry["a"])
            bid.append(entry["b"])
            oi.append(entry["oi"])
            vol.append(entry["v"])
            voi.append(entry["vol/oi"])

    df = pd.DataFrame(
        {
            "Ticker": ticker,
            "Exp": expiry,
            "Strike": option_strike,
            "Type": option_type,
            "Vol/OI": voi,
            "Vol": vol,
            "OI": oi,
        }
    )

    if df.empty:
        raise Exception("No data found!\n")

    title = "Unusual Options"

    df.set_index("Ticker", inplace=True)
    dindex = len(df.index)
    if dindex > 15:
        embeds: list = []
        # Output
        i, i2, end = 0, 0, 20
        df_pg, embeds_img, images_list = [], [], []
        while i < dindex:
            df_pg = df.iloc[i:end]
            df_pg.append(df_pg)
            fig = imps.plot_df(
                df_pg,
                fig_size=(650, (40 + (40 * dindex))),
                col_width=[3, 4, 3, 2.5, 2.5, 2, 2],
                tbl_header=imps.PLT_TBL_HEADER,
                tbl_cells=imps.PLT_TBL_CELLS,
                font=imps.PLT_TBL_FONT,
                row_fill_color=imps.PLT_TBL_ROW_COLORS,
                paper_bgcolor="rgba(0, 0, 0, 0)",
            )
            fig.update_traces(
                cells=(dict(align=["center", "center", "right", "center", "right"]))
            )
            imagefile = "opt-unu.png"
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
            fig_size=(650, (40 + (40 * dindex))),
            col_width=[3, 4, 3, 2.5, 2.5, 2, 2],
            tbl_header=imps.PLT_TBL_HEADER,
            tbl_cells=imps.PLT_TBL_CELLS,
            font=imps.PLT_TBL_FONT,
            row_fill_color=imps.PLT_TBL_ROW_COLORS,
            paper_bgcolor="rgba(0, 0, 0, 0)",
        )
        fig.update_traces(
            cells=(dict(align=["center", "center", "right", "center", "right"]))
        )
        imagefile = imps.save_image("opt-unu.png", fig)

        output = {
            "title": "Unusual Options",
            "imagefile": imagefile,
        }

    return output
