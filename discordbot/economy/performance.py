import os

import df2img
import disnake
import numpy as np
import pandas as pd
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.economy import finviz_model


async def performance_command(ctx, economy_group="sector"):
    """Performance of sectors, industry, country [Finviz]"""

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

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("econ-performance %s", economy_group)

        # Select default group
        if not economy_group:
            if cfg.DEBUG:
                logger.debug("Use default economy_group: 'sector'")
            economy_group = "sector"

        # Check for argument
        possible_groups = list(d_economy_group.keys())

        if economy_group not in possible_groups:
            possible_group_list = ", ".join(possible_groups)
            raise Exception(f"Select a valid group from {possible_group_list}")  # nosec

        group = d_economy_group[economy_group]

        # Retrieve data
        df_group = finviz_model.get_valuation_performance_data(group, "performance")

        # Check for argument
        if df_group.empty:
            raise Exception("No available data found")

        # Output data
        df = pd.DataFrame(df_group)
        df = df.replace(np.nan, 0)

        df["Volume"] = df["Volume"] / 1_000_000
        df["Avg Volume"] = df["Avg Volume"] / 1_000_000

        formats = {
            "Perf Month": "{:.2f}",
            "Perf Quart": "{:.2f}",
            "Perf Half": "{:.2f}",
            "Perf Year": "{:.2f}",
            "Perf YTD": "{:.2f}",
            "Avg Volume": "{:.0f}M",
            "Change": "{:.2f}",
            "Volume": "{:.0f}M",
        }
        for col, value in formats.items():
            df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

        df = df.set_axis(
            [
                "Name",
                "Week",
                "Month",
                "3Month",
                "6Month",
                "1Year",
                "YTD",
                "Recom",
                "Avg Vol.",
                "RelVolume",
                "Change",
                "Volume",
            ],
            axis="columns",
        )

        df = df.fillna("")
        df.set_index("Name", inplace=True)

        dindex = len(df.index)
        fig = df2img.plot_dataframe(
            df,
            fig_size=(1500, (40 + (50 * dindex))),
            col_width=[10, 3, 3, 3, 3, 3, 3, 3, 4, 4, 3, 3.5],
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
        imagefile = "econ-performance.png"
        df2img.save_dataframe(fig=fig, filename=imagefile)

        image = Image.open(imagefile)
        image = autocrop_image(image, 0)
        image.save(imagefile, "PNG", quality=100)

        image = disnake.File(imagefile)

        title = f"Economy: [Finviz] Performance {group}"
        embed = disnake.Embed(title=title, colour=cfg.COLOR)
        embed.set_image(url=f"attachment://{imagefile}")
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        os.remove(imagefile)

        await ctx.send(embed=embed, file=image)

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Economy: [Finviz] Performance",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
