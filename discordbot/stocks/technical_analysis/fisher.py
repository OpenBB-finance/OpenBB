import os
from datetime import datetime, timedelta
import discord
from matplotlib import pyplot as plt

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur
import discordbot.helpers

from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.common.technical_analysis import momentum_model
from gamestonk_terminal.config_plot import PLOT_DPI


async def fisher_command(ctx, ticker="", length="14", start="", end=""):
    """Displays chart with fisher transformation [Yahoo Finance]"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.ta.fisher {ticker} {length} {start} {end}")

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        if start == "":
            start = datetime.now() - timedelta(days=365)
        else:
            start = datetime.strptime(start, cfg.DATE_FORMAT)

        if end == "":
            end = datetime.now()
        else:
            end = datetime.strptime(end, cfg.DATE_FORMAT)

        if not length.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")
        length = float(length)

        ticker = ticker.upper()
        df_stock = discordbot.helpers.load(ticker, start)
        if df_stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve Data
        df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

        df_ta = momentum_model.fisher("1440min", df_stock, length)

        # Output Data
        fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax = axes[0]
        ax.set_title(f"{ticker} Fisher Transform")
        ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=1)
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_ylabel("Price")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")

        ax2 = axes[1]
        ax2.plot(
            df_ta.index,
            df_ta.iloc[:, 0].values,
            "b",
            lw=2,
            label="Fisher",
        )
        ax2.plot(
            df_ta.index,
            df_ta.iloc[:, 1].values,
            "fuchsia",
            lw=2,
            label="Signal",
        )
        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax2.axhspan(2, plt.gca().get_ylim()[1], facecolor="r", alpha=0.2)
        ax2.axhspan(plt.gca().get_ylim()[0], -2, facecolor="g", alpha=0.2)
        ax2.axhline(2, linewidth=3, color="r", ls="--")
        ax2.axhline(-2, linewidth=3, color="g", ls="--")
        ax2.grid(b=True, which="major", color="#666666", linestyle="-")
        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax2.axhspan(2, plt.gca().get_ylim()[1], facecolor="r", alpha=0.2)
        ax2.axhspan(plt.gca().get_ylim()[0], -2, facecolor="g", alpha=0.2)
        ax2.axhline(2, linewidth=3, color="r", ls="--")
        ax2.axhline(-2, linewidth=3, color="g", ls="--")
        ax2.grid(b=True, which="major", color="#666666", linestyle="-")
        ax2.set_yticks([-2, 0, 2])
        ax2.set_yticklabels(["-2 STDEV", "0", "+2 STDEV"])

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)

        plt.legend()

        plt.savefig("ta_fisher.png")
        uploaded_image = gst_imgur.upload_image("ta_fisher.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = "Stocks: Fisher-Transform " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_fisher.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: Fisher-Transform",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
