import os
from datetime import datetime, timedelta
import discord
from matplotlib import pyplot as plt

from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.common.technical_analysis import volume_model
from gamestonk_terminal.config_plot import PLOT_DPI

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur, logger
import discordbot.helpers


async def obv_command(ctx, ticker="", start="", end=""):
    """Displays chart with on balance volume [Yahoo Finance]"""

    try:

        # Debug
        if cfg.DEBUG:
            logger.debug(
                "!stocks.ta.obv %s %s %s",
                ticker,
                start,
                end,
            )

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

        ticker = ticker.upper()
        df_stock = discordbot.helpers.load(ticker, start)
        if df_stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve Data
        df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

        # Output Data
        bar_colors = [
            "r" if x[1].Open < x[1].Close else "g" for x in df_stock.iterrows()
        ]

        bar_width = timedelta(days=1)

        divisor = 1_000_000
        df_vol = df_stock["Volume"].dropna()
        df_vol = df_vol.values / divisor
        df_ta = volume_model.obv("1440min", df_stock)
        df_cal = df_ta.values
        df_cal = df_cal / divisor

        fig, axes = plt.subplots(
            3,
            1,
            gridspec_kw={"height_ratios": [2, 1, 1]},
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
        ax = axes[0]
        ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)

        ax.set_title(f"{ticker} OBV")
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_ylabel("Price")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")
        ax.minorticks_on()
        ax.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)
        ax2 = axes[1]
        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax2.set_ylabel("Volume [M]")
        ax2.bar(
            df_stock.index,
            df_vol,
            color=bar_colors,
            alpha=0.8,
            width=bar_width,
        )
        ax3 = axes[2]
        ax3.set_ylabel("OBV [M]")
        ax3.set_xlabel("Time")
        ax3.plot(df_ta.index, df_cal, "b", lw=1)
        ax3.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax3.grid(b=True, which="major", color="#666666", linestyle="-")
        ax3.minorticks_on()
        ax3.grid(b=True, which="minor", color="#999999", linestyle="-", alpha=0.2)

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)

        plt.savefig("ta_obv.png")
        uploaded_image = gst_imgur.upload_image("ta_obv.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            logger.debug("Image URL: %s", image_link)
        title = "Stocks: On-Balance-Volume " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_obv.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: On-Balance-Volume",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
