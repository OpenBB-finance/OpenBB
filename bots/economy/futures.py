import df2img
import pandas as pd
import yahoo_fin.stock_info as si

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.helpers import save_image


def futures_command():
    """Futures [Yahoo Finance]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug("futures")

    # Retrieve data
    df = si.get_futures()

    # Check for argument
    if df.empty:
        raise Exception("No available data found")

    df["Last Price"] = pd.to_numeric(df["Last Price"].astype(float))
    df["Change"] = pd.to_numeric(df["Change"].astype(float))

    formats = {"Last Price": "${:.2f}", "Change": "${:.2f}"}
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    df = df.iloc[:5]
    df["Name"] = (
        df["Name"]
        .replace(
            to_replace=[
                "Mar",
                "Apr",
                "22",
                "\\$5",
                ",-",
                ".-",
                "Mini",
                "mini",
                "Futures",
                "Futur",
                "Indus",
            ],
            value="",
            regex=True,
        )
        .str.strip()
    )

    df = df.fillna("")
    df.drop(columns="Symbol")
    df = df.rename(columns={"Name": " "})
    df.set_index(" ", inplace=True)

    df = df[["Last Price", "Change", "% Change"]]

    dindex = len(df.index)
    fig = df2img.plot_dataframe(
        df,
        fig_size=(800, (40 + (45 * dindex))),
        col_width=[5, 2, 2, 2],
        tbl_header=cfg.PLT_TBL_HEADER,
        tbl_cells=cfg.PLT_TBL_CELLS,
        font=cfg.PLT_TBL_FONT,
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    fig.update_traces(cells=(dict(align=["left", "center"])))
    imagefile = save_image("econ-futures.png", fig)
    return {"title": "Economy: [WSJ] Futures/Commodities", "imagefile": imagefile}
