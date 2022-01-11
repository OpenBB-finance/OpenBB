import discord

from gamestonk_terminal.stocks.government import quiverquant_model

import discordbot.config_discordbot as cfg
from discordbot.run_discordbot import logger
from discordbot.helpers import pagination


async def lasttrades_command(
    ctx, gov_type="", past_transactions_days="", representative=""
):
    """Displays trades made by the congress/senate/house [quiverquant.com]"""
    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug(
                "!stocks.gov.lasttrades %s %s %s",
                gov_type,
                past_transactions_days,
                representative,
            )

        if past_transactions_days == "":
            past_days = 5
        else:
            if not past_transactions_days.lstrip("-").isnumeric():
                raise Exception("Number has to be an integer")
            past_days = int(past_transactions_days)

        possible_args = ["congress", "senate", "house"]
        if gov_type == "":
            gov_type = "congress"
        elif gov_type not in possible_args:
            raise Exception(
                "Enter a valid government argument, options are: congress, senate and house"
            )

        # Retrieve Data
        df_gov = quiverquant_model.get_government_trading(gov_type)

        # Output Data
        if df_gov.empty:
            raise Exception(f"No {gov_type} trading data found")
        df_gov = df_gov.sort_values("TransactionDate", ascending=False)

        df_gov = df_gov[
            df_gov["TransactionDate"].isin(
                df_gov["TransactionDate"].unique()[:past_days]
            )
        ]

        if gov_type == "congress":
            df_gov = df_gov[
                [
                    "TransactionDate",
                    "Ticker",
                    "Representative",
                    "Transaction",
                    "Range",
                    "House",
                    "ReportDate",
                ]
            ].rename(
                columns={
                    "TransactionDate": "Transaction Date",
                    "ReportDate": "Report Date",
                }
            )
        else:
            df_gov = df_gov[
                [
                    "TransactionDate",
                    "Ticker",
                    "Representative",
                    "Transaction",
                    "Range",
                ]
            ].rename(columns={"TransactionDate": "Transaction Date"})

        if representative:
            df_gov_rep = df_gov[
                df_gov["Representative"].str.split().str[0] == representative
            ]

            if df_gov_rep.empty:
                raise Exception(
                    f"No representative {representative} found in the past {past_days}"
                    f" days. The following are available: "
                    f"{', '.join(df_gov['Representative'].str.split().str[0].unique())}"
                )

            initial_str = "Page 0: Overview"
            i = 1
            for col_name in df_gov_rep["Ticker"].values:
                initial_str += f"\nPage {i}: {col_name}"
                i += 1

            columns = []
            df_gov_rep = df_gov_rep.T
            columns.append(
                discord.Embed(
                    title=f"Stocks: [quiverquant.com] Trades by {representative}",
                    description=initial_str,
                    colour=cfg.COLOR,
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )
            for column in df_gov_rep.columns.values:
                columns.append(
                    discord.Embed(
                        description="```"
                        + df_gov_rep[column].fillna("").to_string()
                        + "```",
                        colour=cfg.COLOR,
                    ).set_author(
                        name=cfg.AUTHOR_NAME,
                        icon_url=cfg.AUTHOR_ICON_URL,
                    )
                )

            await pagination(columns, ctx)

        else:
            initial_str = "Page 0: Overview"
            i = 1
            for col_name in df_gov["Ticker"].values:
                initial_str += f"\nPage {i}: {col_name}"
                i += 1

            columns = []
            df_gov = df_gov.T
            columns.append(
                discord.Embed(
                    title=f"Stocks: [quiverquant.com] Trades for {gov_type.upper()}",
                    description=initial_str,
                    colour=cfg.COLOR,
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )

            for column in df_gov.columns.values:
                columns.append(
                    discord.Embed(
                        description="```"
                        + df_gov[column].fillna("").to_string()
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
            title=f"ERROR Stocks: [quiverquant.com] Trades by {gov_type.upper()}",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
