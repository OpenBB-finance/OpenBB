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


async def contracts_command(
    ctx, ticker: str = "", past_transaction_days: int = 10, raw: bool = False
):
    """Displays contracts associated with tickers [quiverquant.com]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug(
                "!stocks.gov.contracts %s %s %s", ticker, past_transaction_days, raw
            )

        if ticker == "":
            raise Exception("A ticker is required")

        # Retrieve Data
        df_contracts = quiverquant_model.get_government_trading("contracts", ticker)

        if df_contracts.empty:
            raise Exception("No government contracts found")

        # Output Data
        df_contracts["Date"] = pd.to_datetime(df_contracts["Date"]).dt.date

        df_contracts = df_contracts[
            df_contracts["Date"].isin(
                df_contracts["Date"].unique()[:past_transaction_days]
            )
        ]

        df_contracts.drop_duplicates(inplace=True)
        plt.style.use("seaborn")

        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        df_contracts.groupby("Date").sum().div(1000).plot(kind="bar", rot=0, ax=ax)
        ax.set_ylabel("Amount ($1k)")
        ax.set_title(f"Sum of latest government contracts to {ticker}")
        fig.tight_layout()

        plt.savefig("gov_contracts.png")
        imagefile = "gov_contracts.png"

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

        uploaded_image = gst_imgur.upload_image("gov_contracts.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            logger.debug("Image URL: %s", image_link)
        title = f"Stocks: [quiverquant.com] Contracts by {ticker}"
        if raw:
            description = df_contracts.to_string()
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
        os.remove("gov_contracts.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = disnake.Embed(
            title=f"ERROR Stocks: [quiverquant.com] Contracts by {ticker}",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
