import discord
import config_discordbot as cfg
from helpers import pagination

from gamestonk_terminal.economy import finviz_model


async def performance_command(ctx, arg):
    economy_group = {
        "sector": "Sector",
        "industry": "Industry",
        "basic_materials": "Industry (Basic Materials)",
        "communication services": "Industry (Communication Services)",
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

    # Help
    if arg == "-h" or arg == "help":
        help_txt = "Group performance [Source: Finviz]\n"

        possible_args = ""
        for k, v in economy_group.items():
            possible_args += f"\n{k}: {v}"

        help_txt += "\nPossible arguments:\n"
        help_txt += "<GROUP> Groups to get data from. Default: sector\n"
        help_txt += f"The choices are:{possible_args}"
        embed = discord.Embed(
            title="Economy: [Finviz] Performance HELP",
            description=help_txt,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)

    else:
        # Select default
        if not arg:
            arg = "sector"

        # Parse argument
        group = economy_group[arg]

        df_group = finviz_model.get_valuation_performance_data(group, "performance")

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
                title=f"Economy: [Finviz] Performance {group}",
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
