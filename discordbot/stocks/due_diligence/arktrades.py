import discord
import config_discordbot as cfg
from helpers import pagination
import pandas as pd

from gamestonk_terminal.stocks.due_diligence import ark_model


async def arktrades_command(ctx, ticker="", num=""):
    """Displays trades made by ark [cathiesark.com]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            print(f"!stocks.dd.arktrades{ticker}")

        if num == "":
            pass
        else:
            if not num.lstrip("-").isnumeric():
                raise Exception("Number has to be an integer")
            num = float(num)

        if ticker == "":
            raise Exception("A ticker is required")

        ark_holdings = ark_model.get_ark_trades_by_ticker(ticker)

        if ark_holdings.empty:
            raise Exception(
                "Issue getting data from cathiesark.com. Likely no trades found.\n"
            )

        ark_holdings = ark_holdings.drop(columns=["ticker"])
        ark_holdings["Total"] = ark_holdings["Total"] / 1_000_000
        ark_holdings.rename(
            columns={"Close": "Close ($)", "Total": "Total ($1M)"}, inplace=True
        )

        ark_holdings.index = pd.Series(ark_holdings.index).apply(
            lambda x: x.strftime("%Y-%m-%d")
        )

        if num == "":
            ark_holdings_str = ark_holdings.to_string()
        else:
            ark_holdings_str = ark_holdings.head(num).to_string()

        if len(ark_holdings_str) <= 4000:
            embed = discord.Embed(
                title=f"Stocks: [cathiesark.com] {ticker} Trades by Ark",
                description="```" + ark_holdings_str + "```",
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
            while i <= len(ark_holdings_str) / 4000:
                columns.append(
                    discord.Embed(
                        title=f"Stocks: [cathiesark.com] {ticker} Trades by Ark",
                        description="```" + ark_holdings_str[str_start:str_end] + "```",
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

    except Exception as e:
        embed = discord.Embed(
            title=f"ERROR Stocks: [cathiesark.com] {ticker} Trades by Ark",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
