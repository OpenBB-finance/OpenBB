import os
from datetime import datetime, timedelta

import disnake
from matplotlib import pyplot as plt
from PIL import Image

import discordbot.config_discordbot as cfg
import discordbot.helpers
from discordbot.config_discordbot import gst_imgur, logger
from gamestonk_terminal import config_plot as cfp
from gamestonk_terminal.common.technical_analysis import custom_indicators_model
from gamestonk_terminal.helper_funcs import plot_autoscale


async def fib_command(ctx, ticker="", start="", end=""):
    """Displays chart with fibonacci retracement [Yahoo Finance]"""

    try:

        # Debug
        if cfg.DEBUG:
            logger.debug(
                "!stocks.ta.fib %s %s %s",
                ticker,
                start,
                end,
            )

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        if start == "":
            start = datetime.now() - timedelta(days=365)
            f_start = None
        else:
            start = datetime.strptime(start, cfg.DATE_FORMAT)
            f_start = start

        if end == "":
            end = datetime.now()
            f_end = None
        else:
            end = datetime.strptime(end, cfg.DATE_FORMAT)
            f_end = None

        ticker = ticker.upper()
        df_stock = discordbot.helpers.load(ticker, start)
        if df_stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve Data
        df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

        start = start.strftime("%Y-%m-%d")
        end = end.strftime("%Y-%m-%d")
        (
            df_fib,
            min_date,
            max_date,
            min_pr,
            max_pr,
        ) = custom_indicators_model.calculate_fib_levels(df_stock, 120, f_start, f_end)

        levels = df_fib.Price
        plt.style.use("seaborn")
        fig, ax = plt.subplots(figsize=(plot_autoscale()), dpi=cfp.PLOT_DPI)

        ax.plot(df_stock["Adj Close"], "b")
        ax.plot([min_date, max_date], [min_pr, max_pr], c="k")

        for i in levels:
            ax.axhline(y=i, c="g", alpha=0.5)

        for i in range(5):
            ax.fill_between(df_stock.index, levels[i], levels[i + 1], alpha=0.6)

        ax.set_ylabel("Price")
        ax.set_title(f"Fibonacci Support for {ticker.upper()}")
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])

        ax1 = ax.twinx()
        ax1.set_ylim(ax.get_ylim())
        ax1.set_yticks(levels)
        ax1.set_yticklabels([0, 0.235, 0.382, 0.5, 0.618, 1])

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)

        plt.savefig("ta_fib.png")
        imagefile = "ta_fib.png"

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

        uploaded_image = gst_imgur.upload_image("ta_fib.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            logger.debug("Image URL: %s", image_link)
        title = "Stocks: Fibonacci-Retracement-Levels " + ticker
        str_df_fib = "```" + df_fib.to_string(index=False) + "```"
        embed = disnake.Embed(title=title, colour=cfg.COLOR, description=str_df_fib)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_fib.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Stocks: Fibonacci-Retracement-Levels",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
