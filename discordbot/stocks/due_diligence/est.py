import discord
import config_discordbot as cfg
from helpers import pagination

from gamestonk_terminal.stocks.due_diligence import business_insider_model


async def est_command(ctx, ticker=""):
    """Displays earning estimates [Business Insider]"""

    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.dd.est {ticker}")

        # Check for argument
        if ticker == "":
            raise Exception("Stock ticker is required")

        (
            df_year_estimates,
            df_quarter_earnings,
            df_quarter_revenues,
        ) = business_insider_model.get_estimates(ticker)

        if (
            df_quarter_revenues.empty
            and df_year_estimates.empty
            and df_quarter_earnings.empty
        ):
            raise Exception("Enter a valid ticker")

        # Debug user output
        if cfg.DEBUG:
            print(df_year_estimates.to_string())
            print(df_quarter_earnings.to_string())
            print(df_quarter_revenues.to_string())

        # Output data
        cols = []
        initial_text = (
            "´´´Page 0: Overview\nPage 1: Year Estimates\n"
            "Page 2: Quarter Earnings\nPage 3: Quarter Revenues´´´"
        )
        text = "´´´" + df_year_estimates.to_string() + "´´´"
        cols.append(text)
        text = "´´´" + df_quarter_earnings.to_string() + "´´´"
        cols.append(text)
        text = "´´´" + df_quarter_revenues.to_string() + "´´´"
        cols.append(text)
        columns = []
        columns.append(
            discord.Embed(
                title="Stocks: [Business Insider] Earning Estimates",
                description=initial_text,
                colour=cfg.COLOR,
            ).set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
        )
        for text in cols:
            columns.append(
                discord.Embed(description=text, colour=cfg.COLOR,).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )

        await pagination(columns, ctx)
    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: [Business Insider] Earning Estimates",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
