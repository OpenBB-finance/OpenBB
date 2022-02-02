import os
from datetime import datetime, timedelta

import disnake
import matplotlib.dates as mdates
import pandas as pd
from matplotlib import pyplot as plt
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import gst_imgur, logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.government import quiverquant_model


async def gtrades_command(
    ctx,
    ticker: str = "",
    gov_type="",
    past_transactions_months: int = 10,
    raw: bool = False,
):
    """Displays government trades [quiverquant.com]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug(
                "!stocks.gov.gtrades %s %s %s %s",
                ticker,
                gov_type,
                past_transactions_months,
                raw,
            )

        if ticker == "":
            raise Exception("A ticker is required")

        possible_args = ["congress", "senate", "house"]
        if gov_type == "":
            gov_type = "congress"
        elif gov_type not in possible_args:
            raise Exception(
                "Enter a valid government argument, options are: congress, senate and house"
            )

        # Retrieve Data
        df_gov = quiverquant_model.get_government_trading(gov_type, ticker)

        if df_gov.empty:
            raise Exception(f"No {gov_type} trading data found")

        # Output Data
        df_gov = df_gov.sort_values("TransactionDate", ascending=False)

        start_date = datetime.now() - timedelta(days=past_transactions_months * 30)

        df_gov["TransactionDate"] = pd.to_datetime(df_gov["TransactionDate"])

        df_gov = df_gov[df_gov["TransactionDate"] > start_date]

        if df_gov.empty:
            logger.debug("No recent %s trading data found", gov_type)
            return

        df_gov["min"] = df_gov["Range"].apply(
            lambda x: x.split("-")[0].strip("$").replace(",", "").strip()
        )
        df_gov["max"] = df_gov["Range"].apply(
            lambda x: x.split("-")[1].replace(",", "").strip().strip("$")
            if "-" in x
            else x.strip("$").replace(",", "").split("\n")[0]
        )

        df_gov["lower"] = df_gov[["min", "max", "Transaction"]].apply(
            lambda x: int(float(x["min"]))
            if x["Transaction"] == "Purchase"
            else -int(float(x["max"])),
            axis=1,
        )
        df_gov["upper"] = df_gov[["min", "max", "Transaction"]].apply(
            lambda x: int(float(x["max"]))
            if x["Transaction"] == "Purchase"
            else -1 * int(float(x["min"])),
            axis=1,
        )

        df_gov = df_gov.sort_values("TransactionDate", ascending=True)
        plt.style.use("seaborn")

        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        ax.fill_between(
            df_gov["TransactionDate"].unique(),
            df_gov.groupby("TransactionDate")["lower"].sum().values / 1000,
            df_gov.groupby("TransactionDate")["upper"].sum().values / 1000,
        )

        ax.set_xlim(
            [
                df_gov["TransactionDate"].values[0],
                df_gov["TransactionDate"].values[-1],
            ]
        )
        ax.grid()
        ax.set_title(f"{gov_type.capitalize()} trading on {ticker}")
        ax.set_xlabel("Date")
        ax.set_ylabel("Amount ($1k)")
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y/%m/%d"))
        plt.gcf().autofmt_xdate()
        fig.tight_layout()

        plt.savefig("gov_gtrades.png")
        imagefile = "gov_gtrades.png"

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

        uploaded_image = gst_imgur.upload_image("gov_gtrades.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            logger.debug("Image URL: %s", image_link)
        title = "Stocks: [quiverquant.com] Government Trades"
        if raw:
            description = df_gov.to_string()
            embed = disnake.Embed(
                title=title, description=description, colour=cfg.COLOR
            )
        else:
            embed = disnake.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("gov_gtrades.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Stocks: [quiverquant.com] Government Trades",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
