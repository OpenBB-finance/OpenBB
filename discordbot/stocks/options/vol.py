import os
import discord
import matplotlib.pyplot as plt
import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur

from gamestonk_terminal import config_plot as cfp
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.options import tradier_model




async def vol_command(ctx, ticker="", expiry=""):
    """Options VOL"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!vol {ticker} {expiry}")

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")    
        
        dates = tradier_model.option_expirations(ticker)

        if not dates:
            raise Exception("Stock ticker is invalid")
        
        options = tradier_model.get_option_chains(ticker, expiry)
        current_price = tradier_model.last_price(ticker)
        min_strike = 0.75 * current_price
        max_strike = 1.90 * current_price

        if current_price > 100:
            max_strike = 2.25 * current_price
        if current_price > 500:
            min_strike = 0.50 * current_price
            max_strike = 1.25 * current_price      


        calls = options[options.option_type == "call"][["strike", "volume"]]
        puts = options[options.option_type == "put"][["strike", "volume"]]
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
        ax.axvline(current_price, lw=2, c="k", ls="--", label="Current Price", alpha=0.7)
        ax.grid("on")
        ax.set_xlabel("Strike Price")
        ax.set_ylabel("Volume (1k) ")
        ax.set_xlim(min_strike, max_strike)

        ax.set_title(f"Volume for {ticker.upper()} expiring {expiry}")
        plt.legend(loc=0)
        fig.tight_layout(pad=1)

        plt.style.use("seaborn")

        plt.savefig("opt_vol.png")
        uploaded_image = gst_imgur.upload_image("opt_vol.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = " " + ticker.upper() + " Options: Volume"
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_image(url=image_link)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        os.remove("opt_vol.png")

        await ctx.send(embed=embed)

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
