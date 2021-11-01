import discord
import config_discordbot as cfg

from gamestonk_terminal.economy import wsj_model


async def usbonds_command(ctx):
    """US bonds overview [Wall St. Journal]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            print("\n!economy.usbonds")

        # Retrieve data
        df_data = wsj_model.us_bonds()

        # Debug user output
        if cfg.DEBUG:
            print(df_data.to_string())

        # Output data
        if df_data.empty:
            df_data_str = "No US bonds data available"
        else:
            df_data_str = "```" + df_data.to_string(index=False) + "```"

        embed = discord.Embed(
            title="Economy: [WSJ] US Bonds",
            description=df_data_str,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Economy: [WSJ] US Bonds",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
