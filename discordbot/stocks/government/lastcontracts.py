import disnake
import pandas as pd
from menus.menu import Menu

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from gamestonk_terminal.stocks.government import quiverquant_model


async def lastcontracts_command(ctx, past_transactions_days: int = 2, num: int = 20):
    """Displays last government contracts [quiverquant.com]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.gov.lastcontracts %s %s", past_transactions_days, num)

        df_contracts = quiverquant_model.get_government_trading("contracts")

        if df_contracts.empty:
            logger.debug("No government contracts found")
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
        choices = [
            disnake.SelectOption(label="Overview", value="0", emoji="🟢"),
        ]
        initial_str = "Overview"
        i = 1
        for col_name in df_contracts["Ticker"].values:
            menu = f"\nPage {i}: {col_name}"
            initial_str += f"\nPage {i}: {col_name}"
            choices.append(
                disnake.SelectOption(label=menu, value=f"{i}", emoji="🟢"),
            )
            i += 1

        columns = []
        df_contracts = df_contracts.T
        columns.append(
            disnake.Embed(
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
                disnake.Embed(
                    description="```"
                    + df_contracts[column].fillna("").to_string()
                    + "```",
                    colour=cfg.COLOR,
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )

        await ctx.send(embed=columns[0], view=Menu(columns, choices))

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Stocks: [quiverquant.com] Top buy government trading",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
