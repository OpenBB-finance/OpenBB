import discord
import config_discordbot as cfg

from gamestonk_terminal.stocks.due_diligence import finviz_model


async def analyst_command(ctx, ticker=""):
    """Displays analyst recommendations [Finviz]"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.dd.analyst {ticker}")

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        df = finviz_model.get_analyst_data(ticker)

        report = "```" + df.to_string() + "```"
        embed = discord.Embed(
            title="Stocks: [Finviz] Analyst Recommendations",
            description=report,
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: [Finviz] Analyst Recommendations",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
