import os
import discord
from matplotlib import pyplot as plt
import pandas as pd

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.stocks.government import quiverquant_model
from gamestonk_terminal.helper_funcs import plot_autoscale


async def toplobbying_command(ctx, num="", raw=""):
    """Displays top lobbying firms [quiverquant.com]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            print(f"!stocks.gov.toplobbying {num} {raw}")

        if num == "":
            num = 10
        else:
            if not num.lstrip("-").isnumeric():
                raise Exception("Number has to be an integer")
            num = int(num)

        if raw in ["false", "False", "FALSE", ""]:
            raw = False

        if raw in ["true", "True", "TRUE"]:
            raw = True

        if raw not in [True, False]:
            raise Exception("raw argument has to be true or false")

        # Retrieve Data
        df_lobbying = quiverquant_model.get_government_trading("corporate-lobbying")

        if df_lobbying.empty:
            raise Exception("No corporate lobbying found")

        df_lobbying["Amount"] = df_lobbying.Amount.astype(float).fillna(0) / 100_000

        lobbying_by_ticker = pd.DataFrame(
            df_lobbying.groupby("Ticker")["Amount"].agg("sum")
        ).sort_values(by="Amount", ascending=False)
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        lobbying_by_ticker.head(num).plot(kind="bar", ax=ax)
        ax.set_xlabel("Ticker")
        ax.set_ylabel("Total Amount ($100k)")
        ax.set_title(f"Corporate Lobbying Spent since {df_lobbying['Date'].min()}")
        fig.tight_layout()

        plt.savefig("ta_toplobbying.png")
        uploaded_image = gst_imgur.upload_image("ta_toplobbying.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = "Stocks: [quiverquant.com] Top Lobbying Firms"
        if raw:
            description = lobbying_by_ticker.head(num).to_string()
            embed = discord.Embed(
                title=title, description=description, colour=cfg.COLOR
            )
        else:
            embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_toplobbying.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: [quiverquant.com] Top Lobbying Firms",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
