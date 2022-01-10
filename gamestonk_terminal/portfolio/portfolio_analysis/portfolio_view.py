"""Portfolio View"""
__docformat__ = "numpy"

import pandas as pd
from tabulate import tabulate
import gamestonk_terminal.feature_flags as gtff


def display_group_holdings(
    portfolio: pd.DataFrame,
    group_column: str,
    allocation: bool,
):
    """Display portfolio holdings based on grouping

    Parameters
    ----------
    portfolio : pd.DataFrame
        Portfolio dataframe
    group_column : str
        Column to group by
    """
    headers = [group_column, "value"]
    grouped_df = pd.DataFrame(portfolio.groupby(group_column).agg(sum)["value"])

    if allocation:
        total_value = grouped_df["value"].sum()
        grouped_df["pct_allocation"] = grouped_df["value"] / total_value * 100
        headers.append("pct_allocation")
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                grouped_df,
                headers=headers,
                tablefmt="fancy_grid",
                floatfmt=".2f",
            ),
            "\n",
        )
    else:
        print(portfolio.to_string(), "\n")
