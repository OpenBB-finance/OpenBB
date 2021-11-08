import discord
import config_discordbot as cfg
from discordbot import gst_imgur
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import os
import helpers

from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.common.technical_analysis import volume_model
from gamestonk_terminal.config_plot import PLOT_DPI


async def adosc_command(
    ctx, ticker="", open="False", fast="3", slow="10", start="", end=""
):
    """Displays chart with chaikin oscillator [Yahoo Finance]"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.ta.adosc {ticker} {open} {fast} {slow} {start} {end}")

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

        if open == "false" or open == "False" or open == "FALSE":
            open = False
        elif open == "true" or open == "True" or open == "TRUE":
            open = True
        else:
            raise Exception("open argument has to be true or false")

        ticker = ticker.upper()
        df_stock = helpers.load(ticker, start)
        if df_stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve Data
        df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

        # Output Data
        bar_colors = [
            "r" if x[1].Open < x[1].Close else "g" for x in df_stock.iterrows()
        ]

        divisor = 1_000_000
        df_vol = df_stock["Volume"].dropna()
        df_vol = df_vol.values / divisor
        df_ta = volume_model.adosc(df_stock, open, fast, slow)
        df_cal = df_ta.values
        df_cal = df_cal / divisor

        fig, axes = plt.subplots(
            3,
            1,
            figsize=plot_autoscale(),
            dpi=PLOT_DPI,
        )
        ax = axes[0]
        ax.set_title(f"{ticker} AD Oscillator")
        ax.plot(df_stock.index, df_stock["Adj Close"].values, "fuchsia", lw=1)
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_ylabel("Price")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")

        ax1 = axes[1]
        ax1.set_ylabel("Volume [M]")

        ax1.bar(
            df_stock.index,
            df_vol,
            color=bar_colors,
            alpha=0.8,
            width=0.3,
        )
        ax1.set_xlim(df_stock.index[0], df_stock.index[-1])

        ax2 = axes[2]
        ax2.set_ylabel("AD Osc [M]")
        ax2.set_xlabel("Time")
        ax2.plot(df_ta.index, df_cal, "b", lw=2, label="AD Osc")
        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax2.grid(b=True, which="major", color="#666666", linestyle="-")

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)
        plt.legend()

        plt.savefig("ta_adosc.png")
        uploaded_image = gst_imgur.upload_image("ta_adosc.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = "Stocks: Accumulation/Distribution Oscillator " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_adosc.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: Accumulation/Distribution Oscillator",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
