import os

import disnake
import pandas as pd
from matplotlib import pyplot as plt
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import gst_imgur, logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.government import quiverquant_model


async def toplobbying_command(ctx, num: int = 10, raw: bool = False):
    """Displays top lobbying firms [quiverquant.com]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.gov.toplobbying %s %s", num, raw)

        # Retrieve Data
        df_lobbying = quiverquant_model.get_government_trading("corporate-lobbying")

        if df_lobbying.empty:
            raise Exception("No corporate lobbying found")

        df_lobbying["Amount"] = df_lobbying.Amount.astype(float).fillna(0) / 100_000

        lobbying_by_ticker = pd.DataFrame(
            df_lobbying.groupby("Ticker")["Amount"].agg("sum")
        ).sort_values(by="Amount", ascending=False)
        plt.style.use("seaborn")
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        lobbying_by_ticker.head(num).plot(kind="bar", ax=ax)
        ax.set_xlabel("Ticker")
        ax.set_ylabel("Total Amount ($100k)")
        ax.set_title(f"Corporate Lobbying Spent since {df_lobbying['Date'].min()}")
        fig.tight_layout()

        plt.savefig("ta_toplobbying.png")
        imagefile = "ta_toplobbying.png"

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

        uploaded_image = gst_imgur.upload_image("ta_toplobbying.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            logger.debug("Image URL: %s", image_link)
        title = "Stocks: [quiverquant.com] Top Lobbying Firms"
        if raw:
            description = lobbying_by_ticker.head(num).to_string()
            embed = disnake.Embed(
                title=title, description=description, colour=cfg.COLOR
            )
        else:
            embed = disnake.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_toplobbying.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Stocks: [quiverquant.com] Top Lobbying Firms",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
