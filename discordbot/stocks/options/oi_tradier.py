import os
import discord
from matplotlib import pyplot as plt
import pandas as pd


import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur

from gamestonk_terminal import config_plot as cfp
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.options import op_helpers, tradier_model


async def oi_command(ctx, ticker: str= None, expiry: str= None, min_sp: float= None, max_sp: float= None):
    """Options OI"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!oi {ticker} {expiry} {min_sp} {max_sp}")

        # Check for argument
        if ticker is None:
            raise Exception("Stock ticker is required")    
        
        dates = tradier_model.option_expirations(ticker)

        if not dates:
            raise Exception("Stock ticker is invalid")
        
        options = tradier_model.get_option_chains(ticker, expiry)
        current_price = tradier_model.last_price(ticker)


        if min_sp is None:
            min_strike = 0.75 * current_price
        else:
            min_strike = min_sp

        if max_sp is None:
            max_strike = 1.90 * current_price
        else:
            max_strike = max_sp

        calls = options[options.option_type == "call"][["strike", "open_interest"]]
        puts = options[options.option_type == "put"][["strike", "open_interest"]]
        call_oi = calls.set_index("strike")["open_interest"] / 1000
        put_oi = puts.set_index("strike")["open_interest"] / 1000

        df_opt = pd.merge(call_oi, put_oi, left_index=True, right_index=True)
        df_opt = df_opt.rename(
              columns={"open_interest_x": "OI_call", "open_interest_y": "OI_put"}
        )

        max_pain = op_helpers.calculate_max_pain(df_opt)
        plt.style.use("seaborn")
        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=cfp.PLOT_DPI)


        put_oi.plot(
            x="strike",
            y="open_interest",
            label="Puts",
            ax=ax,
            marker="o",
            ls="-",
            c="r",
        )
        call_oi.plot(
            x="strike",
            y="open_interest",
            label="Calls",
            ax=ax,
            marker="o",
            ls="-",
            c="g",
        )
        ax.axvline(
            current_price, lw=2, c="k", ls="--", label="Current Price", alpha=0.7
        )
        ax.axvline(max_pain, lw=3, c="k", label=f"Max Pain: {max_pain}", alpha=0.7)
        ax.grid("on")
        ax.set_xlabel("Strike Price")
        ax.set_ylabel("Open Interest (1k) ")
        ax.set_xlim(min_strike, max_strike)

        ax.set_title(f"Open Interest for {ticker.upper()} expiring {expiry}")
        plt.legend(loc=0)
        fig.tight_layout(pad=1)

        imagefile = "opt_oi.png"
        plt.savefig("opt_oi.png")
        image = discord.File(imagefile)
        
        if cfg.DEBUG:
            print(f"Image URL: {imagefile}")
        title = " " + ticker.upper() + " Options: Open Interest"
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_image(
            url="attachment://opt_oi.png"
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )        
        os.remove("opt_oi.png")

        await ctx.send(embed=embed, file=image)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Options: Open Interest",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        
        await ctx.send(embed=embed)
