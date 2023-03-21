"""Dataframe helpers"""
__docformat__ = "numpy"

import math
import re
import textwrap
from typing import Any, Optional, Union

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.helper_funcs import lambda_long_number_format


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


def lambda_long_number_format_with_type_check(x: Union[int, float]) -> Union[str, Any]:
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

    if get_current_user().preferences.USE_INTERACTIVE_DF:
        return x
    if isinstance(x, (int, float)) and x < 10**18:
        return lambda_long_number_format(x)
    return x


def lambda_replace_underscores_in_column_names(string: str) -> str:
    return string.title().replace("_", " ")


def lambda_very_long_number_formatter(num: Union[str, int, float]) -> str:
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

    if get_current_user().preferences.USE_INTERACTIVE_DF:
        return num  # type:ignore
    if isinstance(num, str):
        try:
            num = float(num)
        except (TypeError, ValueError):
            return str(num)

    if isinstance(num, (int, float)):
        if math.isnan(num):
            num = 0
        num = int(num)
        magnitude = 0
        while abs(num) >= 1000 and magnitude <= 3:
            magnitude += 1
            num /= 1000.0
        num = round(num, 1)
        formatted_num = f"{num:f}".rstrip("0").rstrip(".")

        return f'{formatted_num}{["", "K", "M", "B", "T"][magnitude]}'

    return num


def prettify_paragraph(text):
    # Add tab to the beginning of paragraph
    text = "\t" + text
    pat = "(?<!\n)\n(?!\n)"

    # Add tab to double line break
    pretty_text = re.sub("\n\n", "\n\n\t", text)

    # Replace \n with None
    even_more_pretty_text = re.sub(pat, "", pretty_text)

    return even_more_pretty_text


def prettify_column_names(columns: list) -> list:
    """Helper method that change column names into more human readable format. E.g.
        - tradeAmount => Trade amount,
        - tokenValue => Token value
        - mediumGasPrice => Medium Gas Price

    Parameters
    ----------
    columns: list
        list of column names

    Returns
    -------
    list with reformatted columns
    """
    return [" ".join(re.findall(".[^A-Z]*", val)).capitalize() for val in columns]


def denominate_number(
    number: Any, divider: int = 1000000, round_digits: Optional[int] = 4
) -> float:
    """Denominate numbers base on provided divider and round number by provided digit

    Parameters
    ----------
    number: Any
        value to round
    divider: int
        divide by value
    round_digits:
        round number to n digits
    Returns
    -------
    float:
        denominated number
    """

    if round_digits:
        return round(float(number) / divider, round_digits)
    return round(float(number) / divider)


def lambda_replace_unicode(x: Any) -> Any:
    """Replace unicode characters to ?

    Parameters
    ----------
    x: Any
        value to replace unicode chars

    Returns
    -------
    Any
        replaced value
    """

    if isinstance(x, str):
        return x.encode("ascii", "replace").decode()
    return x
