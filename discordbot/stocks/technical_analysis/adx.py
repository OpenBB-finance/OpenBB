import discord
import config_discordbot as cfg
from discordbot import gst_imgur
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import os
import helpers

from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.common.technical_analysis import trend_indicators_model
from gamestonk_terminal.config_plot import PLOT_DPI


async def adx_command(
    ctx, ticker="", length="14", scalar="100", drift="1", start="", end=""
):
    """Displays chart with average directional movement index [Yahoo Finance]"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.ta.adx {ticker} {length} {scalar} {drift} {start} {end}")

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
        df_stock = helpers.load(ticker, start)
        if df_stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve Data
        df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

        df_ta = trend_indicators_model.adx("1440min", df_stock, length, scalar, drift)

        # Output Data
        fig, ax = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax0 = ax[0]
        ax0.plot(df_stock.index, df_stock["Close"].values, "k", lw=2)
        ax0.set_title(f"Average Directional Movement Index (ADX) on {ticker}")
        ax0.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax0.set_ylabel("Share Price ($)")
        ax0.grid(b=True, which="major", color="#666666", linestyle="-")

        ax1 = ax[1]
        ax1.plot(df_ta.index, df_ta.iloc[:, 0].values, "b", lw=2)
        ax1.plot(df_ta.index, df_ta.iloc[:, 1].values, "g", lw=1)
        ax1.plot(df_ta.index, df_ta.iloc[:, 2].values, "r", lw=1)
        ax1.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax1.axhline(25, linewidth=3, color="k", ls="--")
        ax1.legend(
            [
                f"ADX ({df_ta.columns[0]})",
                f"+DI ({df_ta.columns[1]})",
                f"- DI ({df_ta.columns[2]})",
            ],
            loc="upper left",
        )
        ax1.set_xlabel("Time")
        ax1.grid(b=True, which="major", color="#666666", linestyle="-")

        ax1.set_ylim([0, 100])

        fig.tight_layout()
        plt.gcf().autofmt_xdate()

        plt.savefig("ta_adx.png")
        uploaded_image = gst_imgur.upload_image("ta_adx.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = "Stocks: Average-Directional-Movement-Index " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_adx.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: Average-Directional-Movement-Index",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
