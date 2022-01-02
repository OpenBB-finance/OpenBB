import discord

from gamestonk_terminal.stocks.government import quiverquant_model
import discordbot.config_discordbot as cfg
from discordbot.helpers import pagination


async def lobbying_command(ctx, ticker="", num=""):
    """Displays lobbying details [quiverquant.com]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            print(f"!stocks.gov.lobbying {ticker}")

        if ticker == "":
            raise Exception("A ticker is required")

        if num == "":
            num = 10
        else:
            if not num.lstrip("-").isnumeric():
                raise Exception("Number has to be an integer")
            num = int(num)

        # Retrieve Data
        df_lobbying = quiverquant_model.get_government_trading(
            "corporate-lobbying", ticker=ticker
        )

        if df_lobbying.empty:
            print("No corporate lobbying found\n")
            return

        # Output Data
        report = ""
        for _, row in (
            df_lobbying.sort_values(by=["Date"], ascending=False).head(num).iterrows()
        ):
            amount = (
                "$" + str(int(float(row["Amount"])))
                if row["Amount"] is not None
                else "N/A"
            )
            report += f"{row['Date']}: {row['Client']} {amount}"
            if row["Amount"] is not None:
                report += "\t" + row["Specific_Issue"].replace("\n", " ").replace(
                    "\r", ""
                )
            report += "\n"

        if len(report) <= 4000:
            embed = discord.Embed(
                title=f"Stocks: [quiverquant.com] {ticker.upper()} Lobbying Details",
                description="```" + report + "```",
                colour=cfg.COLOR,
            )
            embed.set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
            await ctx.send(embed=embed)
        else:
            i = 0
            str_start = 0
            str_end = 4000
            columns = []
            while i <= len(report) / 4000:
                columns.append(
                    discord.Embed(
                        title=f"Stocks: [quiverquant.com] {ticker.upper()} Lobbying Details",
                        description="```" + report[str_start:str_end] + "```",
                        colour=cfg.COLOR,
                    ).set_author(
                        name=cfg.AUTHOR_NAME,
                        icon_url=cfg.AUTHOR_ICON_URL,
                    )
                )
                str_end = str_start
                str_start += 4000
                i += 1

            await pagination(columns, ctx)

    except Exception as e:
        embed = discord.Embed(
            title=f"ERROR Stocks: [quiverquant.com] {ticker.upper()} Lobbying Details",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
