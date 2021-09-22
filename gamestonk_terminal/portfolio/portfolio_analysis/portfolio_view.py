"""Portfolio View"""
__docformat__ = "numpy"

import pandas as pd
from tabulate import tabulate
import gamestonk_terminal.feature_flags as gtff


def display_group_holdings(portfolio: pd.DataFrame, group_column: str):
    """Display portfolio holdings based on grouping

    Parameters
    ----------
    portfolio : pd.DataFrame
        Portfolio dataframe
    group_column : str
        Column to group by
    """

    grouped_df = pd.DataFrame(portfolio.groupby(group_column).agg(sum)["value"])
    if gtff.USE_TABULATE_DF:
        print(
            tabulate(
                grouped_df,
                headers=[group_column, "value"],
                tablefmt="fancy_grid",
                floatfmt=".2f",
            ),
            "\n",
        )
    else:
        print(portfolio.to_string(), "\n")
