import disnake
from menus.menu import Menu

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from gamestonk_terminal.stocks.government import quiverquant_model


async def lobbying_command(ctx, ticker="", num: int = 10):
    """Displays lobbying details [quiverquant.com]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            logger.debug("!stocks.gov.lobbying %s", ticker)

        if ticker == "":
            raise Exception("A ticker is required")

        # Retrieve Data
        df_lobbying = quiverquant_model.get_government_trading(
            "corporate-lobbying", ticker=ticker
        )

        if df_lobbying.empty:
            logger.debug("No corporate lobbying found")
            return

        # Output Data
        report = ""
        choices = [
            disnake.SelectOption(label="Overview", value="0", emoji="🟢"),
        ]
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
            embed = disnake.Embed(
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
                    disnake.Embed(
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

            await ctx.send(embed=columns[0], view=Menu(columns, choices))

    except Exception as e:
        embed = disnake.Embed(
            title=f"ERROR Stocks: [quiverquant.com] {ticker.upper()} Lobbying Details",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
