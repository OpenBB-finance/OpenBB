import logging
from typing import Optional

import pandas as pd

from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


def check_columns(
    data: pd.DataFrame, high: bool = True, low: bool = True, close: bool = True
) -> Optional[str]:
    """Returns the close columns, or None if the dataframe does not have required columns

    Parameters
    ----------
    data: pd.DataFrame
        The dataframe to check
    high: bool
        Whether to check for high column
    low: bool
        Whether to check for low column
    close: bool
        Whether to check for close column

    Returns
    -------
    Optional[str]
        The name of the close column, none if df is invalid

    """
    close_col = "Close"
    for title in ["Adj Close", "Close", "adj_close", "Adj_Close"]:
        if title in data.columns:
            close_col = title
            break

    close_col = "Adj Close" if "Adj Close" in data.columns else "Close"
    # pylint: disable=too-many-boolean-expressions
    if (
        ("High" not in data.columns and high)
        or ("Low" not in data.columns and low)
        or (close_col not in data.columns and close)
    ):
        logger.error("Invalid columns. data has columns %s", data.columns)
        console.print(
            "[red] Please make sure that the columns 'High', 'Low', and 'Close'"
            " are in the dataframe.[/red]"
        )
        return None
    return close_col
