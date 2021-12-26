import discord
import yfinance as yf
from tabulate import tabulate

import discordbot.config_discordbot as cfg
from discordbot.helpers import pagination


async def puts_command(ctx, ticker: str = "", expiration_date: str = ""):
    """Show puts for given ticker and expiration"""
    try:
        # Debug
        if cfg.DEBUG:
            print(f"!stocks.opt.puts {ticker.upper()} {expiration_date}")

            # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")
        puts = yf.Ticker(ticker).option_chain(expiration_date).puts.fillna(0)
        puts = puts[["strike", "bid", "ask", "volume", "openInterest"]]
        puts_string = tabulate(
            puts,
            headers=puts.columns,
            showindex=False,
            tablefmt="pipe",
            numalign="left",
            stralign="center",
        )
        if len(puts_string) <= 4000:
            embed = discord.Embed(
                title=f"Stocks: Put Options [yfinance] for {ticker} on {expiration_date}",
                description="```" + puts_string + "```",
                colour=cfg.COLOR,
            )
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
            await ctx.send(embed=embed)
        else:
            i = 0
            str_start = 0
            str_end = 4000
            columns = []
            while i <= len(puts_string) / 4000:
                columns.append(
                    discord.Embed(
                        title=f"Stocks: Put Options [yfinance] for {ticker} on {expiration_date}",
                        description="```" + puts_string[str_start:str_end] + "```",
                        colour=cfg.COLOR,
                    ).set_author(
                        name=cfg.AUTHOR_NAME,
                        icon_url=cfg.AUTHOR_ICON_URL,
                    )
                )
                str_end = str_start
                str_start += 4000
                i += 1

            await pagination(columns, ctx)

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
