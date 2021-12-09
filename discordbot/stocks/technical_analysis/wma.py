import os
from datetime import datetime, timedelta
import discord
from matplotlib import pyplot as plt
import pandas as pd

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur
import discordbot.helpers

from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.common.technical_analysis import overlap_model
from gamestonk_terminal.config_plot import PLOT_DPI


async def wma_command(ctx, ticker="", window="", offset="", start="", end=""):
    """Displays chart with weighted moving average [Yahoo Finance]"""

    try:
        # Debug
        if cfg.DEBUG:
            print(f"!stocks.ta.wma {ticker} {window} {offset} {start} {end}")

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

        l_legend = [ticker]

        if window == "":
            window = [20, 50]
        else:
            window_temp = []
            i = 0
            b = 0
            while i < len(window):
                if window[i] == ",":
                    window_temp.append(float(window[b:i]))
                    l_legend.append(float(window[b:i]))
                    b = i
                i += 1
            window = window_temp

        if offset == "":
            offset = 0
        else:
            if not offset.lstrip("-").isnumeric():
                raise Exception("Number has to be an integer")
            offset = float(offset)

        ticker = ticker.upper()
        stock = discordbot.helpers.load(ticker, start)
        if stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve Data
        price_df = pd.DataFrame(
            stock["Adj Close"].values, columns=["Price"], index=stock.index
        )
        i = 1
        for win in window:
            wma_data = overlap_model.wma(
                s_interval="1440min", df_stock=stock, length=win, offset=offset
            )
            price_df = price_df.join(wma_data)
            l_legend.append(f"WMA {win}")
            i += 1

        # Output Data
        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")
        price_df = price_df.loc[(price_df.index >= start) & (price_df.index < end)]

        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax.set_title(f"{ticker} WMA")

        ax.plot(price_df.index, price_df["Price"], lw=3, c="k")

        ax.set_xlabel("Time")
        ax.set_xlim([price_df.index[0], price_df.index[-1]])
        ax.set_ylabel(f"{ticker} Price")

        for idx in range(1, price_df.shape[1]):
            ax.plot(price_df.iloc[:, idx])

        ax.legend(l_legend)
        ax.grid(b=True, which="major", color="#666666", linestyle="-")

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)

        plt.savefig("ta_wma.png")
        uploaded_image = gst_imgur.upload_image("ta_wma.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = "Stocks: Weighted-Moving-Average " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_wma.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: Weighted-Moving-Average",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
