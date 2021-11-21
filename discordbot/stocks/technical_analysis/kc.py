import discord
import config_discordbot as cfg
from discordbot import gst_imgur
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import os
import helpers

from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.common.technical_analysis import volatility_model
from gamestonk_terminal.config_plot import PLOT_DPI


async def kc_command(
    ctx, ticker="", length="20", scalar="2", mamode="sma", offset="0", start="", end=""
):
    """Displays chart with keltner channel [Yahoo Finance]"""

    try:

        # Debug
        if cfg.DEBUG:
            print(
                f"!stocks.ta.kc {ticker} {length} {scalar} {mamode} {offset} {start} {end}"
            )

        # Check for argument
        possible_ma = ["sma", "ema", "wma", "hma", "zlma"]

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
        if not offset.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")
        offset = float(offset)

        if mamode not in possible_ma:
            raise Exception("Invalid ma entered")

        ticker = ticker.upper()
        df_stock = helpers.load(ticker, start)
        if df_stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve Data
        df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

        df_ta = volatility_model.kc("1440min", df_stock, length, scalar, mamode, offset)

        # Output Data
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax.plot(df_stock.index, df_stock["Adj Close"].values, color="fuchsia")
        ax.plot(df_ta.index, df_ta.iloc[:, 0].values, "b", lw=1.5, label="upper")
        ax.plot(df_ta.index, df_ta.iloc[:, 1].values, "b", lw=1.5, ls="--")
        ax.plot(df_ta.index, df_ta.iloc[:, 2].values, "b", lw=1.5, label="lower")
        ax.set_title(f"{ticker} Keltner Channels")
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_xlabel("Time")
        ax.set_ylabel("Price")

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

        plt.legend()

        plt.savefig("ta_kc.png")
        uploaded_image = gst_imgur.upload_image("ta_kc.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = "Stocks: Keltner-Channel " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_kc.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: Keltner-Channel",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
