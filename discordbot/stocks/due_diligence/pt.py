import os
from datetime import datetime, timedelta

import disnake
from matplotlib import pyplot as plt
from PIL import Image

import discordbot.config_discordbot as cfg
import discordbot.helpers
from discordbot.config_discordbot import gst_imgur, logger
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.due_diligence import business_insider_model


async def pt_command(ctx, ticker: str = "", raw: bool = False, start=""):
    """Displays price targets [Business Insider]"""

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

    if raw not in [True, False]:
        raise Exception("raw argument has to be true or false")

    df_analyst_data = business_insider_model.get_price_target_from_analysts(ticker)
    stock = discordbot.helpers.load(ticker, start)
    print(df_analyst_data)
    if df_analyst_data.empty or stock.empty:
        raise Exception("Enter valid ticker")

    # Output Data

    if raw:
        df_analyst_data.sort_index(ascending=False)
        report = "```" + df_analyst_data.to_string() + "```"
        embed = disnake.Embed(
            title="Stocks: [Business Insider] Price Targets",
            description=report,
            colour=cfg.COLOR,
        ).set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        ctx.send(embed=embed)
    else:
        plt.style.use("seaborn")
        plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
        if start:
            df_analyst_data = df_analyst_data[start:]

        plt.plot(stock.index, stock["Adj Close"].values, lw=3)

        plt.plot(df_analyst_data.groupby(by=["Date"]).mean())

        plt.scatter(df_analyst_data.index, df_analyst_data["Price Target"], c="r", s=40)

        plt.legend(["Closing Price", "Average Price Target", "Price Target"])

        plt.title(f"{ticker} (Time Series) and Price Target")
        plt.xlim(stock.index[0], stock.index[-1])
        plt.xlabel("Time")
        plt.ylabel("Share Price")
        plt.grid(b=True, which="major", color="#666666", linestyle="-")
        plt.savefig("ta_pt.png")
        imagefile = "ta_pt.png"

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
        image = discordbot.helpers.autocrop_image(image, 0)
        image.save(imagefile, "PNG", quality=100)

        uploaded_image = gst_imgur.upload_image("ta_pt.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            logger.debug("Image URL: %s", image_link)
        title = "Stocks: [Business Insider] Price Targets " + ticker
        embed = disnake.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_pt.png")

        await ctx.send(embed=embed)
