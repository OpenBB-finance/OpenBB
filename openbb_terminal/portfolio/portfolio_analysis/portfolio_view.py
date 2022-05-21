"""Portfolio View"""
__docformat__ = "numpy"

import logging

import pandas as pd

from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import print_rich_table

logger = logging.getLogger(__name__)


@log_start_end(log=logger)
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
    print_rich_table(grouped_df, headers=list(headers), title="Portfolio Holdings")
