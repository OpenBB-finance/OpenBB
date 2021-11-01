import discord
import config_discordbot as cfg
from helpers import pagination

from gamestonk_terminal.economy import finviz_model


async def valuation_command(ctx, economy_group="sector"):
    """Valuation of sectors, industry, country [Finviz]"""

    d_economy_group = {
        "sector": "Sector",
        "industry": "Industry",
        "basic_materials": "Industry (Basic Materials)",
        "communication_services": "Industry (Communication Services)",
        "consumer_cyclical": "Industry (Consumer Cyclical)",
        "consumer_defensive": "Industry (Consumer Defensive)",
        "energy": "Industry (Energy)",
        "financial": "Industry (Financial)",
        "healthcare": "Industry (Healthcare)",
        "industrials": "Industry (Industrials)",
        "real_estate": "Industry (Real Estate)",
        "technology": "Industry (Technology)",
        "utilities": "Industry (Utilities)",
        "country": "Country (U.S. listed stocks only)",
        "capitalization": "Capitalization",
    }

    try:
        # Debug user input
        if cfg.DEBUG:
            print(f"\n!economy.valuation {economy_group}")

        # Select default group
        if economy_group == "":
            if cfg.DEBUG:
                print("Use default economy_group: 'sector'")
            economy_group = "sector"

        # Check for argument
        possible_groups = list(d_economy_group.keys())

        if economy_group not in possible_groups:
            raise Exception(f"Select a valid group from {', '.join(possible_groups)}")

        group = d_economy_group[economy_group]

        # Retrieve data
        df_group = finviz_model.get_valuation_performance_data(group, "valuation")

        # Debug user output
        if cfg.DEBUG:
            print(df_group.to_string())

        # Output data
        future_column_name = df_group["Name"]
        df_group = df_group.transpose()
        df_group.columns = future_column_name
        df_group.drop("Name")
        columns = []

        initial_str = "Page 0: Overview"
        i = 1
        for col_name in df_group.columns.values:
            initial_str += f"\nPage {i}: {col_name}"
            i += 1

        columns.append(
            discord.Embed(
                title=f"Economy: [Finviz] Valuation {group}",
                description=initial_str,
                colour=cfg.COLOR,
            ).set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
        )
        for column in df_group.columns.values:
            columns.append(
                discord.Embed(
                    description="```" + df_group[column].fillna("").to_string() + "```",
                    colour=cfg.COLOR,
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )

        await pagination(columns, ctx)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Economy: [Finviz] Valuation",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
