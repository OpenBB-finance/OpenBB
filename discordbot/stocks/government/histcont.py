import os

import disnake
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import gst_imgur, logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.government import quiverquant_model


async def histcont_command(ctx, ticker=""):
    """Displays historical quarterly-contracts [quiverquant.com]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.gov.histcont %s", ticker)

        if ticker == "":
            raise Exception("A ticker is required")

        # Retrieve Data
        df_contracts = quiverquant_model.get_government_trading(
            "quarter-contracts", ticker=ticker
        )

        if df_contracts.empty:
            logger.debug("No quarterly government contracts found")
            return

        # Output Data
        amounts = df_contracts.sort_values(by=["Year", "Qtr"])["Amount"].values

        qtr = df_contracts.sort_values(by=["Year", "Qtr"])["Qtr"].values
        year = df_contracts.sort_values(by=["Year", "Qtr"])["Year"].values

        quarter_ticks = [
            f"{quarter[0]}" if quarter[1] == 1 else "" for quarter in zip(year, qtr)
        ]
        plt.style.use("seaborn")

        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        ax.plot(np.arange(0, len(amounts)), amounts / 1000, "-*", lw=2, ms=15)

        ax.set_xlim([-0.5, len(amounts) - 0.5])
        ax.set_xticks(np.arange(0, len(amounts)))
        ax.set_xticklabels(quarter_ticks)
        ax.grid()
        ax.set_title(f"Historical Quarterly Government Contracts for {ticker.upper()}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Amount ($1k)")
        fig.tight_layout()

        plt.savefig("gov_histcont.png")
        imagefile = "gov_histcont.png"

        img = Image.open(imagefile)
        print(img.size)
        im_bg = Image.open(cfg.IMG_BG)
        h = img.height + 240
        w = img.width + 520

        img = img.resize((w, h), Image.ANTIALIAS)
        x1 = int(0.5 * im_bg.size[0]) - int(0.5 * img.size[0])
        y1 = int(0.5 * im_bg.size[1]) - int(0.5 * img.size[1])
        x2 = int(0.5 * im_bg.size[0]) + int(0.5 * img.size[0])
        y2 = int(0.5 * im_bg.size[1]) + int(0.5 * img.size[1])
        img = img.convert("RGB")
        im_bg.paste(img, box=(x1 - 5, y1, x2 - 5, y2))
        im_bg.save(imagefile, "PNG", quality=100)

        image = Image.open(imagefile)
        image = autocrop_image(image, 0)
        image.save(imagefile, "PNG", quality=100)

        uploaded_image = gst_imgur.upload_image("gov_histcont.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            logger.debug("Image URL: %s", image_link)
        title = "Stocks: Historical Quarterly Government Contract " + ticker
        embed = disnake.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("gov_histcont.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Stocks: Historical Quarterly Government Contract",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
