import discord
import pandas as pd

from gamestonk_terminal.stocks.government import quiverquant_model
import discordbot.config_discordbot as cfg
from discordbot.helpers import pagination


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
        df_contracts["Date"] = df_contracts["Date"].dt.date

        df_contracts.drop_duplicates(inplace=True)
        df_contracts = df_contracts[
            df_contracts["Date"].isin(
                df_contracts["Date"].unique()[:past_transactions_days]
            )
        ]

        df_contracts = df_contracts[["Date", "Ticker", "Amount", "Agency"]][:num]

        initial_str = "Page 0: Overview"
        i = 1
        for col_name in df_contracts["Ticker"].values:
            initial_str += f"\nPage {i}: {col_name}"
            i += 1

        columns = []
        df_contracts = df_contracts.T
        columns.append(
            discord.Embed(
                title="Stocks: [quiverquant.com] Top buy government trading",
                description=initial_str,
                colour=cfg.COLOR,
            ).set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
        )
        for column in df_contracts.columns.values:
            columns.append(
                discord.Embed(
                    description="```"
                    + df_contracts[column].fillna("").to_string()
                    + "```",
                    colour=cfg.COLOR,
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )

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
