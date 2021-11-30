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


async def macd_command(
    ctx, ticker="", fast="12", slow="26", signal="9", start="", end=""
):
    """Displays chart with moving average convergence/divergence [Yahoo Finance]"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.ta.macd {ticker} {fast} {slow} {signal} {start} {end}")

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

        if not fast.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")
        fast = float(fast)
        if not slow.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")
        slow = float(slow)
        if not signal.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")
        signal = float(signal)

        ticker = ticker.upper()
        df_stock = discordbot.helpers.load(ticker, start)
        if df_stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve Data
        df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

        df_ta = momentum_model.macd("1440min", df_stock, fast, slow, signal)

        # Output Data
        fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax = axes[0]
        ax.set_title(f"{ticker} MACD")
        ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_ylabel("Share Price ($)")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")

        ax2 = axes[1]
        ax2.plot(df_ta.index, df_ta.iloc[:, 0].values, "b", lw=2)
        ax2.plot(df_ta.index, df_ta.iloc[:, 2].values, "r", lw=2)
        ax2.bar(df_ta.index, df_ta.iloc[:, 1].values, color="g")
        ax2.legend(
            [
                f"MACD Line {df_ta.columns[0]}",
                f"Signal Line {df_ta.columns[2]}",
                f"Histogram {df_ta.columns[1]}",
            ],
            loc="upper left",
        )
        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax2.grid(b=True, which="major", color="#666666", linestyle="-")

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)

        plt.savefig("ta_macd.png")
        uploaded_image = gst_imgur.upload_image("ta_cci.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = "Stocks: Moving-Average-Convergence-Divergence " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_macd.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: Moving-Average-Convergence-Divergence",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
