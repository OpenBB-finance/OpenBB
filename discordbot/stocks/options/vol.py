import os
import discord
import matplotlib.pyplot as plt
import discordbot.config_discordbot as cfg

from gamestonk_terminal import config_plot as cfp
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.options import yfinance_model


async def vol_command(
    ctx,
    ticker: str = None,
    expiry: str = "",
    min_sp: float = None,
    max_sp: float = None,
):
    """Options VOL"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.opt.vol {ticker} {expiry} {min_sp} {max_sp}")

        # Check for argument
        if ticker is None:
            raise Exception("Stock ticker is required")

        dates = yfinance_model.option_expirations(ticker)

        if not dates:
            raise Exception("Stock ticker is invalid")

        options = yfinance_model.get_option_chain(ticker, expiry)
        current_price = yfinance_model.get_price(ticker)

        if min_sp is None:
            min_strike = 0.75 * current_price
        else:
            min_strike = min_sp

        if max_sp is None:
            max_strike = 1.25 * current_price
        else:
            max_strike = max_sp

        calls = options.calls
        puts = options.puts
        call_v = calls.set_index("strike")["volume"] / 1000
        put_v = puts.set_index("strike")["volume"] / 1000
        plt.style.use("seaborn")
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)

        put_v.plot(
            x="strike",
            y="volume",
            label="Puts",
            ax=ax,
            marker="o",
            ls="-",
            c="r",
        )
        call_v.plot(
            x="strike",
            y="volume",
            label="Calls",
            ax=ax,
            marker="o",
            ls="-",
            c="g",
        )
        ax.axvline(
            current_price, lw=2, c="k", ls="--", label="Current Price", alpha=0.7
        )
        ax.grid("on")
        ax.set_xlabel("Strike Price")
        ax.set_ylabel("Volume (1k) ")
        ax.set_xlim(min_strike, max_strike)

        ax.set_title(f"Volume for {ticker.upper()} expiring {expiry}")
        plt.legend(loc=0)
        fig.tight_layout(pad=1)

        imagefile = "opt_vol.png"
        plt.savefig("opt_vol.png")
        image = discord.File(imagefile)

        if cfg.DEBUG:
            print(f"Image: {imagefile}")
        title = f"Volume for {ticker.upper()} expiring {expiry}"
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_image(url="attachment://opt_vol.png")
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        os.remove("opt_vol.png")

        await ctx.send(embed=embed, file=image)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Options: Volume",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
