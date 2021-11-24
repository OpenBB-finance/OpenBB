import discord
import config_discordbot as cfg
from discordbot import gst_imgur
from matplotlib import pyplot as plt
import os
import numpy as np

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.stocks.government import quiverquant_model
from gamestonk_terminal.helper_funcs import plot_autoscale


async def histcont_command(ctx, ticker=""):
    """Displays historical quarterly-contracts [quiverquant.com]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            print(f"!stocks.gov.histcont {ticker}")

        if ticker == "":
            raise Exception("A ticker is required")

        # Retrieve Data
        df_contracts = quiverquant_model.get_government_trading(
            "quarter-contracts", ticker=ticker
        )

        if df_contracts.empty:
            print("No quarterly government contracts found\n")
            return

        # Output Data
        amounts = df_contracts.sort_values(by=["Year", "Qtr"])["Amount"].values

        qtr = df_contracts.sort_values(by=["Year", "Qtr"])["Qtr"].values
        year = df_contracts.sort_values(by=["Year", "Qtr"])["Year"].values

        quarter_ticks = [
            f"{quarter[0]}" if quarter[1] == 1 else "" for quarter in zip(year, qtr)
        ]
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
        uploaded_image = gst_imgur.upload_image("gov_histcont.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = "Stocks: Historical Quarterly Government Contract " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("gov_histcont.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: Historical Quarterly Government Contract",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
