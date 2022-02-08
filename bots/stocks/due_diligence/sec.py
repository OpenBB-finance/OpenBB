import disnake

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from gamestonk_terminal.stocks.due_diligence import marketwatch_model


async def sec_command(ctx, ticker=""):
    """Displays sec filings [Market Watch]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.dd.sec %s", ticker)

        if ticker == "":
            raise Exception("A ticker is required")

        df_financials = marketwatch_model.get_sec_filings(ticker)

        if df_financials.empty:
            raise Exception("Enter a valid ticker")

        # Debug user output
        if cfg.DEBUG:
            logger.debug(df_financials.to_string())

        df = df_financials
        df.loc[:, "Link"] = "[Link Source](" + df.loc[:, "Link"].astype(str)
        df.loc[:, "Link"] = df.loc[:, "Link"] + ")"
        # Output data
        embed = disnake.Embed(
            title="Stocks: [Market Watch] SEC Filings",
            description=df.to_string(),
            colour=cfg.COLOR,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Stocks: [Market Watch] SEC Filings",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
