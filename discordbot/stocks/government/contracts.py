import discord
import config_discordbot as cfg
from discordbot import gst_imgur
from matplotlib import pyplot as plt
import os
import pandas as pd

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.stocks.government import quiverquant_model
from gamestonk_terminal.helper_funcs import plot_autoscale


async def contracts_command(ctx, ticker="", past_transaction_days="", raw=""):
    """Displays contracts associated with tickers [quiverquant.com]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            print(f"!stocks.gov.contracts {ticker} {past_transaction_days} {raw}")

        if past_transaction_days == "":
            past_transaction_days = 10
        else:
            if not past_transaction_days.lstrip("-").isnumeric():
                raise Exception("Number has to be an integer")
            past_transaction_days = int(past_transaction_days)

        if raw == "false" or raw == "False" or raw == "FALSE" or raw == "":
            raw = False
        elif raw == "true" or raw == "True" or raw == "TRUE":
            raw = True
        else:
            raise Exception("raw argument has to be true or false")

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

        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        df_contracts.groupby("Date").sum().div(1000).plot(kind="bar", rot=0, ax=ax)
        ax.set_ylabel("Amount ($1k)")
        ax.set_title(f"Sum of latest government contracts to {ticker}")
        fig.tight_layout()

        plt.savefig("gov_contracts.png")
        uploaded_image = gst_imgur.upload_image("gov_contracts.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = f"Stocks: [quiverquant.com] Contracts by {ticker}"
        if raw:
            description = df_contracts.to_string()
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
        os.remove("gov_contracts.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title=f"ERROR Stocks: [quiverquant.com] Contracts by {ticker}",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
