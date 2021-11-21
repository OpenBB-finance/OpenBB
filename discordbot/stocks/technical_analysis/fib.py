import discord
import config_discordbot as cfg
from discordbot import gst_imgur
from datetime import datetime, timedelta
from matplotlib import pyplot as plt
import os
import helpers

from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.common.technical_analysis import custom_indicators_model
from gamestonk_terminal import config_plot as cfp


async def fib_command(ctx, ticker="", start="", end=""):
    """Displays chart with fibonacci retracement [Yahoo Finance]"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.ta.fib {ticker} {start} {end}")

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

        ticker = ticker.upper()
        df_stock = helpers.load(ticker, start)
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
        ) = custom_indicators_model.calculate_fib_levels(df_stock, 120, start, end)

        levels = df_fib.Price
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
        uploaded_image = gst_imgur.upload_image("ta_fib.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = "Stocks: Fibonacci-Retracement-Levels " + ticker
        str_df_fib = "```" + df_fib.to_string(index=False) + "```"
        embed = discord.Embed(title=title, colour=cfg.COLOR, description=str_df_fib)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_fib.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: Fibonacci-Retracement-Levels",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
