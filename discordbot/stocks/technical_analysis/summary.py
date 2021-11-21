import discord
import config_discordbot as cfg

from gamestonk_terminal.stocks.technical_analysis import finbrain_model


async def summary_command(ctx, ticker=""):
    """Displays text of a given stocks ta summary [FinBrain API]"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.ta.summary {ticker}")

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        report = finbrain_model.get_technical_summary_report(ticker)
        if report:
            report = "```" + report.replace(". ", ".\n") + "```"
        embed = discord.Embed(
            title="Stocks: [FinBrain API] Summary",
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
            title="ERROR Stocks: [FinBrain API] Summary",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
