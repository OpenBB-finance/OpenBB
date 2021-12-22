import discord
import pandas as pd
import yfinance as yf

import discordbot.config_discordbot as cfg


async def expirations_command(ctx, ticker: str = ""):
    """Show expirations for given ticker"""
    try:
        # Debug
        if cfg.DEBUG:
            print(f"!stocks.opt.exp {ticker.upper()}")

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        expirations_df = pd.DataFrame(yf.Ticker(ticker.upper()).options)
        expirations_df.columns = ["Expirations"]

        embed = discord.Embed(
            title=f"Options Expirations for {ticker}",
            description="```" + expirations_df.to_string(index=False) + "```",
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stock-Options: Expirations",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
