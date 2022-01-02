import os
import io
import discord
import matplotlib.pyplot as plt
from PIL import Image

from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.technical_analysis import finviz_model
from gamestonk_terminal.config_plot import PLOT_DPI

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur


async def view_command(ctx, ticker=""):
    """Displays image from Finviz [Finviz]"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.ta.view {ticker}")

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")
        image_data = finviz_model.get_finviz_image(ticker)
        dataBytesIO = io.BytesIO(image_data)
        im = Image.open(dataBytesIO)

        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax.set_axis_off()
        fig.subplots_adjust(left=0, right=1, top=1, bottom=0)

        plt.imshow(im)

        plt.savefig("ta_view.png")
        uploaded_image = gst_imgur.upload_image("ta_view.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = "Stocks: [Finviz] Trendlines & Data " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_view.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: [Finviz] Trendlines & Data",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
