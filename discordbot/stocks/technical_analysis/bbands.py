import os
from datetime import datetime, timedelta
import discord
from matplotlib import pyplot as plt

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur
import discordbot.helpers

from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.common.technical_analysis import volatility_model
from gamestonk_terminal.config_plot import PLOT_DPI


async def bbands_command(
    ctx, ticker="", length="5", n_std="2", mamode="sma", start="", end=""
):
    """Displays chart with bollinger bands [Yahoo Finance]"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.ta.bbands {ticker} {length} {n_std} {mamode} {start} {end}")

        # Check for argument
        possible_ma = [
            "dema",
            "ema",
            "fwma",
            "hma",
            "linreg",
            "midpoint",
            "pwma",
            "rma",
            "sinwma",
            "sma",
            "swma",
            "t3",
            "tema",
            "trima",
            "vidya",
            "wma",
            "zlma",
        ]

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
        if not n_std.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")
        n_std = float(n_std)

        if mamode not in possible_ma:
            raise Exception("Invalid ma entered")

        ticker = ticker.upper()
        df_stock = discordbot.helpers.load(ticker, start)
        if df_stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve Data
        df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

        df_ta = volatility_model.bbands("1440min", df_stock, length, n_std, mamode)

        # Output Data
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax.plot(df_stock.index, df_stock["Adj Close"].values, color="k", lw=3)
        ax.plot(df_ta.index, df_ta.iloc[:, 0].values, "r", lw=2)
        ax.plot(df_ta.index, df_ta.iloc[:, 1].values, "b", lw=1.5, ls="--")
        ax.plot(df_ta.index, df_ta.iloc[:, 2].values, "g", lw=2)
        ax.set_title(f"{ticker} Bollinger Bands")
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_xlabel("Time")
        ax.set_ylabel("Share Price ($)")

        ax.legend([ticker, df_ta.columns[0], df_ta.columns[1], df_ta.columns[2]])
        ax.fill_between(
            df_ta.index,
            df_ta.iloc[:, 0].values,
            df_ta.iloc[:, 2].values,
            alpha=0.1,
            color="b",
        )
        ax.grid(b=True, which="major", color="#666666", linestyle="-")

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)

        plt.savefig("ta_bbands.png")
        uploaded_image = gst_imgur.upload_image("ta_bbands.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = "Stocks: Bollinger-Bands " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_bbands.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: Bollinger-Bands",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
