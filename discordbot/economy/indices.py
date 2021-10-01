import discord
import config_discordbot as cfg

from gamestonk_terminal.economy import wsj_model


async def indices_command(ctx, arg):
    # Help
    if arg == "-h" or arg == "help":
        help_txt = "US Indices [Source: Wall St. Journal]\n"
        embed = discord.Embed(
            title="Economy: [WSJ] US Indices HELP",
            description=help_txt,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)

    else:
        df_data = wsj_model.us_indices()
        if df_data.empty:
            df_data_str = "No indices data available"
        else:
            df_data_str = "```" + df_data.to_string(index=False) + "```"

        embed = discord.Embed(
            title="Economy: [WSJ] US Indices", description=df_data_str, colour=cfg.COLOR
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
