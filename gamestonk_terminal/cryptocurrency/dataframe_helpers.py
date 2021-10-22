"""Dataframe helpers"""
__docformat__ = "numpy"

from typing import Union, Any
import textwrap
import pandas as pd
from gamestonk_terminal.helper_funcs import long_number_format


def wrap_text_in_df(df: pd.DataFrame, w: int = 55) -> pd.DataFrame:  # pragma: no cover
    """
    Parameters
    ----------
    df: pd.DataFrame
        Data Frame with some data
    w: int
        length of text in column after which text is wrapped into new line

    Returns
    -------
    pd.DataFrame
    """

    return df.applymap(
        lambda x: "\n".join(textwrap.wrap(x, width=w)) if isinstance(x, str) else x
    )


def percent_to_float(s: str) -> float:
    """Helper method to replace string pct like "123.56%" to float 1.2356
    Parameters
    ----------
    s: string
        string to replace
    Returns
    -------
    float
    """

    s = str(float(s.rstrip("%")))
    i = s.find(".")
    if i == -1:
        return int(s) / 100
    if s.startswith("-"):
        return -percent_to_float(s.lstrip("-"))
    s = s.replace(".", "")
    i -= 2
    if i < 0:
        return float("." + "0" * abs(i) + s)
    return float(s[:i] + "." + s[i:])


def create_df_index(df: pd.DataFrame, name: str = "rank") -> None:
    """Helper method that creates new index for given data frame, with provided index name
    Parameters
    ----------
    df:
        pd.DataFrame
    name: str
        index name
    """

    df.index = df.index + 1
    df.reset_index(inplace=True)
    df.rename(columns={"index": name}, inplace=True)


def long_number_format_with_type_check(x: Union[int, float]) -> Union[str, Any]:
    """Helper which checks if type of x is int or float and it's smaller then 10^18.
    If yes it apply long_num_format

    Parameters
    ----------
    x: int/float
        number to apply long_number_format method
    Returns
    -------
    Union[str, Any]
    """

    if isinstance(x, (int, float)) and x < 10 ** 18:
        return long_number_format(x)
    return x


def replace_underscores_in_column_names(string: str) -> str:
    return string.title().replace("_", " ")


def very_long_number_formatter(num: Union[str, int, float]) -> str:
    """Apply nice string format for very big numbers like Trillions, Quadrillions, Billions etc.

    Parameters
    ----------
    num: Union[str, int, float]
        number to format
    Returns
    -------
    str:
        formatted number
    """

    if isinstance(num, str):
        try:
            num = float(num)
        except (TypeError, ValueError):
            return str(num)

    if isinstance(num, (int, float)):
        num = int(num)
        magnitude = 0
        while abs(num) >= 1000 and magnitude <= 3:
            magnitude += 1
            num /= 1000.0
        num = round(num, 1)
        return "{}{}".format(
            f"{num:f}".rstrip("0").rstrip("."),
            ["", "K", "M", "B", "T"][magnitude],
        )
    return num
