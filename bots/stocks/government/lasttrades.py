import disnake

import bots.config_discordbot as cfg
from bots.config_discordbot import logger
from bots.menus.menu import Menu
from gamestonk_terminal.stocks.government import quiverquant_model


def lasttrades_command(gov_type="", past_days: int = 5, representative=""):
    """Displays trades made by the congress/senate/house [quiverquant.com]"""

    # Debug user input
    if cfg.DEBUG:
        logger.debug(
            "gov-lasttrades %s %s %s",
            gov_type,
            past_days,
            representative,
        )

    possible_args = ["congress", "senate", "house"]
    if gov_type == "":
        gov_type = "congress"
    elif gov_type not in possible_args:
        raise Exception(
            "Enter a valid government argument, options are: congress, senate and house"
        )

    # Retrieve Data
    df_gov = quiverquant_model.get_government_trading(gov_type)

    # Output Data
    if df_gov.empty:
        raise Exception(f"No {gov_type} trading data found")
    df_gov = df_gov.sort_values("TransactionDate", ascending=False)

    df_gov = df_gov[
        df_gov["TransactionDate"].isin(df_gov["TransactionDate"].unique()[:past_days])
    ]

    if gov_type == "congress":
        df_gov = df_gov[
            [
                "TransactionDate",
                "Ticker",
                "Representative",
                "Transaction",
                "Range",
                "House",
                "ReportDate",
            ]
        ].rename(
            columns={
                "TransactionDate": "Transaction Date",
                "ReportDate": "Report Date",
            }
        )
    else:
        df_gov = df_gov[
            [
                "TransactionDate",
                "Ticker",
                "Representative",
                "Transaction",
                "Range",
            ]
        ].rename(columns={"TransactionDate": "Transaction Date"})

    if representative:
        df_gov_rep = df_gov[
            df_gov["Representative"].str.split().str[0] == representative
        ]

        if df_gov_rep.empty:
            raise Exception(
                f"No representative {representative} found in the past {past_days}"
                f" days. The following are available: "
                f"{', '.join(df_gov['Representative'].str.split().str[0].unique())}"
            )
        choices = [
            disnake.SelectOption(label="Overview", value="0", emoji="🟢"),
        ]
        title = f"Stocks: [quiverquant.com] Trades by {representative}"
        initial_str = "Overview"
        i = 1
        for col_name in df_gov_rep["Ticker"].values:
            menu = f"\nPage {i}: {col_name}"
            initial_str += f"\nPage {i}: {col_name}"
            if i < 19:
                choices.append(
                    disnake.SelectOption(label=menu, value=f"{i}", emoji="🟢"),
                )
            if i == 20:
                choices.append(
                    disnake.SelectOption(label="Max Reached", value=f"{i}", emoji="🟢"),
                )
            i += 1

        embeds = []
        df_gov_rep = df_gov_rep.T
        embeds.append(
            disnake.Embed(
                title=title,
                description=initial_str,
                colour=cfg.COLOR,
            ).set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
        )
        reports = [f"{initial_str}"]
        for column in df_gov_rep.columns.values:
            description = "```" + df_gov_rep[column].fillna("").to_string() + "```"
            embeds.append(
                disnake.Embed(description=description, colour=cfg.COLOR,).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )
            reports.append(f"{description}")

        output = {
            "view": Menu,
            "title": title,
            "description": reports,
            "embed": embeds,
            "choices": choices,
        }

    else:
        choices = [
            disnake.SelectOption(label="Overview", value="0", emoji="🟢"),
        ]
        title = f"Stocks: [quiverquant.com] Trades for {gov_type.upper()}"
        initial_str = "Overview"
        i = 1
        for col_name in df_gov["Ticker"].values:
            menu = f"\nPage {i}: {col_name}"
            initial_str += f"\nPage {i}: {col_name}"
            if i < 19:
                choices.append(
                    disnake.SelectOption(label=menu, value=f"{i}", emoji="🟢"),
                )
            if i == 20:
                choices.append(
                    disnake.SelectOption(label="Max Reached", value=f"{i}", emoji="🟢"),
                )
            i += 1

        embeds = []
        df_gov = df_gov.T
        embeds.append(
            disnake.Embed(
                title=title,
                description=initial_str,
                colour=cfg.COLOR,
            ).set_author(
                name=cfg.AUTHOR_NAME,
                icon_url=cfg.AUTHOR_ICON_URL,
            )
        )
        reports = [f"{initial_str}"]
        for column in df_gov.columns.values:
            description = "```" + df_gov[column].fillna("").to_string() + "```"
            embeds.append(
                disnake.Embed(description=description, colour=cfg.COLOR,).set_author(
                    name=cfg.AUTHOR_NAME,
                    icon_url=cfg.AUTHOR_ICON_URL,
                )
            )
            reports.append(f"{description}")

        output = {
            "view": Menu,
            "title": title,
            "description": reports,
            "embed": embeds,
            "choices": choices,
        }

    return output
