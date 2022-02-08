import os

import df2img
import disnake
import pandas as pd
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.economy import wsj_model


async def overview_command(ctx):
    """Market data overview [Wall St. Journal]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("econ-overview")

        # Retrieve data
        df = wsj_model.market_overview()

        # Check for argument
        if df.empty:
            raise Exception("No available data found")

        df["Price"] = pd.to_numeric(df["Price"].astype(float))
        df["Chg"] = pd.to_numeric(df["Chg"].astype(float))
        df["%Chg"] = pd.to_numeric(df["%Chg"].astype(float))

        formats = {"Price": "${:.2f}", "Chg": "${:.2f}", "%Chg": "{:.2f}%"}
        for col, v in formats.items():
            df[col] = df[col].map(lambda x: v.format(x))  # pylint: disable=W0640

        df = df[
            [
                "Price",
                "Chg",
                "%Chg",
            ]
        ]

        df = df.fillna("")
        df.set_index(" ", inplace=True)

        dindex = len(df.index)
        fig = df2img.plot_dataframe(
            df,
            fig_size=(800, (40 + (40 * dindex))),
            col_width=[8, 3, 3],
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
        imagefile = "econ-indices.png"
        df2img.save_dataframe(fig=fig, filename=imagefile)

        image = Image.open(imagefile)
        image = autocrop_image(image, 0)
        image.save(imagefile, "PNG", quality=100)

        image = disnake.File(imagefile)

        title = "Economy: [WSJ] Market Overview"
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
            title="ERROR Economy: [WSJ] Market Overview",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
