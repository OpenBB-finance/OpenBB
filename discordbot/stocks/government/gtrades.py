import discord
import config_discordbot as cfg
from discordbot import gst_imgur
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import os
import pandas as pd

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.stocks.government import quiverquant_model
from gamestonk_terminal.helper_funcs import plot_autoscale


async def gtrades_command(
    ctx, ticker="", gov_type="", past_transactions_months="", raw=""
):
    """Displays government trades [quiverquant.com]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            print(
                f"!stocks.gov.gtrades {ticker} {gov_type} {past_transactions_months} {raw}"
            )

        if past_transactions_months == "":
            past_transactions_months = 10
        else:
            if not past_transactions_months.lstrip("-").isnumeric():
                raise Exception("Number has to be an integer")
            past_transactions_months = float(past_transactions_months)

        if raw == "false" or raw == "False" or raw == "FALSE" or raw == "":
            raw = False
        elif raw == "true" or raw == "True" or raw == "TRUE":
            raw = True
        else:
            raise Exception("raw argument has to be true or false")

        if ticker == "":
            raise Exception("A ticker is required")

        possible_args = ["congress", "senate", "house"]
        if gov_type == "":
            gov_type = "congress"
        elif gov_type not in possible_args:
            raise Exception(
                "Enter a valid government argument, options are: congress, senate and house"
            )

        # Retrieve Data
        df_gov = quiverquant_model.get_government_trading(gov_type, ticker)

        if df_gov.empty:
            raise Exception(f"No {gov_type} trading data found")

        # Output Data
        df_gov = df_gov.sort_values("TransactionDate", ascending=False)

        start_date = datetime.now() - timedelta(days=past_transactions_months * 30)

        df_gov["TransactionDate"] = pd.to_datetime(df_gov["TransactionDate"])

        df_gov = df_gov[df_gov["TransactionDate"] > start_date]

        if df_gov.empty:
            print(f"No recent {gov_type} trading data found\n")
            return

        df_gov["min"] = df_gov["Range"].apply(
            lambda x: x.split("-")[0].strip("$").replace(",", "").strip()
        )
        df_gov["max"] = df_gov["Range"].apply(
            lambda x: x.split("-")[1].replace(",", "").strip().strip("$")
            if "-" in x
            else x.strip("$").replace(",", "").split("\n")[0]
        )

        df_gov["lower"] = df_gov[["min", "max", "Transaction"]].apply(
            lambda x: int(float(x["min"]))
            if x["Transaction"] == "Purchase"
            else -int(float(x["max"])),
            axis=1,
        )
        df_gov["upper"] = df_gov[["min", "max", "Transaction"]].apply(
            lambda x: int(float(x["max"]))
            if x["Transaction"] == "Purchase"
            else -1 * int(float(x["min"])),
            axis=1,
        )

        df_gov = df_gov.sort_values("TransactionDate", ascending=True)

        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        ax.fill_between(
            df_gov["TransactionDate"].unique(),
            df_gov.groupby("TransactionDate")["lower"].sum().values / 1000,
            df_gov.groupby("TransactionDate")["upper"].sum().values / 1000,
        )

        ax.set_xlim(
            [
                df_gov["TransactionDate"].values[0],
                df_gov["TransactionDate"].values[-1],
            ]
        )
        ax.grid()
        ax.set_title(f"{gov_type.capitalize()} trading on {ticker}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Amount ($1k)")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y/%m/%d"))
        plt.gcf().autofmt_xdate()
        fig.tight_layout()

        plt.savefig("gov_gtrades.png")
        uploaded_image = gst_imgur.upload_image("gov_gtrades.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = "Stocks: [quiverquant.com] Government Trades"
        if raw:
            description = df_gov.to_string()
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
        os.remove("gov_gtrades.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: [quiverquant.com] Government Trades",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
