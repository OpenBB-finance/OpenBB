import difflib

import disnake
import pandas as pd
from menus.menu import Menu

import discordbot.config_discordbot as cfg
from discordbot.config_discordbot import logger
from discordbot.stocks.screener import screener_options as so
from gamestonk_terminal.stocks.screener.finviz_model import get_screener_data


async def performance_command(
    ctx, preset: str = "template", sort: str = "", limit: int = 5, ascend: bool = False
):
    """Displays stocks and sort by performance categories [Finviz]"""
    try:
        # Check for argument
        if preset == "template" or preset not in so.all_presets:
            raise Exception("Invalid preset selected!")

        # Debug
        if cfg.DEBUG:
            logger.debug(
                "!stocks.scr.performance %s %s %s %s", preset, sort, limit, ascend
            )

        # Check for argument
        if limit < 0:
            raise Exception("Number has to be above 0")

        # Output Data
        df_screen = get_screener_data(
            preset,
            "performance",
            limit,
            ascend,
        )

        d_cols_to_sort = {
            "performance": [
                "Ticker",
                "Perf Week",
                "Perf Month",
                "Perf Quart",
                "Perf Half",
                "Perf Year",
                "Perf YTD",
                "Volatility W",
                "Volatility M",
                "Recom",
                "Avg Volume",
                "Rel Volume",
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
                if " ".join(sort) in d_cols_to_sort["performance"]:
                    df_screen = df_screen.sort_values(
                        by=[" ".join(sort)],
                        ascending=ascend,
                        na_position="last",
                    )
                else:
                    similar_cmd = difflib.get_close_matches(
                        " ".join(sort),
                        d_cols_to_sort["performance"],
                        n=1,
                        cutoff=0.7,
                    )
                    if similar_cmd:
                        description = f"Replacing '{' '.join(sort)}' by '{similar_cmd[0]}' so table can be sorted.\n\n"
                        df_screen = df_screen.sort_values(
                            by=[similar_cmd[0]],
                            ascending=ascend,
                            na_position="last",
                        )
                    else:
                        raise ValueError(
                            "Wrong sort column provided! Provide one of these:"
                            f"{', '.join(d_cols_to_sort['performance'])}"
                        )

            df_screen = df_screen.fillna("")
            future_column_name = df_screen["Ticker"]
            df_screen = df_screen.head(n=limit).transpose()
            df_screen.columns = future_column_name
            df_screen.drop("Ticker")

            columns = []
            choices = [
                disnake.SelectOption(label="Overview", value="0", emoji="🟢"),
            ]
            initial_str = description + "Overview"
            i = 1
            for column in df_screen.columns.values:
                menu = f"\nPage {i}: {column}"
                initial_str += f"\nPage {i}: {column}"
                if i < 19:
                    choices.append(
                        disnake.SelectOption(label=menu, value=f"{i}", emoji="🟢"),
                    )
                if i == 20:
                    choices.append(
                        disnake.SelectOption(
                            label="Max Reached", value=f"{i}", emoji="🟢"
                        ),
                    )
                i += 1
            columns.append(
                disnake.Embed(
                    title="Stocks: [Finviz] Performance Screener",
                    description=initial_str,
                    colour=cfg.COLOR,
                ).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )
            for column in df_screen.columns.values:
                columns.append(
                    disnake.Embed(
                        title="Stocks: [Finviz] Performance Screener",
                        description="```"
                        + df_screen[column].fillna("").to_string()
                        + "```",
                        colour=cfg.COLOR,
                    ).set_author(
                        name=cfg.AUTHOR_NAME,
                        icon_url=cfg.AUTHOR_ICON_URL,
                    )
                )

            await ctx.send(embed=columns[0], view=Menu(columns, choices))

    except Exception as e:
        embed = disnake.Embed(
            title="ERROR Stocks: [Finviz] Performance Screener",
            colour=cfg.COLOR,
            description=e,
        )
        embed.set_author(
            name=cfg.AUTHOR_NAME,
            icon_url=cfg.AUTHOR_ICON_URL,
        )

        await ctx.send(embed=embed, delete_after=30.0)
