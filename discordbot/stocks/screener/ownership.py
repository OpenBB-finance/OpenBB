import difflib
import discord
import pandas as pd

import discordbot.config_discordbot as cfg
from discordbot.helpers import pagination

from gamestonk_terminal.stocks.screener.finviz_model import get_screener_data


async def ownership_command(
    ctx, preset="template", sort="", limit="25", ascend="False"
):
    """Displays stocks based on own share float and ownership data [Finviz]"""
    try:

        # Debug
        if cfg.DEBUG:
            print(f"!stocks.scr.ownership {preset} {sort} {limit} {ascend}")

        # Check for argument
        if not limit.lstrip("-").isnumeric():
            raise Exception("Number has to be an integer")

        limit = int(limit)

        if limit < 0:
            raise Exception("Number has to be above 0")

        if ascend.lower() == "false":
            ascend = False
        elif ascend.lower() == "true":
            ascend = True
        else:
            raise Exception("ascend argument has to be true or false")

        # Output Data
        df_screen = get_screener_data(
            preset,
            "overview",
            limit,
            ascend,
        )

        d_cols_to_sort = {
            "ownership": [
                "Ticker",
                "Market Cap",
                "Outstanding",
                "Float",
                "Insider Own",
                "Insider Trans",
                "Inst Own",
                "Inst Trans",
                "Float Short",
                "Short Ratio",
                "Avg Volume",
                "Price",
                "Change",
                "Volume",
            ],
        }

        description = ""

        if isinstance(df_screen, pd.DataFrame):
            if df_screen.empty:
                return []

            df_screen = df_screen.dropna(axis="columns", how="all")

            if sort:
                if " ".join(sort) in d_cols_to_sort["ownership"]:
                    df_screen = df_screen.sort_values(
                        by=[" ".join(sort)],
                        ascending=ascend,
                        na_position="last",
                    )
                else:
                    similar_cmd = difflib.get_close_matches(
                        " ".join(sort),
                        d_cols_to_sort["ownership"],
                        n=1,
                        cutoff=0.7,
                    )
                    if similar_cmd:
                        description = f"Replacing '{' '.join(sort)}' by '{similar_cmd[0]}' so table can be sorted.\n"
                        df_screen = df_screen.sort_values(
                            by=[similar_cmd[0]],
                            ascending=ascend,
                            na_position="last",
                        )
                    else:
                        raise ValueError(
                            f"Wrong sort column provided! Provide one of these: {', '.join(d_cols_to_sort['ownership'])}"
                        )

            df_screen = df_screen.fillna("")
            df_screen = df_screen.head(n=limit).to_string()

            df_screen_str = description + df_screen

            if len(df_screen_str) <= 4000:
                embed = discord.Embed(
                    title="Stocks: [Finviz] Ownership Screener",
                    description="```" + df_screen_str + "```",
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
                while i <= len(df_screen_str) / 4000:
                    columns.append(
                        discord.Embed(
                            title="Stocks: [Finviz] Ownership Screener",
                            description="```"
                            + df_screen_str[str_start:str_end]
                            + "```",
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
            title="ERROR Stocks: [Finviz] Ownership Screener",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed)
