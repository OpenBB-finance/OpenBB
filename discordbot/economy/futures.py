import discord
import config_discordbot as cfg

from gamestonk_terminal.economy import wsj_model


async def futures_command(ctx, arg=""):
    """Gets the futures data from GST and sends it

    Parameters
    -----------
    arg: str
        -h or help

    Returns
    -------
    discord message
        Sends a message containing an embed of futures data to the user
    """

    try:
        # Debug
        if cfg.DEBUG:
            print(f"!stocks.economy.futures {arg}")

        # Help
        if arg == "-h" or arg == "help":
            help_txt = "Futures/Commodities [Source: Wall St. Journal]\n"
            embed = discord.Embed(
                title="Economy: [WSJ] Futures/Commodities HELP",
                description=help_txt,
                colour=cfg.COLOR,
            )
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )

        else:
            df_data = wsj_model.top_commodities()
            if df_data.empty:
                df_data_str = "No futures/commodities data available"
            else:
                df_data_str = "```" + df_data.to_string(index=False) + "```"

            embed = discord.Embed(
                title="Economy: [WSJ] Futures/Commodities",
                description=df_data_str,
                colour=cfg.COLOR,
            )
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )

        await ctx.send(embed=embed)

    except Exception as e:
        title = "INTERNAL ERROR"
        embed = discord.Embed(title=title, colour=cfg.COLOR)
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )
        embed.set_description(
            "Try updating the bot, make sure DEBUG is True in the config "
            "and restart it.\nIf the error still occurs open a issue at: "
            "https://github.com/GamestonkTerminal/GamestonkTerminal/issues"
            f"\n{e}"
        )
        await ctx.send(embed=embed)
        if cfg.DEBUG:
            print(e)
