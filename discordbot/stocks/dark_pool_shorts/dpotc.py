import os
import matplotlib.dates as mdates
import discord
import yfinance as yf
import config_discordbot as cfg
from matplotlib import pyplot as plt
from discordbot import gst_imgur
from gamestonk_terminal.config_plot import PLOT_DPI

from gamestonk_terminal.stocks.dark_pool_shorts import finra_model


async def dpotc_command(ctx, ticker=""):
    """Dark pools (ATS) vs OTC data [FINRA]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            print(f"\n!stocks.dps.dpotc {ticker}")

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        ticker = ticker.upper()

        stock = yf.download(ticker, progress=False)
        if stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve data
        ats, otc = finra_model.getTickerFINRAdata(ticker)

        # Debug user output
        if cfg.DEBUG:
            print(ats.to_string())
            print(otc.to_string())

        # Output data
        title = f"Stocks: [FINRA] Dark Pools (ATS) vs OTC {ticker}"
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        if ats.empty and otc.empty:
            embed = embed.set_description("No data found.")
        _, _ = plt.subplots(dpi=PLOT_DPI)

        plt.subplot(3, 1, (1, 2))
        if not ats.empty and not otc.empty:
            plt.bar(
                ats.index,
                (ats["totalWeeklyShareQuantity"] + otc["totalWeeklyShareQuantity"])
                / 1_000_000,
                color="tab:orange",
            )
            plt.bar(
                otc.index,
                otc["totalWeeklyShareQuantity"] / 1_000_000,
                color="tab:blue",
            )
            plt.legend(["ATS", "OTC"])

        elif not ats.empty:
            plt.bar(
                ats.index,
                ats["totalWeeklyShareQuantity"] / 1_000_000,
                color="tab:orange",
            )
            plt.legend(["ATS"])

        elif not otc.empty:
            plt.bar(
                otc.index,
                otc["totalWeeklyShareQuantity"] / 1_000_000,
                color="tab:blue",
            )
            plt.legend(["OTC"])

        plt.ylabel("Total Weekly Shares [Million]")
        plt.grid(b=True, which="major", color="#666666", linestyle="-", alpha=0.2)
        plt.title(f"Dark Pools (ATS) vs OTC (Non-ATS) Data for {ticker}")

        plt.subplot(313)
        if not ats.empty:
            plt.plot(
                ats.index,
                ats["totalWeeklyShareQuantity"] / ats["totalWeeklyTradeCount"],
                color="tab:orange",
            )
            plt.legend(["ATS"])

            if not otc.empty:
                plt.plot(
                    otc.index,
                    otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
                    color="tab:blue",
                )
                plt.legend(["ATS", "OTC"])

        else:
            plt.plot(
                otc.index,
                otc["totalWeeklyShareQuantity"] / otc["totalWeeklyTradeCount"],
                color="tab:blue",
            )
            plt.legend(["OTC"])

        plt.ylabel("Shares per Trade")
        plt.grid(b=True, which="major", color="#666666", linestyle="-", alpha=0.2)
        plt.gcf().autofmt_xdate()
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%m/%d"))
        plt.gca().xaxis.set_major_locator(mdates.DayLocator(interval=4))
        plt.xlabel("Weeks")
        file_name = ticker + "_dpotc.png"
        plt.savefig(file_name)
        plt.close("all")
        uploaded_image = gst_imgur.upload_image(file_name, title="something")
        image_link = uploaded_image.link
        embed.set_image(url=image_link)
        os.remove(file_name)

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title=f"ERROR Stocks: [FINRA] Dark Pools (ATS) vs OTC {ticker}",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
