import os
from datetime import datetime, timedelta
import discord
from matplotlib import pyplot as plt
import pandas as pd

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.stocks.government import quiverquant_model
from gamestonk_terminal.helper_funcs import plot_autoscale


async def topsells_command(
    ctx, gov_type="", past_transactions_months="", num="", raw=""
):
    """Displays most sold stocks by the congress/senate/house [quiverquant.com]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            print(
                f"!stocks.gov.topsells {gov_type} {past_transactions_months} {num} {raw}"
            )

        if past_transactions_months == "":
            past_transactions_months = 5
        else:
            if not past_transactions_months.lstrip("-").isnumeric():
                raise Exception("Number has to be an integer")
            past_transactions_months = int(past_transactions_months)

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

        possible_args = ["congress", "senate", "house"]
        if gov_type == "":
            gov_type = "congress"
        elif gov_type not in possible_args:
            raise Exception(
                "Enter a valid government argument, options are: congress, senate and house"
            )

        # Retrieve Data
        df_gov = quiverquant_model.get_government_trading(gov_type)

        # Output Data
        if df_gov.empty:
            raise Exception(f"No {gov_type} trading data found\n")

        df_gov = df_gov.sort_values("TransactionDate", ascending=False)

        start_date = datetime.now() - timedelta(days=past_transactions_months * 30)

        df_gov["TransactionDate"] = pd.to_datetime(df_gov["TransactionDate"])

        df_gov = df_gov[df_gov["TransactionDate"] > start_date].dropna()

        df_gov["Range"] = df_gov["Range"].apply(
            lambda x: "$5,000,001-$5,000,001" if x == ">$5,000,000" else x
        )

        df_gov["min"] = df_gov["Range"].apply(
            lambda x: x.split("-")[0]
            .strip("$")
            .replace(",", "")
            .strip()
            .replace(">$", "")
            .strip()
        )
        df_gov["max"] = df_gov["Range"].apply(
            lambda x: x.split("-")[1]
            .replace(",", "")
            .strip()
            .strip("$")
            .replace(">$", "")
            .strip()
            if "-" in x
            else x.strip("$").replace(",", "").replace(">$", "").strip()
        )

        df_gov["lower"] = df_gov[["min", "max", "Transaction"]].apply(
            lambda x: float(x["min"])
            if x["Transaction"] == "Purchase"
            else -float(x["max"]),
            axis=1,
        )
        df_gov["upper"] = df_gov[["min", "max", "Transaction"]].apply(
            lambda x: float(x["max"])
            if x["Transaction"] == "Purchase"
            else -float(x["min"]),
            axis=1,
        )

        df_gov = df_gov.sort_values("TransactionDate", ascending=True)
        if raw:
            df = pd.DataFrame(
                df_gov.groupby("Ticker")["upper"]
                .sum()
                .div(1000)
                .sort_values(ascending=True)
                .abs()
                .head(n=num)
            )
            description = "```" + df.to_string() + "```"

        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        df_gov.groupby("Ticker")["upper"].sum().div(1000).sort_values().abs().head(
            n=num
        ).plot(kind="bar", rot=0, ax=ax)
        ax.set_ylabel("Amount ($1k)")
        ax.set_title(
            f"{num} most sold stocks over last {past_transactions_months} months"
            f" (upper bound) for {gov_type}"
        )
        plt.gcf().axes[0].yaxis.get_major_formatter().set_scientific(False)
        fig.tight_layout()

        plt.savefig("gov_topsells.png")
        uploaded_image = gst_imgur.upload_image("gov_topsells.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = f"Stocks: [quiverquant.com] Top sells for {gov_type.upper()}"
        if raw:
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
        os.remove("gov_topsells.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title=f"ERROR Stocks: [quiverquant.com] Top sells for {gov_type.upper()}",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
