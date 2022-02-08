import os

import df2img
import disnake
import numpy as np
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.stocks.due_diligence import finviz_model


async def analyst_command(ctx, ticker=""):
    """Displays analyst recommendations [Finviz]"""

    try:

        # Debug
        if cfg.DEBUG:
            logger.debug("!stocks.dd.analyst %s", ticker)

        # Check for argument
        if not ticker:
            raise Exception("Stock ticker is required")

        df = finviz_model.get_analyst_data(ticker)
        df = df.replace(np.nan, 0)
        df.index.names = ["Date"]
        df = df.rename(
            columns={
                "category": "Category",
                "analyst": "Analyst",
                "rating": "Rating",
                "target": "Target",
                "target_from": "Target From",
                "target_to": "Target To",
            }
        )

        dindex = len(df.index)
        fig = df2img.plot_dataframe(
            df,
            fig_size=(1500, (40 + (40 * dindex))),
            col_width=[5, 5, 8, 14, 5, 5, 5],
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
        imagefile = "dd-analyst.png"

        df2img.save_dataframe(fig=fig, filename=imagefile)
        image = Image.open(imagefile)
        image = autocrop_image(image, 0)
        image.save(imagefile, "PNG", quality=100)

        image = disnake.File(imagefile)

        title = f"Stocks: [Finviz] Analyst Recommendations {ticker.upper()}"
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
            title="ERROR Stocks: [Finviz] Analyst Recommendations",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
