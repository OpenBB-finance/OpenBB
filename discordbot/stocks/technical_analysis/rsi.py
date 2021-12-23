import os
from datetime import datetime, timedelta
import discord
from matplotlib import pyplot as plt

from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.common.technical_analysis import momentum_model
from gamestonk_terminal.config_plot import PLOT_DPI

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur
import discordbot.helpers


async def rsi_command(
    ctx, ticker="", length="14", scalar="100", drift="1", start="", end=""
):
    """Displays chart with relative strength index [Yahoo Finance]"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.ta.rsi {ticker} {length} {scalar} {drift} {start} {end}")

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
        if not scalar.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")
        scalar = float(scalar)
        if not drift.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")
        drift = float(drift)

        ticker = ticker.upper()
        df_stock = discordbot.helpers.load(ticker, start)
        if df_stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve Data
        df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

        df_ta = momentum_model.rsi("1440min", df_stock, length, scalar, drift)

        # Output Data
        fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax = axes[0]
        ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)
        ax.set_title(f" {ticker} RSI{length} ")
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_ylabel("Share Price ($)")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")

        ax2 = axes[1]
        ax2.plot(df_ta.index, df_ta.values, "b", lw=2)
        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax2.axhspan(70, 100, facecolor="r", alpha=0.2)
        ax2.axhspan(0, 30, facecolor="g", alpha=0.2)
        ax2.axhline(70, linewidth=3, color="r", ls="--")
        ax2.axhline(30, linewidth=3, color="g", ls="--")
        ax2.grid(b=True, which="major", color="#666666", linestyle="-")
        ax2.set_ylim([0, 100])
        ax3 = ax2.twinx()
        ax3.set_ylim(ax2.get_ylim())
        ax3.set_yticks([30, 70])
        ax3.set_yticklabels(["OVERSOLD", "OVERBOUGHT"])

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)

        plt.savefig("ta_rsi.png")
        uploaded_image = gst_imgur.upload_image("ta_rsi.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = "Stocks: Relative-Strength-Index " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_rsi.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: Relative-Strength-Index",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
