import discord
import config_discordbot as cfg
from discordbot import gst_imgur
from matplotlib import pyplot as plt
import os
import numpy as np

from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.stocks.government import quiverquant_model
from gamestonk_terminal.helper_funcs import plot_autoscale


async def qtrcontracts_command(ctx, num="", analysis=""):
    """Displays a look at government contracts [quiverquant.com]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            print(f"!stocks.gov.qtrcontracts {num} {analysis}")

        if num == "":
            num = 20
        else:
            if not num.lstrip("-").isnumeric():
                raise Exception("Number has to be an integer")
            num = int(num)

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
            uploaded_image = gst_imgur.upload_image(
                "gov_qtrcontracts.png", title="something"
            )
            image_link = uploaded_image.link
            if cfg.DEBUG:
                print(f"Image URL: {image_link}")
            title = "Stocks: [quiverquant.com] Government contracts"
            embed = discord.Embed(
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
            description = tickers.to_string()
            embed = discord.Embed(
                title="Stocks: [quiverquant.com] Government contracts",
                description=description,
                colour=cfg.COLOR,
            )
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )

            await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: [quiverquant.com] Government contracts",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
