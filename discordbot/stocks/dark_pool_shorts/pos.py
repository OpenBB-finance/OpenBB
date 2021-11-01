import discord
import config_discordbot as cfg
from helpers import pagination

from gamestonk_terminal.stocks.dark_pool_shorts import stockgrid_model


async def pos_command(ctx, sort="dpp_dollar", num="10"):
    """Dark pool short position [Stockgrid]"""

    try:
        # Debug user input
        if cfg.DEBUG:
            print(f"\n!stocks.dps.pos {sort} {num}")

        # Check for argument
        possible_sorts = ("sv", "sv_pct", "nsv", "nsv_dollar", "dpp", "dpp_dollar")

        if sort not in possible_sorts:
            raise Exception(f"The possible sorts are: {', '.join(possible_sorts)}")

        if not num.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")

        num = int(num)

        if num < 0:
            raise Exception("Number has to be above 0")

        # Retrieve data
        df = stockgrid_model.get_dark_pool_short_positions(sort, False)
        df = df.iloc[:num]

        # Debug user output
        if cfg.DEBUG:
            print(df.to_string())

        # Output data
        dp_date = df["Date"].values[0]
        df = df.drop(columns=["Date"])
        df["Net Short Volume $"] = df["Net Short Volume $"] / 100_000_000
        df["Short Volume"] = df["Short Volume"] / 1_000_000
        df["Net Short Volume"] = df["Net Short Volume"] / 1_000_000
        df["Short Volume %"] = df["Short Volume %"] * 100
        df["Dark Pools Position $"] = df["Dark Pools Position $"] / (1_000_000_000)
        df["Dark Pools Position"] = df["Dark Pools Position"] / 1_000_000
        df.columns = [
            "Ticker",
            "Short Vol. (1M)",
            "Short Vol. %",
            "Net Short Vol. (1M)",
            "Net Short Vol. ($100M)",
            "DP Position (1M)",
            "DP Position ($1B)",
        ]
        future_column_name = df["Ticker"]
        df = df.transpose()
        df.columns = future_column_name
        df.drop("Ticker")
        columns = []
        initial_str = "Page 0: Overview"
        i = 1
        for column in df.columns.values:
            initial_str = initial_str + "\nPage " + str(i) + ": " + column
            i += 1
        columns.append(
            discord.Embed(
                title="Stocks: [Stockgrid] Dark Pool Short Position",
                description=initial_str,
                colour=cfg.COLOR,
            ).set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
        )
        for column in df.columns.values:
            columns.append(
                discord.Embed(
                    title="High Short Interest",
                    description="```The following data corresponds to the date: "
                    + dp_date
                    + "\n\n"
                    + df[column].fillna("").to_string()
                    + "```",
                    colour=cfg.COLOR,
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )

        await pagination(columns, ctx)

    except Exception as e:
        embed = discord.Embed(
            title="ERROR Stocks: [Stockgrid] Dark Pool Short Position",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
