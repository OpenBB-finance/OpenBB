"""Helper functions for technical analysis indicators."""

import re
from typing import Optional

import pandas as pd


def check_columns(
    data: pd.DataFrame, high: bool = True, low: bool = True, close: bool = True
) -> Optional[str]:
    """Return the close columns, or None if the dataframe does not have required columns.

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
    close_regex = r"(Adj\sClose|adj_close|Close)"
    # pylint: disable=too-many-boolean-expressions
    if (
        (re.findall(r"High", str(data.columns), re.IGNORECASE) is None and high)
        or (re.findall(r"Low", str(data.columns), re.IGNORECASE) is None and low)
        or (close_col := re.findall(close_regex, str(data.columns), re.IGNORECASE))
        is None
        and close
    ):
        raise ValueError(
            " Please make sure that the columns 'High', 'Low', and 'Close'"
            " are in the dataframe."
        )

    close_col = [col for col in close_col if col in data.columns]

    # giving priority to the standard close column
    if "close" in close_col:
        return "close"

    return close_col[-1]
