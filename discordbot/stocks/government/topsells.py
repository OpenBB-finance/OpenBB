import os
from datetime import datetime, timedelta

import disnake
import pandas as pd
from matplotlib import pyplot as plt
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import gst_imgur, logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.government import quiverquant_model


async def topsells_command(
    ctx,
    gov_type="",
    past_transactions_months: int = 5,
    num: int = 10,
    raw: bool = False,
):
    """Displays most sold stocks by the congress/senate/house [quiverquant.com]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug(
                "!stocks.gov.topsells %s %s %s %s",
                gov_type,
                past_transactions_months,
                num,
                raw,
            )

        possible_args = ["congress", "senate", "house"]
        if gov_type == "":
            gov_type = "congress"
        elif gov_type not in possible_args:
            raise Exception(
                "Enter a valid government argument, options are: congress, senate and house"
            )

        # Retrieve Data
        df_gov = quiverquant_model.get_government_trading(gov_type)

        # Output Data
        if df_gov.empty:
            raise Exception(f"No {gov_type} trading data found\n")

        df_gov = df_gov.sort_values("TransactionDate", ascending=False)

        start_date = datetime.now() - timedelta(days=past_transactions_months * 30)

        df_gov["TransactionDate"] = pd.to_datetime(df_gov["TransactionDate"])

        df_gov = df_gov[df_gov["TransactionDate"] > start_date].dropna()

        df_gov["Range"] = df_gov["Range"].apply(
            lambda x: "$5,000,001-$5,000,001" if x == ">$5,000,000" else x
        )

        df_gov["min"] = df_gov["Range"].apply(
            lambda x: x.split("-")[0]
            .strip("$")
            .replace(",", "")
            .strip()
            .replace(">$", "")
            .strip()
        )
        df_gov["max"] = df_gov["Range"].apply(
            lambda x: x.split("-")[1]
            .replace(",", "")
            .strip()
            .strip("$")
            .replace(">$", "")
            .strip()
            if "-" in x
            else x.strip("$").replace(",", "").replace(">$", "").strip()
        )

        df_gov["lower"] = df_gov[["min", "max", "Transaction"]].apply(
            lambda x: float(x["min"])
            if x["Transaction"] == "Purchase"
            else -float(x["max"]),
            axis=1,
        )
        df_gov["upper"] = df_gov[["min", "max", "Transaction"]].apply(
            lambda x: float(x["max"])
            if x["Transaction"] == "Purchase"
            else -float(x["min"]),
            axis=1,
        )

        df_gov = df_gov.sort_values("TransactionDate", ascending=True)
        if raw:
            df = pd.DataFrame(
                df_gov.groupby("Ticker")["upper"]
                .sum()
                .div(1000)
                .sort_values(ascending=True)
                .abs()
                .head(n=num)
            )
            description = "```" + df.to_string() + "```"
        plt.style.use("seaborn")
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        df_gov.groupby("Ticker")["upper"].sum().div(1000).sort_values().abs().head(
            n=num
        ).plot(kind="bar", rot=0, ax=ax)
        ax.set_ylabel("Amount ($1k)")
        ax.set_title(
            f"{num} most sold stocks over last {past_transactions_months} months"
            f" (upper bound) for {gov_type}"
        )
        plt.gcf().axes[0].yaxis.get_major_formatter().set_scientific(False)
        fig.tight_layout()

        plt.savefig("gov_topsells.png")
        imagefile = "gov_topsells.png"

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

        uploaded_image = gst_imgur.upload_image("gov_topsells.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            logger.debug("Image URL: %s", image_link)
        title = f"Stocks: [quiverquant.com] Top sells for {gov_type.upper()}"
        if raw:
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
        os.remove("gov_topsells.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = disnake.Embed(
            title=f"ERROR Stocks: [quiverquant.com] Top sells for {gov_type.upper()}",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
