import discord
import config_discordbot as cfg

from gamestonk_terminal.economy import wsj_model


async def glbonds_command(ctx, arg):
    # Help
    if arg == "-h" or arg == "help":
        help_txt = "Global Bonds [Source: Wall St. Journal]\n"
        embed = discord.Embed(
            title="Economy: [WSJ] Global Bonds HELP",
            description=help_txt,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)

    else:
        df_data = wsj_model.global_bonds()
        if df_data.empty:
            df_data_str = "No global bonds data available"
        else:
            df_data_str = "```" + df_data.to_string(index=False) + "```"

        embed = discord.Embed(
            title="Economy: [WSJ] Global Bonds",
            description=df_data_str,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
