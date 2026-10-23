"""Helper functions for technical analysis indicators."""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pandas import DataFrame


def check_columns(
    data: "DataFrame", high: bool = True, low: bool = True, close: bool = True
) -> str | None:
    """Return the close columns, or None if the dataframe does not have required columns.

    Parameters
    ----------
    data: DataFrame
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
    import re

    close_regex = r"(Adj\sClose|adj_close|Close)"
    if (
        (re.findall(r"High", str(data.columns), re.IGNORECASE) is None and high)
        or (re.findall(r"Low", str(data.columns), re.IGNORECASE) is None and low)
        or (close_col := re.findall(close_regex, str(data.columns), re.IGNORECASE))
        is None
        and close
    ):
        raise ValueError(  # pragma: no cover  # re.findall never returns None, so this guard cannot fire
            " Please make sure that the columns 'High', 'Low', and 'Close' are in the dataframe."
        )

    close_col = [col for col in close_col if col in data.columns]

    if "close" in close_col:
        return "close"

    return close_col[-1]
