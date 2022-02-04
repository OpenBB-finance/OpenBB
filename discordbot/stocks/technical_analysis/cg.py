import os
from datetime import datetime, timedelta

import disnake
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image

import discordbot.config_discordbot as cfg
import discordbot.helpers
from discordbot.config_discordbot import gst_imgur, logger
from gamestonk_terminal.common.technical_analysis import momentum_model
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale


async def cg_command(ctx, ticker="", length="14", start="", end=""):
    """Displays chart with centre of gravity [Yahoo Finance]"""

    try:

        # Debug
        if cfg.DEBUG:
            logger.debug(
                "!stocks.ta.cg %s %s %s %s",
                ticker,
                length,
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

        if not length.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")
        length = float(length)

        ticker = ticker.upper()
        df_stock = discordbot.helpers.load(ticker, start)
        if df_stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve Data
        df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]
        df_close = df_stock["Adj Close"]
        df_close.columns = ["values"]
        df_ta = momentum_model.cg(df_close, length)

        # Output Data
        plt.style.use("seaborn")
        fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax = axes[0]
        ax.set_title(f"{ticker} Centre of Gravity")
        ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=1)
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_ylabel("Share Price ($)")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")

        ax2 = axes[1]
        ax2.plot(df_ta.index, df_ta.values, "b", lw=2, label="CG")
        # shift cg 1 bar forward for signal
        signal = df_ta.values
        signal = np.roll(signal, 1)
        ax2.plot(df_ta.index, signal, "g", lw=1, label="Signal")
        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax2.grid(b=True, which="major", color="#666666", linestyle="-")

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)
        plt.legend()

        plt.savefig("ta_cg.png")
        imagefile = "ta_cg.png"

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

        uploaded_image = gst_imgur.upload_image("ta_cg.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            logger.debug("Image URL: %s", image_link)
        title = "Stocks: Center-of-Gravity " + ticker
        embed = disnake.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_cg.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Stocks: Center-of-Gravity",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
