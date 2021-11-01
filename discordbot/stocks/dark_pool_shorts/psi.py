import os
from datetime import timedelta
from matplotlib import pyplot as plt
import yfinance as yf
import discord
import config_discordbot as cfg
from discordbot import gst_imgur
from gamestonk_terminal.config_plot import PLOT_DPI

from gamestonk_terminal.stocks.dark_pool_shorts import stockgrid_model


async def psi_command(ctx, ticker=""):
    """Price vs short interest volume [Stockgrid]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            print(f"\n!stocks.dps.psi {ticker}")

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        ticker = ticker.upper()

        stock = yf.download(ticker, progress=False)
        if stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve data
        df, prices = stockgrid_model.get_short_interest_volume(ticker)

        # Debug user output
        if cfg.DEBUG:
            print(df.to_string())

        # Output data
        title = f"Stocks: [Stockgrid] Price vs Short Interest Volume {ticker}"
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        _, axes = plt.subplots(
            2,
            1,
            dpi=PLOT_DPI,
            gridspec_kw={"height_ratios": [2, 1]},
        )

        axes[0].bar(
            df["date"],
            df["total_volume"] / 1_000_000,
            width=timedelta(days=1),
            color="b",
            alpha=0.4,
            label="Total Volume",
        )
        axes[0].bar(
            df["date"],
            df["short_volume"] / 1_000_000,
            width=timedelta(days=1),
            color="r",
            alpha=0.4,
            label="Short Volume",
        )

        axes[0].set_ylabel("Volume (1M)")
        ax2 = axes[0].twinx()
        ax2.plot(
            df["date"].values, prices[len(prices) - len(df) :], c="k", label="Price"
        )
        ax2.set_ylabel("Price ($)")

        lines, labels = axes[0].get_legend_handles_labels()
        lines2, labels2 = ax2.get_legend_handles_labels()
        ax2.legend(lines + lines2, labels + labels2, loc="upper left")

        axes[0].grid()
        axes[0].ticklabel_format(style="plain", axis="y")
        plt.title(f"Price vs Short Volume Interest for {ticker}")
        plt.gcf().autofmt_xdate()

        axes[1].plot(
            df["date"].values,
            100 * df["short_volume%"],
            c="green",
            label="Short Vol. %",
        )

        axes[1].set_ylabel("Short Vol. %")

        axes[1].grid(axis="y")
        lines, labels = axes[1].get_legend_handles_labels()
        axes[1].legend(lines, labels, loc="upper left")
        axes[1].set_ylim([0, 100])
        file_name = ticker + "_psi.png"
        plt.savefig(file_name)
        plt.close("all")
        uploaded_image = gst_imgur.upload_image(file_name, title="something")
        image_link = uploaded_image.link
        embed.set_image(url=image_link)
        os.remove(file_name)

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title=f"ERROR Stocks: [Stockgrid] Price vs Short Interest Volume {ticker}",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
