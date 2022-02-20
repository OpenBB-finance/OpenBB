import df2img
import numpy as np
import pandas as pd
import requests

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.helpers import save_image
from gamestonk_terminal.helper_funcs import get_user_agent


def unu_command(num: int = None):
    """Unusual Options"""

    # Debug
    if cfg.DEBUG:
        logger.debug("opt-unu %s", num)

    # Check for argument
    if num is None:
        num = 10

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

    df = df.replace({"2021-", "2022-"}, "", regex=True)
    df.set_index("Ticker", inplace=True)
    dindex = len(df.index)
    fig = df2img.plot_dataframe(
        df,
        fig_size=(800, (40 + (40 * dindex))),
        col_width=[3, 3, 3, 3, 3, 3, 3],
        tbl_cells=dict(
            align="left",
            height=35,
        ),
        template="plotly_dark",
        font=dict(
            family="Consolas",
            size=20,
        ),
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = save_image("opt-unu.png", fig)

    return {
        "title": "Unusual Options",
        "imagefile": imagefile,
    }
