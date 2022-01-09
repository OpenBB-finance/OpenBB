import os
from datetime import datetime, timedelta
import discord
from matplotlib import pyplot as plt

from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.common.technical_analysis import momentum_model
from gamestonk_terminal.config_plot import PLOT_DPI

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur, logger
import discordbot.helpers


async def stoch_command(
    ctx, ticker="", fast_k="14", slow_d="3", slow_k="3", start="", end=""
):
    """Displays chart with stochastic relative strength average [Yahoo Finance]"""

    try:

        # Debug
        if cfg.DEBUG:
            logger.debug(
                "!stocks.ta.stoch %s %s %s %s %s %s",
                ticker,
                fast_k,
                slow_k,
                slow_d,
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

        if not fast_k.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")
        fast_k = int(fast_k)
        if not slow_k.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")
        slow_k = int(slow_k)
        if not slow_d.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")
        slow_d = int(slow_d)

        ticker = ticker.upper()
        df_stock = discordbot.helpers.load(ticker, start)
        if df_stock.empty:
            raise Exception("Stock ticker is invalid")

        # Retrieve Data
        df_stock = df_stock.loc[(df_stock.index >= start) & (df_stock.index < end)]

        df_ta = momentum_model.stoch(
            df_stock["High"],
            df_stock["Low"],
            df_stock["Adj Close"],
            fast_k,
            slow_d,
            slow_k,
        )

        # Output Data
        fig, axes = plt.subplots(2, 1, figsize=plot_autoscale(), dpi=PLOT_DPI)
        ax = axes[0]
        ax.plot(df_stock.index, df_stock["Adj Close"].values, "k", lw=2)
        ax.set_title(f"Stochastic Relative Strength Index (STOCH RSI) on {ticker}")
        ax.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax.set_xticklabels([])
        ax.set_ylabel("Share Price ($)")
        ax.grid(b=True, which="major", color="#666666", linestyle="-")

        ax2 = axes[1]
        ax2.plot(df_ta.index, df_ta.iloc[:, 0].values, "k", lw=2)
        ax2.plot(df_ta.index, df_ta.iloc[:, 1].values, "b", lw=2, ls="--")
        ax2.set_xlim(df_stock.index[0], df_stock.index[-1])
        ax2.axhspan(80, 100, facecolor="r", alpha=0.2)
        ax2.axhspan(0, 20, facecolor="g", alpha=0.2)
        ax2.axhline(80, linewidth=3, color="r", ls="--")
        ax2.axhline(20, linewidth=3, color="g", ls="--")
        ax2.grid(b=True, which="major", color="#666666", linestyle="-")
        ax2.set_ylim([0, 100])

        ax3 = ax2.twinx()
        ax3.set_ylim(ax2.get_ylim())
        ax3.set_yticks([20, 80])
        ax3.set_yticklabels(["OVERSOLD", "OVERBOUGHT"])
        ax2.legend(
            [f"%K {df_ta.columns[0]}", f"%D {df_ta.columns[1]}"], loc="lower left"
        )

        plt.gcf().autofmt_xdate()
        fig.tight_layout(pad=1)

        plt.savefig("ta_stoch.png")
        uploaded_image = gst_imgur.upload_image("ta_stoch.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            logger.debug("Image URL: %s", image_link)
        title = "Stocks: Stochastic-Relative-Strength-Index " + ticker
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("ta_stoch.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: Stochastic-Relative-Strength-Index",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
