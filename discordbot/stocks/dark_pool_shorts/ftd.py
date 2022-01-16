import os
from datetime import datetime, timedelta

import discord
import yfinance as yf
import matplotlib.dates as mdates
from matplotlib import pyplot as plt

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.stocks.dark_pool_shorts import sec_model

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur, logger
import discordbot.helpers


async def ftd_command(ctx, ticker="", start="", end=""):
    """Fails-to-deliver data [SEC]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.dps.ftd %s %s %s", ticker, start, end)

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        ticker = ticker.upper()

        stock = yf.download(ticker, progress=False)
        if stock.empty:
            raise Exception("Stock ticker is invalid")

        if start == "":
            start = datetime.now() - timedelta(days=365)
        else:
            start = datetime.strptime(start, cfg.DATE_FORMAT)

        if end == "":
            end = datetime.now()
        else:
            end = datetime.strptime(end, cfg.DATE_FORMAT)

        # Retrieve data
        ftds_data = sec_model.get_fails_to_deliver(ticker, start, end, 0)

        # Debug user output
        if cfg.DEBUG:
            logger.debug(ftds_data.to_string())

        plt.figure(dpi=PLOT_DPI)
        # Output data
        plt.bar(
            ftds_data["SETTLEMENT DATE"],
            ftds_data["QUANTITY (FAILS)"] / 1000,
        )
        plt.ylabel("Shares [K]")
        plt.title(f"Fails-to-deliver Data for {ticker}")
        plt.grid(b=True, which="major", color="#666666", linestyle="-", alpha=0.2)
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y/%m/%d"))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=7))
        plt.gcf().autofmt_xdate()
        plt.xlabel("Days")
        _ = plt.gca().twinx()
        stock = discordbot.helpers.load(ticker, start)
        stock_ftd = stock[stock.index > start]
        stock_ftd = stock_ftd[stock_ftd.index < end]
        plt.plot(stock_ftd.index, stock_ftd["Adj Close"], color="tab:orange")
        plt.ylabel("Share Price [$]")
        plt.savefig("dps_ftd.png")
        plt.close("all")
        uploaded_image = gst_imgur.upload_image("dps_ftd.png", title="something")
        image_link = uploaded_image.link

        title = "Stocks: [SEC] Failure-to-deliver " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)

        os.remove("dps_ftd.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title=f"ERROR Stocks: [SEC] Failure-to-deliver {ticker}",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
