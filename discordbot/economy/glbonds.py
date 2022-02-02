import os

import df2img
import disnake
import pandas as pd
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.economy import wsj_model


async def glbonds_command(ctx):
    """Global bonds overview [Wall St. Journal]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("econ-glbonds")

        # Retrieve data
        df = wsj_model.global_bonds()

        # Check for argument
        if df.empty:
            raise Exception("No available data found")

        df["Rate (%)"] = pd.to_numeric(df["Rate (%)"].astype(float))
        df["Yld (%)"] = pd.to_numeric(df["Yld (%)"].astype(float))
        df["Yld Chg (%)"] = pd.to_numeric(df["Yld Chg (%)"].astype(float))

        formats = {
            "Rate (%)": "{:.2f}%",
            "Yld (%)": "{:.2f}%",
            "Yld Chg (%)": "{:.2f}%",
        }
        for col, value in formats.items():
            df[col] = df[col].map(lambda x: value.format(x))  # pylint: disable=W0640

        # Debug user output
        if cfg.DEBUG:
            logger.debug(df.to_string())

        df = df.fillna("")
        df = df.replace(
            ("Government Bond", "10 Year"), ("Gov .Bond", "10yr"), regex=True
        )
        df.set_index(" ", inplace=True)
        df = df.set_axis(
            [
                "Rate",
                "Yld",
                "Yld Chg",
            ],
            axis="columns",
        )
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
        imagefile = "econ-glbonds.png"
        df2img.save_dataframe(fig=fig, filename=imagefile)
        image = Image.open(imagefile)
        image = autocrop_image(image, 0)
        image.save(imagefile, "PNG", quality=100)
        image = disnake.File(imagefile)
        title = "Economy: [WSJ] Global Bonds"
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
            title="ERROR Economy: [WSJ] Global Bonds",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
