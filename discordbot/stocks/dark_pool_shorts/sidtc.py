import discord
import config_discordbot as cfg
from helpers import pagination

from gamestonk_terminal.stocks.dark_pool_shorts import stockgrid_model


async def sidtc_command(ctx, sort="float", num="10"):
    """Short interest and days to cover [Stockgrid]"""

    try:
        # Debug
        if cfg.DEBUG:
            print(f"\n!stocks.dps.sidtc {sort} {num}")

        # Check for argument
        possible_sorts = ("float", "dtc", "si")

        if sort not in possible_sorts:
            raise Exception(f"The possible sorts are: {', '.join(possible_sorts)}")

        if not num.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")

        num = int(num)

        if num < 0:
            raise Exception("Number has to be above 0")

        # Retrieve data
        df = stockgrid_model.get_short_interest_days_to_cover(sort)
        df = df.iloc[:num]

        # Debug user output
        if cfg.DEBUG:
            print(df.to_string())

        # Output data
        dp_date = df["Date"].values[0]
        df = df.drop(columns=["Date"])
        df["Short Interest"] = df["Short Interest"] / 1_000_000
        df.head()
        df.columns = [
            "Ticker",
            "Float Short %",
            "Days to Cover",
            "Short Interest (1M)",
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
                title="Dark Pool Shorts", description=initial_str, colour=cfg.COLOR
            ).set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
        )
        for column in df.columns.values:
            columns.append(
                discord.Embed(
                    title="Stocks: [Stockgrid] Short Interest and Days to Cover",
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
            title="ERROR Stocks: [Stockgrid] Short Interest and Days to Cover",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
