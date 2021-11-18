import discord
import config_discordbot as cfg
from helpers import pagination
import pandas as pd

from gamestonk_terminal.stocks.government import quiverquant_model


async def lastcontracts_command(ctx, past_transactions_days="", num=""):
    """Displays last government contracts [quiverquant.com]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            print(f"!stocks.gov.lastcontracts {past_transactions_days} {num}")

        if past_transactions_days == "":
            past_transactions_days = 2
        else:
            if not past_transactions_days.lstrip("-").isnumeric():
                raise Exception("Number has to be an integer")
            past_transactions_days = float(past_transactions_days)

        if num == "":
            num = 20
        else:
            if not num.lstrip("-").isnumeric():
                raise Exception("Number has to be an integer")
            num = int(num)

        df_contracts = quiverquant_model.get_government_trading("contracts")

        if df_contracts.empty:
            print("No government contracts found\n")
            return

        df_contracts.sort_values("Date", ascending=False)

        df_contracts["Date"] = pd.to_datetime(df_contracts["Date"])

        df_contracts.drop_duplicates(inplace=True)
        df_contracts = df_contracts[
            df_contracts["Date"].isin(
                df_contracts["Date"].unique()[:past_transactions_days]
            )
        ]

        df_contracts = df_contracts[
            ["Date", "Ticker", "Amount", "Description", "Agency"]
        ][:num]
        df_contracts_str = df_contracts.to_string()
        if len(df_contracts_str) <= 4000:
            embed = discord.Embed(
                title="Stocks: [quiverquant.com] Top buy government trading",
                description="```" + df_contracts_str + "```",
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
            while i <= len(df_contracts_str) / 4000:
                columns.append(
                    discord.Embed(
                        title="Stocks: [quiverquant.com] Top buy government trading",
                        description="```" + df_contracts_str[str_start:str_end] + "```",
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
            title="ERROR Stocks: [quiverquant.com] Top buy government trading",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
