import df2img
import numpy as np
import pandas as pd

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.helpers import save_image
from gamestonk_terminal.economy import finviz_model


def valuation_command(economy_group="sector"):
    """Valuation of sectors, industry, country [Finviz]"""

    d_economy_group = {
        "sector": "Sector",
        "industry": "Industry",
        "basic_materials": "Industry (Basic Materials)",
        "communication_services": "Industry (Communication Services)",
        "consumer_cyclical": "Industry (Consumer Cyclical)",
        "consumer_defensive": "Industry (Consumer Defensive)",
        "energy": "Industry (Energy)",
        "financial": "Industry (Financial)",
        "healthcare": "Industry (Healthcare)",
        "industrials": "Industry (Industrials)",
        "real_estate": "Industry (Real Estate)",
        "technology": "Industry (Technology)",
        "utilities": "Industry (Utilities)",
        "country": "Country (U.S. listed stocks only)",
        "capitalization": "Capitalization",
    }

    # Debug user input
    if cfg.DEBUG:
        logger.debug("econ-valuation %s", economy_group)

    # Select default group
    if economy_group == "":
        if cfg.DEBUG:
            logger.debug("Use default economy_group: 'sector'")
        economy_group = "sector"

    # Check for argument
    possible_groups = list(d_economy_group.keys())

    if economy_group not in possible_groups:
        raise Exception(
            f"Select a valid group from {', '.join(possible_groups)}"  # nosec
        )

    group = d_economy_group[economy_group]

    # Retrieve data
    df_group = finviz_model.get_valuation_performance_data(group, "valuation")

    # Check for argument
    if df_group.empty:
        raise Exception("No available data found")

    # Output data
    df = pd.DataFrame(df_group)
    df = df.replace(np.nan, 0)

    df = df.set_axis(
        [
            "Name",
            "MarketCap",
            "P/E",
            "FwdP/E",
            "PEG",
            "P/S",
            "P/B",
            "P/C",
            "P/FCF",
            "EPSpast5Y",
            "EPSnext5Y",
            "Salespast5Y",
            "Change",
            "Volume",
        ],
        axis="columns",
    )

    df["P/E"] = pd.to_numeric(df["P/E"].astype(float))
    df["FwdP/E"] = pd.to_numeric(df["FwdP/E"].astype(float))
    df["EPSpast5Y"] = pd.to_numeric(df["EPSpast5Y"].astype(float))
    df["EPSnext5Y"] = pd.to_numeric(df["EPSnext5Y"].astype(float))
    df["Salespast5Y"] = pd.to_numeric(df["Salespast5Y"].astype(float))
    df["Volume"] = pd.to_numeric(df["Volume"].astype(float))
    df["Volume"] = df["Volume"] / 1_000_000

    formats = {
        "P/E": "{:.2f}",
        "FwdP/E": "{:.2f}",
        "EPSpast5Y": "{:.2f}",
        "EPSnext5Y": "{:.2f}",
        "Salespast5Y": "{:.2f}",
        "Change": "{:.2f}",
        "Volume": "{:.0f}M",
    }
    for col, value in formats.items():
        df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

    df = df.fillna("")
    df.set_index("Name", inplace=True)

    dindex = len(df.index)
    fig = df2img.plot_dataframe(
        df,
        fig_size=(1600, (40 + (50 * dindex))),
        col_width=[12, 5, 4, 4, 4, 4, 4, 4, 4, 6, 6, 6, 4, 4],
        tbl_cells=dict(
            align=["left", "center"],
            height=35,
        ),
        template="plotly_dark",
        font=dict(
            family="Consolas",
            size=20,
        ),
        paper_bgcolor="rgba(0, 0, 0, 0)",
    )
    imagefile = save_image("econ-valuation.png", fig)
    return {
        "title": "Economy: [Finviz] Valuation",
        "imagefile": imagefile,
    }
