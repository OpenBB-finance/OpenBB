import os

import disnake
import numpy as np
from matplotlib import pyplot as plt
from PIL import Image

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import gst_imgur, logger
from discordbot.helpers import autocrop_image
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.government import quiverquant_model


async def qtrcontracts_command(ctx, num: int = 20, analysis=""):
    """Displays a look at government contracts [quiverquant.com]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.gov.qtrcontracts %s %s", num, analysis)

        possible_args = ["total", "upmom", "downmom"]
        if analysis == "":
            analysis = "total"
        elif analysis not in possible_args:
            raise Exception(
                "Enter a valid analysis argument, options are: total, upmom and downmom"
            )

        # Retrieve Data
        df_contracts = quiverquant_model.get_government_trading("quarter-contracts")

        if df_contracts.empty:
            raise Exception("No quarterly government contracts found")

        tickers = quiverquant_model.analyze_qtr_contracts(analysis, num)
        plt.style.use("seaborn")

        # Output Data
        if analysis in {"upmom", "downmom"}:
            description = tickers.to_string()
            fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)
            max_amount = 0
            quarter_ticks = []
            for symbol in tickers:
                amounts = (
                    df_contracts[df_contracts["Ticker"] == symbol]
                    .sort_values(by=["Year", "Qtr"])["Amount"]
                    .values
                )

                qtr = (
                    df_contracts[df_contracts["Ticker"] == symbol]
                    .sort_values(by=["Year", "Qtr"])["Qtr"]
                    .values
                )
                year = (
                    df_contracts[df_contracts["Ticker"] == symbol]
                    .sort_values(by=["Year", "Qtr"])["Year"]
                    .values
                )

                ax.plot(
                    np.arange(0, len(amounts)), amounts / 1_000_000, "-*", lw=2, ms=15
                )

                if len(amounts) > max_amount:
                    max_amount = len(amounts)
                    quarter_ticks = [
                        f"{quarter[0]} - Q{quarter[1]} " for quarter in zip(year, qtr)
                    ]

            ax.set_xlim([-0.5, max_amount - 0.5])
            ax.set_xticks(np.arange(0, max_amount))
            ax.set_xticklabels(quarter_ticks)
            ax.grid()
            ax.legend(tickers)
            titles = {
                "upmom": "Highest increasing quarterly Government Contracts",
                "downmom": "Highest decreasing quarterly Government Contracts",
            }
            ax.set_title(titles[analysis])
            ax.set_xlabel("Date")
            ax.set_ylabel("Amount ($1M)")
            fig.tight_layout()

            plt.savefig("gov_qtrcontracts.png")
            imagefile = "gov_qtrcontracts.png"

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

            uploaded_image = gst_imgur.upload_image(
                "gov_qtrcontracts.png", title="something"
            )
            image_link = uploaded_image.link
            if cfg.DEBUG:
                logger.debug("Image URL: %s", image_link)
            title = "Stocks: [quiverquant.com] Government contracts"
            embed = disnake.Embed(
                title=title, description=description, colour=cfg.COLOR
            )
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
            embed.set_image(url=image_link)
            os.remove("gov_qtrcontracts.png")

            await ctx.send(embed=embed)

        elif analysis == "total":

            tickers.index = [ind + " " * (7 - len(ind)) for ind in tickers.index]
            tickers[:] = [str(round(val[0] / 1e9, 2)) for val in tickers.values]
            tickers.columns = ["Amount [M]"]

            embed = disnake.Embed(
                title="Stocks: [quiverquant.com] Government contracts",
                description=tickers.to_string(),
                colour=cfg.COLOR,
            )
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )

            await ctx.send(embed=embed)

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Stocks: [quiverquant.com] Government contracts",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
