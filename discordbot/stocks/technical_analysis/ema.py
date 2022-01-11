import os
from datetime import datetime, timedelta
import discord
from matplotlib import pyplot as plt
import pandas as pd

from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.common.technical_analysis import overlap_model
from gamestonk_terminal.config_plot import PLOT_DPI

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur, logger
import discordbot.helpers


async def ema_command(ctx, ticker="", window="", offset="", start="", end=""):
    """Displays chart with exponential moving average [Yahoo Finance]"""

    try:
        # Debug
        if cfg.DEBUG:
            logger.debug(
                "!stocks.ta.ema %s %s %s %s %s",
                ticker,
                window,
                offset,
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

        l_legend = [ticker]

        if window == "":
            window = [20, 50]
        else:
            window_temp = list()
            for wind in window.split(","):
                try:
                    window_temp.append(float(wind))
                except Exception as e:
                    raise Exception("Window needs to be a float") from e
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
            ema_data = overlap_model.ema(
                values=stock["Adj Close"], length=win, offset=offset
            )
            price_df = price_df.join(ema_data)
            l_legend.append(f"EMA {win}")
            i += 1

        # Output Data
        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")
        price_df = price_df.loc[(price_df.index >= start) & (price_df.index < end)]

        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax.set_title(f"{ticker} EMA")

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

        plt.savefig("ta_ema.png")
        uploaded_image = gst_imgur.upload_image("ta_ema.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            logger.debug("Image URL: %s", image_link)
        title = "Stocks: Exponential-Moving-Average " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_ema.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: Exponential-Moving-Average",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
