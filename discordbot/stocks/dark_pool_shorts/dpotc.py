import os

import disnake
import matplotlib.dates as mdates
import yfinance as yf
from matplotlib import pyplot as plt
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import gst_imgur, logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.dark_pool_shorts import finra_model


async def dpotc_command(ctx, ticker: str = ""):
    """Dark pools (ATS) vs OTC data [FINRA]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.dps.dpotc %s", ticker)

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
            logger.debug(ats.to_string())
            logger.debug(otc.to_string())

        # Output data
        title = f"Stocks: [FINRA] Dark Pools (ATS) vs OTC {ticker}"
        embed = disnake.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        plt.style.use("seaborn")
        plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        if ats.empty and otc.empty:
            raise Exception("Stock ticker is invalid")
        _, _ = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

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
        imagefile = file_name

        img = Image.open(imagefile)
        print(img.size)
        im_bg = Image.open(cfg.IMG_BG)
        h = img.height + 240
        w = img.width + 520

        img = img.resize((w, h), Image.ANTIALIAS)
        x1 = int(0.5 * im_bg.size[0]) - int(0.5 * img.size[0])
        y1 = int(0.5 * im_bg.size[1]) - int(0.5 * img.size[1])
        x2 = int(0.5 * im_bg.size[0]) + int(0.5 * img.size[0])
        y2 = int(0.5 * im_bg.size[1]) + int(0.5 * img.size[1])
        img = img.convert("RGB")
        im_bg.paste(img, box=(x1 - 5, y1, x2 - 5, y2))
        im_bg.save(imagefile, "PNG", quality=100)

        image = Image.open(imagefile)
        image = autocrop_image(image, 0)
        image.save(imagefile, "PNG", quality=100)

        plt.close("all")
        uploaded_image = gst_imgur.upload_image(file_name, title="something")
        image_link = uploaded_image.link
        embed.set_image(url=image_link)
        os.remove(file_name)

        await ctx.send(embed=embed)

    except Exception as e:
        embed = disnake.Embed(
            title=f"ERROR Stocks: [FINRA] Dark Pools (ATS) vs OTC {ticker}",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
