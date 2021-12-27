"""Yahoo Finance Mutual Fund Model"""
__docformat__ = "numpy"

import pandas as pd
from rich.console import Console

import gamestonk_terminal.feature_flags as gtff
from gamestonk_terminal.helper_funcs import rich_table_from_df
from gamestonk_terminal.mutual_funds import yfinance_model

console = Console()


def display_sector(fund: str):
    """Display sector weightings for fund

    Parameters
    ----------
    fund: str
        Fund symbol
    """
    sector_weights = yfinance_model.get_information(fund)["sectorWeightings"]
    weights = {}
    for weight in sector_weights:
        weights.update(weight)
    df_weight = pd.DataFrame.from_dict(weights, orient="index")
    df_weight = df_weight.apply(lambda x: round(100 * x, 3))
    if gtff.USE_TABULATE_DF:
        console.print(
            rich_table_from_df(
                df_weight,
                show_index=True,
                index_name="Sector",
                headers=["Weight (%)"],
                title=f"[bold]{fund.upper()} Sector Weightings[/bold] ",
            )
        )
    else:
        console.print(df_weight.to_string())
    console.print("")


def display_equity(fund: str):
    """Display equity holdings for fund

    Parameters
    ----------
    fund: str
        Fund symbol
    """
    equity_hold = yfinance_model.get_information(fund)["equityHoldings"]
    df_weight = pd.DataFrame.from_dict(equity_hold, orient="index")
    df_weight = df_weight.apply(lambda x: round(100 * x, 3))
    if gtff.USE_TABULATE_DF:
        console.print(
            rich_table_from_df(
                df_weight,
                show_index=True,
                index_name="Equity",
                headers=["Holding"],
                title=f"[bold]{fund.upper()} Equity Holdings[/bold] ",
            )
        )
    else:
        console.print(df_weight.to_string())
    console.print("")
