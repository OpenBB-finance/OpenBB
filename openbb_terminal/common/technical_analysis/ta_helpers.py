from typing import Optional

import pandas as pd

from openbb_terminal.rich_config import console


def check_columns(data: pd.DataFrame) -> Optional[str]:
    """Returns the close columns, or None if the dataframe does not have required columns

    Parameters
    ----------
    data: pd.DataFrame
        The dataframe to check

    Returns
    ----------
    Optional[str]
        The name of the close column, none if df is invalid

    """
    close_col = "Adj Close" if "Adj Close" in data.columns else "Close"
    if (
        "High" not in data.columns
        or "Low" not in data.columns
        or close_col not in data.columns
    ):
        console.print(
            "[red] Please make sure that the columns 'High', 'Low', and 'Close'"
            " are in the dataframe.[/red]"
        )
        return None
    return close_col
