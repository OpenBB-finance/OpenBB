import os

import disnake
import yfinance as yf
from matplotlib import pyplot as plt
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import gst_imgur, logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.dark_pool_shorts import stockgrid_model


async def spos_command(ctx, ticker: str = ""):
    """Net short vs position [Stockgrid]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.dps.spos %s", ticker)

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        ticker = ticker.upper()

        stock = yf.download(ticker, progress=False)
        if stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve data
        df = stockgrid_model.get_net_short_position(ticker)

        # Debug user output
        if cfg.DEBUG:
            logger.debug(df.to_string())

        # Output data
        title = f"Stocks: [Stockgrid] Net Short vs Position {ticker}"
        embed = disnake.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        plt.style.use("seaborn")
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        ax = fig.add_subplot(111)
        ax.bar(
            df["dates"],
            df["dollar_net_volume"] / 1_000,
            color="r",
            alpha=0.4,
            label="Net Short Vol. (1k $)",
        )
        ax.set_ylabel("Net Short Vol. (1k $)")

        ax2 = ax.twinx()
        ax2.plot(
            df["dates"].values,
            df["dollar_dp_position"],
            c="tab:blue",
            label="Position (1M $)",
        )
        ax2.set_ylabel("Position (1M $)")

        lines, labels = ax.get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc="upper left")

        ax.grid()
        plt.title(f"Net Short Vol. vs Position for {ticker}")
        plt.gcf().autofmt_xdate()
        file_name = ticker + "_spos.png"
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
            title=f"ERROR Stocks: [Stockgrid] Net Short vs Position {ticker}",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
