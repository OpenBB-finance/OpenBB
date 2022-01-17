import os
from datetime import datetime, timedelta

import discord
from matplotlib import pyplot as plt

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.stocks.due_diligence import business_insider_model

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur, logger
import discordbot.helpers


async def pt_command(ctx, ticker="", raw="", start=""):
    """Displays price targets [Business Insider]"""

    try:
        # Debug
        if cfg.DEBUG:
            logger.debug("!stocks.dd.pt %s", ticker)

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        if start == "":
            start = datetime.now() - timedelta(days=365)
        else:
            start = datetime.strptime(start, cfg.DATE_FORMAT)

        if raw in ["false", "False", "FALSE", ""]:
            raw = False

        if raw in ["true", "True", "TRUE"]:
            raw = True

        if raw not in [True, False]:
            raise Exception("raw argument has to be true or false")

        df_analyst_data = business_insider_model.get_price_target_from_analysts(ticker)
        stock = discordbot.helpers.load(ticker, start)

        if df_analyst_data.empty or stock.empty:
            raise Exception("Enter valid ticker")

        # Output Data

        if raw:
            df_analyst_data.sort_index(ascending=False)
            report = "´´´" + df_analyst_data.to_string() + "´´´"
            embed = discord.Embed(
                title="Stocks: [Business Insider] Price Targets",
                description=report,
                colour=cfg.COLOR,
            ).set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
            ctx.send(embed=embed)
        else:
            plt.figure(dpi=PLOT_DPI)
            if start:
                df_analyst_data = df_analyst_data[start:]

            plt.plot(stock.index, stock["Adj Close"].values, lw=3)

            plt.plot(df_analyst_data.groupby(by=["Date"]).mean())

            plt.scatter(
                df_analyst_data.index, df_analyst_data["Price Target"], c="r", s=40
            )

            plt.legend(["Closing Price", "Average Price Target", "Price Target"])

            plt.title(f"{ticker} (Time Series) and Price Target")
            plt.xlim(stock.index[0], stock.index[-1])
            plt.xlabel("Time")
            plt.ylabel("Share Price")
            plt.grid(b=True, which="major", color="#666666", linestyle="-")
            plt.gcf().autofmt_xdate()
            plt.savefig("ta_pt.png")
            uploaded_image = gst_imgur.upload_image("ta_pt.png", title="something")
            image_link = uploaded_image.link
            if cfg.DEBUG:
                logger.debug("Image URL: %s", image_link)
            title = "Stocks: [Business Insider] Price Targets " + ticker
            embed = discord.Embed(title=title, colour=cfg.COLOR)
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
            embed.set_image(url=image_link)
            os.remove("ta_pt.png")

            await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: [Business Insider] Price Targets",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
