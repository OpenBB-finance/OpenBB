import os

import discord
import matplotlib.pyplot as plt
import pandas as pd
import yfinance as yf

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import gst_imgur
from gamestonk_terminal.config_plot import PLOT_DPI
from gamestonk_terminal.helper_funcs import plot_autoscale
from gamestonk_terminal.stocks.options import op_helpers


async def oi_command(ctx, ticker: str = "", expiration_date: str = ""):
    """Show open interest for expiration and ticker"""
    try:
        # Debug
        if cfg.DEBUG:
            print(f"!stocks.opt.oi {ticker.upper()} {expiration_date}")

            # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        fig, ax = plt.subplots(figsize=plot_autoscale(), dpi=PLOT_DPI)

        options = yf.Ticker(ticker).option_chain(expiration_date)
        calls = options.calls
        puts = options.puts
        call_oi = calls.set_index("strike")["openInterest"] / 1000
        put_oi = puts.set_index("strike")["openInterest"] / 1000

        df_opt = pd.merge(call_oi, put_oi, left_index=True, right_index=True)
        df_opt = df_opt.rename(
            columns={"openInterest_x": "OI_call", "openInterest_y": "OI_put"}
        )

        df_opt = pd.merge(call_oi, put_oi, left_index=True, right_index=True).fillna(0)
        df_opt = df_opt.rename(
            columns={"openInterest_x": "OI_call", "openInterest_y": "OI_put"}
        )
        max_pain = op_helpers.calculate_max_pain(df_opt)
        current_price = float(yf.Ticker(ticker).info["regularMarketPrice"])

        call_oi.plot(
            x="strike",
            y="openInterest",
            label="Calls",
            ax=ax,
            marker="o",
            ls="-",
            c="g",
        )
        put_oi.plot(
            x="strike",
            y="openInterest",
            label="Puts",
            ax=ax,
            marker="o",
            ls="-",
            c="r",
        )

        ax.set_xlabel("Strike Price")
        ax.set_ylabel("Open Interest (1k)")
        ax.axvline(
            current_price, lw=2, c="k", ls="--", label="Current Price", alpha=0.4
        )
        ax.axvline(max_pain, lw=3, c="k", label=f"Max Pain: {max_pain}", alpha=0.4)
        ax.set_title(f"Open Interest for {ticker.upper()} on {expiration_date}")

        ax.grid("on")
        ax.legend()
        fig.tight_layout()
        plt.savefig("OI.png")
        uploaded_image = gst_imgur.upload_image("OI.png", title="something")
        image_link = uploaded_image.link
        if cfg.DEBUG:
            print(f"Image URL: {image_link}")
        title = f"Open Interest for {ticker} on {expiration_date}"
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_image(url=image_link)
        os.remove("OI.png")

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stock-Options: Open Interest",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
