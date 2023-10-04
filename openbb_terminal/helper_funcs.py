"""Helper functions."""
__docformat__ = "numpy"

# pylint: disable=too-many-lines

# IMPORTS STANDARD LIBRARY
# IMPORTS STANDARD
import argparse
import inspect
import io
import json
import logging
import os
import random
import re
import shutil
import sys
import urllib.parse
import webbrowser
from datetime import (
    date as d,
    datetime,
    timedelta,
)
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

# IMPORTS THIRDPARTY
import iso8601
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas.io.formats.format
import pandas_ta as ta
import pytz
import requests
import yfinance as yf
from holidays import US as us_holidays
from langchain.chat_models import ChatOpenAI
from llama_index import (
    LLMPredictor,
    PromptHelper,
    ServiceContext,
    SimpleDirectoryReader,
    StorageContext,
    VectorStoreIndex,
    load_index_from_storage,
)
from pandas._config.config import get_option
from pandas.plotting import register_matplotlib_converters
from PIL import Image, ImageDraw
from rich.table import Table
from screeninfo import get_monitors

from openbb_terminal import OpenBBFigure, plots_backend
from openbb_terminal.core.config.paths import (
    HOME_DIRECTORY,
    MISCELLANEOUS_DIRECTORY,
)
from openbb_terminal.core.plots.plotly_ta.ta_class import PlotlyTA
from openbb_terminal.core.session.current_system import get_current_system

# IMPORTS INTERNAL
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.decorators import check_api_key
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

register_matplotlib_converters()
if (
    get_current_user().preferences.PLOT_BACKEND is not None
    and get_current_user().preferences.PLOT_BACKEND != "None"
):
    matplotlib.use(get_current_user().preferences.PLOT_BACKEND)

NO_EXPORT = 0
EXPORT_ONLY_RAW_DATA_ALLOWED = 1
EXPORT_ONLY_FIGURES_ALLOWED = 2
EXPORT_BOTH_RAW_DATA_AND_FIGURES = 3

MENU_GO_BACK = 0
MENU_QUIT = 1
MENU_RESET = 2

GPT_INDEX_DIRECTORY = MISCELLANEOUS_DIRECTORY / "gpt_index/"
GPT_INDEX_VER = 0.4


# Command location path to be shown in the figures depending on watermark flag
command_location = ""


# pylint: disable=R1702,R0912


# pylint: disable=global-statement
def set_command_location(cmd_loc: str):
    """Set command location.

    Parameters
    ----------
    cmd_loc: str
        Command location called by user
    """
    if cmd_loc.split("/")[-1] == "hold":
        return
    global command_location  # noqa
    command_location = cmd_loc


def check_path(path: str) -> str:
    """Check that path file exists.

    Parameters
    ----------
    path: str
        path of file

    Returns
    -------
    str:
        Ratio of similarity between two strings
    """
    # Just return empty path because this will be handled outside this function
    if not path:
        return ""
    if path[0] == "~":
        path = path.replace("~", HOME_DIRECTORY.as_posix())
    # Return string of path if such relative path exists
    if os.path.isfile(path):
        return path
    # Return string of path if an absolute path exists
    if os.path.isfile("/" + path):
        return f"/{path}"
    logger.error("The path file '%s' does not exist.", path)
    console.print(f"[red]The path file '{path}' does not exist.\n[/red]")
    return ""


def parse_and_split_input(an_input: str, custom_filters: List) -> List[str]:
    """Filter and split the input queue.

    Uses regex to filters command arguments that have forward slashes so that it doesn't
    break the execution of the command queue.
    Currently handles unix paths and sorting settings for screener menus.

    Parameters
    ----------
    an_input : str
        User input as string
    custom_filters : List
        Additional regular expressions to match

    Returns
    -------
    List[str]
        Command queue as list
    """
    # Make sure that the user can go back to the root when doing "/"
    if an_input and an_input == "/":
        an_input = "home"

    # everything from ` -f ` to the next known extension
    file_flag = r"(\ -f |\ --file )"
    up_to = r".*?"
    known_extensions = r"(\.(xlsx|csv|xls|tsv|json|yaml|ini|openbb|ipynb))"
    unix_path_arg_exp = f"({file_flag}{up_to}{known_extensions})"

    # Add custom expressions to handle edge cases of individual controllers
    custom_filter = ""
    for exp in custom_filters:
        if exp is not None:
            custom_filter += f"|{exp}"
            del exp

    slash_filter_exp = f"({unix_path_arg_exp}){custom_filter}"

    filter_input = True
    placeholders: Dict[str, str] = {}
    while filter_input:
        match = re.search(pattern=slash_filter_exp, string=an_input)
        if match is not None:
            placeholder = f"{{placeholder{len(placeholders)+1}}}"
            placeholders[placeholder] = an_input[
                match.span()[0] : match.span()[1]  # noqa:E203
            ]
            an_input = (
                an_input[: match.span()[0]]
                + placeholder
                + an_input[match.span()[1] :]  # noqa:E203
            )
        else:
            filter_input = False

    commands = an_input.split("/")

    for command_num, command in enumerate(commands):
        if command == commands[command_num] == commands[-1] == "":
            return list(filter(None, commands))
        matching_placeholders = [tag for tag in placeholders if tag in command]
        if len(matching_placeholders) > 0:
            for tag in matching_placeholders:
                commands[command_num] = command.replace(tag, placeholders[tag])
    return commands


def log_and_raise(error: Union[argparse.ArgumentTypeError, ValueError]) -> None:
    """Log and output an error."""
    logger.error(str(error))
    raise error


def similar(a: str, b: str) -> float:
    """Return a similarity float between string a and string b.

    Parameters
    ----------
    a: str
        string a
    b: str
        string b

    Returns
    -------
    float:
        Ratio of similarity between two strings
    """
    return SequenceMatcher(None, a, b).ratio()


def return_colored_value(value: str):
    """Return the string value with green, yellow, red or white color based on
    whether the number is positive, negative, zero or other, respectively.

    Parameters
    ----------
    value: str
        string to be checked

    Returns
    -------
    value: str
        string with color based on value of number if it exists
    """
    values = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", value)

    # Finds exactly 1 number in the string
    if len(values) == 1:
        if float(values[0]) > 0:
            return f"[green]{value}[/green]"

        if float(values[0]) < 0:
            return f"[red]{value}[/red]"

        if float(values[0]) == 0:
            return f"[yellow]{value}[/yellow]"

    return f"{value}"


# pylint: disable=too-many-arguments
def print_rich_table(  # noqa: PLR0912
    df: pd.DataFrame,
    show_index: bool = False,
    title: str = "",
    index_name: str = "",
    headers: Optional[Union[List[str], pd.Index]] = None,
    floatfmt: Union[str, List[str]] = ".2f",
    show_header: bool = True,
    automatic_coloring: bool = False,
    columns_to_auto_color: Optional[List[str]] = None,
    rows_to_auto_color: Optional[List[str]] = None,
    export: bool = False,
    print_to_console: bool = False,
    limit: Optional[int] = 1000,
    source: Optional[str] = None,
    columns_keep_types: Optional[List[str]] = None,
):
    """Prepare a table from df in rich.

    Parameters
    ----------
    df: pd.DataFrame
        Dataframe to turn into table
    show_index: bool
        Whether to include index
    title: str
        Title for table
    index_name : str
        Title for index column
    headers: List[str]
        Titles for columns
    floatfmt: Union[str, List[str]]
        Float number formatting specs as string or list of strings. Defaults to ".2f"
    show_header: bool
        Whether to show the header row.
    automatic_coloring: bool
        Automatically color a table based on positive and negative values
    columns_to_auto_color: List[str]
        Columns to automatically color
    rows_to_auto_color: List[str]
        Rows to automatically color
    export: bool
        Whether we are exporting the table to a file. If so, we don't want to print it.
    limit: Optional[int]
        Limit the number of rows to show.
    print_to_console: bool
        Whether to print the table to the console. If False and interactive mode is
        enabled, the table will be displayed in a new window. Otherwise, it will print to the
        console.
    source: Optional[str]
        Source of the table. If provided, it will be displayed in the header of the table.
    columns_keep_types: Optional[List[str]]
        Columns to keep their types, i.e. not convert to numeric
    """
    if export:
        return

    current_user = get_current_user()
    enable_interactive = (
        current_user.preferences.USE_INTERACTIVE_DF and plots_backend().isatty
    )

    # Make a copy of the dataframe to avoid SettingWithCopyWarning
    df = df.copy()

    show_index = not isinstance(df.index, pd.RangeIndex) and show_index
    #  convert non-str that are not timestamp or int into str
    # eg) praw.models.reddit.subreddit.Subreddit
    for col in df.columns:
        if columns_keep_types is not None and col in columns_keep_types:
            continue
        try:
            if not any(
                isinstance(df[col].iloc[x], pd.Timestamp)
                for x in range(min(10, len(df)))
            ):
                df[col] = pd.to_numeric(df[col], errors="ignore")
        except (ValueError, TypeError):
            df[col] = df[col].astype(str)

    def _get_headers(_headers: Union[List[str], pd.Index]) -> List[str]:
        """Check if headers are valid and return them."""
        output = _headers
        if isinstance(_headers, pd.Index):
            output = list(_headers)
        if len(output) != len(df.columns):
            log_and_raise(
                ValueError("Length of headers does not match length of DataFrame")
            )
        return output

    if enable_interactive and not print_to_console:
        df_outgoing = df.copy()
        # If headers are provided, use them
        if headers is not None:
            # We check if headers are valid
            df_outgoing.columns = _get_headers(headers)

        if show_index and index_name not in df_outgoing.columns:
            # If index name is provided, we use it
            df_outgoing.index.name = index_name or "Index"
            df_outgoing = df_outgoing.reset_index()

        for col in df_outgoing.columns:
            if col == "":
                df_outgoing = df_outgoing.rename(columns={col: "  "})

        plots_backend().send_table(
            df_table=df_outgoing,
            title=title,
            source=source,  # type: ignore
            theme=current_user.preferences.TABLE_STYLE,
        )
        return

    df = df.copy() if not limit else df.copy().iloc[:limit]
    if automatic_coloring:
        if columns_to_auto_color:
            for col in columns_to_auto_color:
                # checks whether column exists
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: return_colored_value(str(x)))
        if rows_to_auto_color:
            for row in rows_to_auto_color:
                # checks whether row exists
                if row in df.index:
                    df.loc[row] = df.loc[row].apply(
                        lambda x: return_colored_value(str(x))
                    )

        if columns_to_auto_color is None and rows_to_auto_color is None:
            df = df.applymap(lambda x: return_colored_value(str(x)))

    if current_user.preferences.USE_TABULATE_DF:
        table = Table(title=title, show_lines=True, show_header=show_header)

        if show_index:
            table.add_column(index_name)

        if headers is not None:
            headers = _get_headers(headers)
            for header in headers:
                table.add_column(str(header))
        else:
            for column in df.columns:
                table.add_column(str(column))

        if isinstance(floatfmt, list) and len(floatfmt) != len(df.columns):
            log_and_raise(
                ValueError(
                    "Length of floatfmt list does not match length of DataFrame columns."
                )
            )
        if isinstance(floatfmt, str):
            floatfmt = [floatfmt for _ in range(len(df.columns))]

        for idx, values in zip(df.index.tolist(), df.values.tolist()):
            # remove hour/min/sec from timestamp index - Format: YYYY-MM-DD # make better
            row_idx = [str(idx)] if show_index else []
            row_idx += [
                str(x)
                if not isinstance(x, float) and not isinstance(x, np.float64)
                else (
                    f"{x:{floatfmt[idx]}}"
                    if isinstance(floatfmt, list)
                    else (
                        f"{x:.2e}" if 0 < abs(float(x)) <= 0.0001 else f"{x:floatfmt}"
                    )
                )
                for idx, x in enumerate(values)
            ]
            table.add_row(*row_idx)
        console.print(table)
    else:
        console.print(df.to_string(col_space=0))


def check_int_range(mini: int, maxi: int):
    """Check if argparse argument is an int between 2 values.

    Parameters
    ----------
    mini: int
        Min value to compare
    maxi: int
        Max value to compare

    Returns
    -------
    int_range_checker:
        Function that compares the three integers
    """

    # Define the function with default arguments
    def int_range_checker(num: int) -> int:
        """Check if int is between a high and low value.

        Parameters
        ----------
        num: int
            Input integer

        Returns
        ----------
        num: int
            Input number if conditions are met

        Raises
        ------
        argparse.ArgumentTypeError
            Input number not between min and max values
        """
        num = int(num)
        if num < mini or num > maxi:
            log_and_raise(
                argparse.ArgumentTypeError(f"Argument must be in range [{mini},{maxi}]")
            )
        return num

    # Return function handle to checking function
    return int_range_checker


def check_non_negative(value) -> int:
    """Argparse type to check non negative int."""
    new_value = int(value)
    if new_value < 0:
        log_and_raise(argparse.ArgumentTypeError(f"{value} is negative"))
    return new_value


def check_terra_address_format(address: str) -> str:
    """Validate that terra account address has proper format.

    Example: ^terra1[a-z0-9]{38}$

    Parameters
    ----------
    address: str
        terra blockchain account address
    Returns
    -------
    str
        Terra blockchain address or raise argparse exception
    """
    pattern = re.compile(r"^terra1[a-z0-9]{38}$")
    if not pattern.match(address):
        log_and_raise(
            argparse.ArgumentTypeError(
                f"Terra address: {address} has invalid format. Valid format: ^terra1[a-z0-9]{{38}}$"
            )
        )
    return address


def check_non_negative_float(value) -> float:
    """Argparse type to check non negative int."""
    new_value = float(value)
    if new_value < 0:
        log_and_raise(argparse.ArgumentTypeError(f"{value} is negative"))
    return new_value


def check_positive_list(value) -> List[int]:
    """Argparse type to return list of positive ints."""
    list_of_nums = value.split(",")
    list_of_pos = []
    for a_value in list_of_nums:
        new_value = int(a_value)
        if new_value <= 0:
            log_and_raise(
                argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
            )
        list_of_pos.append(new_value)
    return list_of_pos


def check_positive_float_list(value) -> List[float]:
    """Argparse type to return list of positive floats."""
    list_of_nums = value.split(",")
    list_of_pos = []
    for a_value in list_of_nums:
        new_value = float(a_value)
        if new_value <= 0:
            log_and_raise(
                argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
            )
        list_of_pos.append(new_value)
    return list_of_pos


def check_positive(value) -> int:
    """Argparse type to check positive int."""
    new_value = int(value)
    if new_value <= 0:
        log_and_raise(
            argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
        )
    return new_value


def check_indicators(string: str) -> List[str]:
    """Check if indicators are valid."""
    ta_cls = PlotlyTA()
    choices = sorted(
        [c.name.replace("plot_", "") for c in ta_cls if c.name != "plot_ma"]
        + ta_cls.ma_mode
    )
    choices_print = (
        f"{'`, `'.join(choices[:10])}`\n    `{'`, `'.join(choices[10:20])}"
        f"`\n    `{'`, `'.join(choices[20:])}"
    )

    strings = string.split(",")
    for s in strings:
        if s not in choices:
            raise argparse.ArgumentTypeError(
                f"\nInvalid choice: {s}, choose from \n    `{choices_print}`",
            )
    return strings


def check_indicator_parameters(args: str, _help: bool = False) -> str:
    """Check if indicators parameters are valid."""
    ta_cls = PlotlyTA()
    indicators_dict: dict = {}

    regex = re.compile(r"([a-zA-Z]+)\[([0-9.,]*)\]")
    no_params_regex = re.compile(r"([a-zA-Z]+)")

    matches = regex.findall(args)
    no_params_matches = no_params_regex.findall(args)

    indicators = [m[0] for m in matches]
    for match in no_params_matches:
        if match not in indicators:
            matches.append((match, ""))

    if _help:
        console.print(
            """[yellow]To pass custom parameters to indicators:[/]

    [green]Example:
        -i macd[12,26,9],rsi[14],sma[20,50]
        -i macd,rsi,sma (uses default parameters)

    [yellow]Would pass the following to the indicators:[/]
        [green]macd=dict(fast=12, slow=26, signal=9)
        rsi=dict(length=14)
        sma=dict(length=[20,50])

        They must be in the same order as the function parameters.[/]\n"""
        )

    pop_keys = ["close", "high", "low", "open", "open_", "volume", "talib", "return"]
    if matches:
        check_indicators(",".join([m[0] for m in matches]))
        for match in matches:
            indicator, args = match

            indicators_dict.setdefault(indicator, {})
            if indicator in ["fib", "srlines", "demark", "clenow"]:
                if _help:
                    console.print(
                        f"[yellow]{indicator}:[/]\n{'':^4}[green]Parameters: None[/]"
                    )
                continue

            fullspec = inspect.getfullargspec(getattr(ta, indicator))
            kwargs = list(set(fullspec.args) - set(pop_keys))
            kwargs.sort(key=fullspec.args.index)

            if _help:
                console.print(
                    f"[yellow]{indicator}:[/]\n{'':^4}[green]Parameters: {', '.join(kwargs)}[/]"
                )

            if indicator in ta_cls.ma_mode:
                indicators_dict[indicator]["length"] = check_positive_list(args)
                continue

            for i, arg in enumerate(args.split(",")):
                if arg and len(kwargs) > i:
                    indicators_dict[indicator][kwargs[i]] = (
                        float(arg) if "." in arg else int(arg)
                    )
        return json.dumps(indicators_dict)

    if not matches:
        raise argparse.ArgumentTypeError(
            f"Invalid indicator arguments: {args}. \n Example: -i macd[12,26,9],rsi[14]"
        )
    return args


def check_positive_float(value) -> float:
    """Argparse type to check positive float."""
    new_value = float(value)
    if new_value <= 0:
        log_and_raise(
            argparse.ArgumentTypeError(f"{value} is not a positive float value")
        )
    return new_value


def check_percentage_range(num) -> float:
    """Check if float is between 0 and 100. If so, return it.

    Parameters
    ----------
    num: float
        Input float

    Returns
    -------
    num: float
        Input number if conditions are met

    Raises
    ------
    argparse.ArgumentTypeError
        Input number not between min and max values
    """
    num = float(num)
    maxi = 100.0
    mini = 0.0
    if num <= mini or num >= maxi:
        log_and_raise(argparse.ArgumentTypeError("Value must be between 0 and 100"))
    return num


def check_proportion_range(num) -> float:
    """Check if float is between 0 and 1. If so, return it.

    Parameters
    ----------
    num: float
        Input float
    Returns
    -------
    num: float
        Input number if conditions are met
    Raises
    ----------
    argparse.ArgumentTypeError
        Input number not between min and max values
    """
    num = float(num)
    maxi = 1.0
    mini = 0.0
    if num < mini or num > maxi:
        log_and_raise(argparse.ArgumentTypeError("Value must be between 0 and 1"))
    return num


def valid_date_in_past(s: str) -> datetime:
    """Argparse type to check date is in valid format."""
    try:
        delta = datetime.now() - datetime.strptime(s, "%Y-%m-%d")
        if delta.days < 1:
            log_and_raise(
                argparse.ArgumentTypeError(
                    f"Not a valid date: {s}. Must be earlier than today"
                )
            )
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError as value_error:
        logging.exception(str(value_error))
        raise argparse.ArgumentTypeError(f"Not a valid date: {s}") from value_error


def check_list_dates(str_dates: str) -> List[datetime]:
    """Argparse type to check list of dates provided have a valid format.

    Parameters
    ----------
    str_dates: str
        string with dates separated by ","

    Returns
    -------
    list_dates: List[datetime]
        List of valid dates
    """
    list_dates = list()
    if str_dates:
        if "," in str_dates:
            for dt_marker in str_dates.split(","):
                list_dates.append(valid_date(dt_marker))
        else:
            list_dates.append(valid_date(str_dates))

    return list_dates


def valid_date(s: str) -> datetime:
    """Argparse type to check date is in valid format."""
    try:
        return datetime.strptime(s, "%Y-%m-%d")
    except ValueError as value_error:
        logging.exception(str(value_error))
        raise argparse.ArgumentTypeError(f"Not a valid date: {s}") from value_error


def is_valid_date(s: str) -> bool:
    """Check if date is in valid format."""
    try:
        datetime.strptime(s, "%Y-%m-%d")
        return True
    except ValueError:
        return False


def valid_repo(repo: str) -> str:
    """Argparse type to check github repo is in valid format."""
    result = re.search(r"^[a-zA-Z0-9-_.]+\/[a-zA-Z0-9-_.]+$", repo)  # noqa: W605
    if not result:
        log_and_raise(
            argparse.ArgumentTypeError(
                f"{repo} is not a valid repo. Valid repo: org/repo"
            )
        )
    return repo


def valid_hour(hr: str) -> int:
    """Argparse type to check hour is valid with 24-hour notation."""
    new_hr = int(hr)

    if (new_hr < 0) or (new_hr > 24):
        log_and_raise(
            argparse.ArgumentTypeError(f"{hr} doesn't follow 24-hour notion.")
        )
    return new_hr


def lower_str(string: str) -> str:
    """Convert string to lowercase."""
    return string.lower()


def us_market_holidays(years) -> list:
    """Get US market holidays."""
    if isinstance(years, int):
        years = [
            years,
        ]
    # https://www.nyse.com/markets/hours-calendars
    market_holidays = [
        "Martin Luther King Jr. Day",
        "Washington's Birthday",
        "Memorial Day",
        "Independence Day",
        "Labor Day",
        "Thanksgiving",
        "Christmas Day",
    ]
    #   http://www.maa.clell.de/StarDate/publ_holidays.html
    good_fridays = {
        2010: "2010-04-02",
        2011: "2011-04-22",
        2012: "2012-04-06",
        2013: "2013-03-29",
        2014: "2014-04-18",
        2015: "2015-04-03",
        2016: "2016-03-25",
        2017: "2017-04-14",
        2018: "2018-03-30",
        2019: "2019-04-19",
        2020: "2020-04-10",
        2021: "2021-04-02",
        2022: "2022-04-15",
        2023: "2023-04-07",
        2024: "2024-03-29",
        2025: "2025-04-18",
        2026: "2026-04-03",
        2027: "2027-03-26",
        2028: "2028-04-14",
        2029: "2029-03-30",
        2030: "2030-04-19",
    }
    market_and_observed_holidays = market_holidays + [
        holiday + " (Observed)" for holiday in market_holidays
    ]
    all_holidays = us_holidays(years=years)
    valid_holidays = [
        date
        for date in list(all_holidays)
        if all_holidays[date] in market_and_observed_holidays
    ]

    for year in years:
        new_Year = datetime.strptime(f"{year}-01-01", "%Y-%m-%d")
        if new_Year.weekday() != 5:  # ignore saturday
            valid_holidays.append(new_Year.date())
        if new_Year.weekday() == 6:  # add monday for Sunday
            valid_holidays.append(new_Year.date() + timedelta(1))
    for year in years:
        valid_holidays.append(datetime.strptime(good_fridays[year], "%Y-%m-%d").date())
    return valid_holidays


def lambda_long_number_format(num, round_decimal=3) -> Union[str, int, float]:
    """Format a long number."""
    if get_current_user().preferences.USE_INTERACTIVE_DF:
        return num

    if num == float("inf"):
        return "inf"

    if isinstance(num, float):
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0

        string_fmt = f".{round_decimal}f"

        num_str = int(num) if num.is_integer() else f"{num:{string_fmt}}"

        return f"{num_str} {' KMBTP'[magnitude]}".strip()
    if isinstance(num, int):
        num = str(num)
    if (
        isinstance(num, str)
        and num.lstrip("-").isdigit()
        and not num.lstrip("-").startswith("0")
        and not is_valid_date(num)
    ):
        num = int(num)
        num /= 1.0
        magnitude = 0
        while abs(num) >= 1000:
            magnitude += 1
            num /= 1000.0

        string_fmt = f".{round_decimal}f"
        num_str = int(num) if num.is_integer() else f"{num:{string_fmt}}"

        return f"{num_str} {' KMBTP'[magnitude]}".strip()
    return num


def revert_lambda_long_number_format(num_str: str) -> Union[float, str]:
    """
    Revert the formatting of a long number if the input is a formatted number, otherwise return the input as is.

    Parameters
    ----------
    num_str : str
        The number to remove the formatting.

    Returns
    -------
    Union[float, str]
        The number as float (with no formatting) or the input as is.

    """
    magnitude_dict = {
        "K": 1000,
        "M": 1000000,
        "B": 1000000000,
        "T": 1000000000000,
        "P": 1000000000000000,
    }

    # Ensure the input is a string and not empty
    if not num_str or not isinstance(num_str, str):
        return num_str

    num_as_list = num_str.strip().split()

    # If the input string is a number parse it as float
    if (
        len(num_as_list) == 1
        and num_as_list[0].replace(".", "").replace("-", "").isdigit()
        and not is_valid_date(num_str)
    ):
        return float(num_str)

    # If the input string is a formatted number with magnitude
    if (
        len(num_as_list) == 2
        and num_as_list[1] in magnitude_dict
        and num_as_list[0].replace(".", "").replace("-", "").isdigit()
    ):
        num, unit = num_as_list
        magnitude = magnitude_dict.get(unit)
        if magnitude:
            return float(num) * magnitude

    # Return the input string as is if it's not a formatted number
    return num_str


def lambda_long_number_format_y_axis(df, y_column, ax):
    """Format long number that goes onto Y axis."""
    max_values = df[y_column].values.max()

    magnitude = 0
    while abs(max_values) >= 1000:
        magnitude += 1
        max_values /= 1000.0

    magnitude_sym = " KMBTP"[magnitude]

    # Second y label axis -
    if magnitude_sym == " ":
        ax[2].set_ylabel(f"{y_column}")
    else:
        ax[2].set_ylabel(f"{y_column} [{magnitude_sym}]")

    divider_map = {" ": 1, "K": 1000, "M": 1000000, "B": 1000000000}
    divider = divider_map[magnitude_sym]

    ax[2].get_yaxis().set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda x, _: int(x / divider))
    )


def lambda_clean_data_values_to_float(val: str) -> float:
    """Clean data to float based on string ending."""
    # Remove any leading or trailing parentheses and spaces
    val = val.strip("( )")
    if val == "-":
        val = "0"

    # Convert percentage to decimal
    if val.endswith("%"):
        return float(val[:-1]) / 100.0
    if val.endswith("B"):
        return float(val[:-1]) * 1_000_000_000
    if val.endswith("M"):
        return float(val[:-1]) * 1_000_000
    if val.endswith("K"):
        return float(val[:-1]) * 1000
    return float(val)


def lambda_int_or_round_float(x) -> str:
    """Format int or round float."""
    # If the data is inf, -inf, or NaN then simply return '~' because it is either too
    # large, too small, or we do not have data to display for it
    if x in (np.inf, -np.inf, np.nan):
        return " " + "~"
    if (x - int(x) < -sys.float_info.epsilon) or (x - int(x) > sys.float_info.epsilon):
        return " " + str(round(x, 2))

    return " " + str(int(x))


def divide_chunks(data, n):
    """Split into chunks."""
    # looping till length of data
    for i in range(0, len(data), n):
        yield data[i : i + n]  # noqa: E203


def get_next_stock_market_days(last_stock_day, n_next_days) -> list:
    """Get the next stock market day.

    Checks against weekends and holidays.
    """
    n_days = 0
    l_pred_days = []
    years: list = []
    holidays: list = []
    if isinstance(last_stock_day, datetime):
        while n_days < n_next_days:
            last_stock_day += timedelta(hours=24)
            year = last_stock_day.date().year
            if year not in years:
                years.append(year)
                holidays += us_market_holidays(year)
            # Check if it is a weekend
            if last_stock_day.date().weekday() > 4:
                continue
            # Check if it is a holiday
            if last_stock_day.strftime("%Y-%m-%d") in holidays:
                continue
            # Otherwise stock market is open
            n_days += 1
            l_pred_days.append(last_stock_day)
    else:
        while n_days < n_next_days:
            l_pred_days.append(last_stock_day + 1 + n_days)
            n_days += 1

    return l_pred_days


def is_intraday(df: pd.DataFrame) -> bool:
    """Check if the data granularity is intraday.

    Parameters
    ----------
    df : pd.DataFrame
        Price data

    Returns
    -------
    bool
        True if data is intraday
    """
    granularity = df.index[1] - df.index[0]
    intraday = not granularity >= timedelta(days=1)
    return intraday


def reindex_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Reindex dataframe to exclude non-trading days.

    Resets the index of a df to an integer and prepares the 'date' column to become
    x tick labels on a plot.

    Parameters
    ----------
    df : pd.DataFrame
        Source dataframe

    Returns
    -------
    pd.DataFrame
        Reindexed dataframe
    """
    date_format = "%b %d %H:%M" if is_intraday(df) else "%Y-%m-%d"
    reindexed_df = df.reset_index()
    reindexed_df["date"] = reindexed_df["date"].dt.strftime(date_format)
    return reindexed_df


def get_data(tweet):
    """Get twitter data from API request."""
    if "+" in tweet["created_at"]:
        s_datetime = tweet["created_at"].split(" +")[0]
    else:
        s_datetime = iso8601.parse_date(tweet["created_at"]).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

    s_text = tweet["full_text"] if "full_text" in tweet else tweet["text"]
    return {"created_at": s_datetime, "text": s_text}


def clean_tweet(tweet: str, symbol: str) -> str:
    """Clean tweets to be fed to sentiment model."""
    whitespace = re.compile(r"\s+")
    web_address = re.compile(r"(?i)http(s):\/\/[a-z0-9.~_\-\/]+")
    ticker = re.compile(rf"(?i)@{symbol}(?=\b)")
    user = re.compile(r"(?i)@[a-z0-9_]+")

    tweet = whitespace.sub(" ", tweet)
    tweet = web_address.sub("", tweet)
    tweet = ticker.sub(symbol, tweet)
    tweet = user.sub("", tweet)

    return tweet


def get_user_agent() -> str:
    """Get a not very random user agent."""
    user_agent_strings = [
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:82.1) Gecko/20100101 Firefox/82.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:84.0) Gecko/20100101 Firefox/84.0",
    ]

    return random.choice(user_agent_strings)  # nosec # noqa: S311


def text_adjustment_init(self):
    """Adjust text monkey patch for Pandas."""
    self.ansi_regx = re.compile(r"\x1B[@-_][0-?]*[ -/]*[@-~]")
    self.encoding = get_option("display.encoding")


def text_adjustment_len(self, text):
    """Get the length of the text adjustment."""
    # return compat.strlen(self.ansi_regx.sub("", text), encoding=self.encoding)
    return len(self.ansi_regx.sub("", text))


def text_adjustment_justify(self, texts, max_len, mode="right"):
    """Apply 'Justify' text alignment."""
    justify = (
        str.ljust
        if (mode == "left")
        else str.rjust
        if (mode == "right")
        else str.center
    )
    out = []
    for s in texts:
        escapes = self.ansi_regx.findall(s)
        if len(escapes) == 2:
            out.append(
                escapes[0].strip()
                + justify(self.ansi_regx.sub("", s), max_len)
                + escapes[1].strip()
            )
        else:
            out.append(justify(s, max_len))
    return out


# pylint: disable=unused-argument
def text_adjustment_join_unicode(self, lines, sep=""):
    """Join Unicode."""
    try:
        return sep.join(lines)
    except UnicodeDecodeError:
        # sep = compat.text_type(sep)
        return sep.join([x.decode("utf-8") if isinstance(x, str) else x for x in lines])


# pylint: disable=unused-argument
def text_adjustment_adjoin(self, space, *lists, **kwargs):
    """Join text."""
    # Add space for all but the last column:
    pads = ([space] * (len(lists) - 1)) + [0]
    max_col_len = max(len(col) for col in lists)
    new_cols = []
    for col, pad in zip(lists, pads):
        width = max(self.len(s) for s in col) + pad
        c = self.justify(col, width, mode="left")
        # Add blank cells to end of col if needed for different col lens:
        if len(col) < max_col_len:
            c.extend([" " * width] * (max_col_len - len(col)))
        new_cols.append(c)

    rows = [self.join_unicode(row_tup) for row_tup in zip(*new_cols)]
    return self.join_unicode(rows, sep="\n")


# https://github.com/pandas-dev/pandas/issues/18066#issuecomment-522192922
def patch_pandas_text_adjustment():
    """Set pandas text adjustment settings."""
    pandas.io.formats.format.TextAdjustment.__init__ = text_adjustment_init
    pandas.io.formats.format.TextAdjustment.len = text_adjustment_len
    pandas.io.formats.format.TextAdjustment.justify = text_adjustment_justify
    pandas.io.formats.format.TextAdjustment.join_unicode = text_adjustment_join_unicode
    pandas.io.formats.format.TextAdjustment.adjoin = text_adjustment_adjoin


def lambda_financials_colored_values(val: str) -> str:
    """Add a color to a value."""

    # We don't want to do the color stuff in interactive mode
    if get_current_user().preferences.USE_INTERACTIVE_DF:
        return val

    if val == "N/A" or str(val) == "nan":
        val = "[yellow]N/A[/yellow]"
    elif sum(c.isalpha() for c in val) < 2:
        if "%" in val and "-" in val or "%" not in val and "(" in val:
            val = f"[red]{val}[/red]"
        elif "%" in val:
            val = f"[green]{val}[/green]"
    return val


def check_ohlc(type_ohlc: str) -> str:
    """Check that data is in ohlc."""
    if bool(re.match("^[ohlca]+$", type_ohlc)):
        return type_ohlc
    raise argparse.ArgumentTypeError("The type specified is not recognized")


def lett_to_num(word: str) -> str:
    """Match ohlca to integers."""
    replacements = [("o", "1"), ("h", "2"), ("l", "3"), ("c", "4"), ("a", "5")]
    for a, b in replacements:
        word = word.replace(a, b)
    return word


AVAILABLE_FLAIRS = {
    ":openbb": "(🦋)",
    ":bug": "(🐛)",
    ":rocket": "(🚀)",
    ":diamond": "(💎)",
    ":stars": "(✨)",
    ":baseball": "(⚾)",
    ":boat": "(⛵)",
    ":phone": "(☎)",
    ":mercury": "(☿)",
    ":hidden": "",
    ":sun": "(☼)",
    ":moon": "(☾)",
    ":nuke": "(☢)",
    ":hazard": "(☣)",
    ":tunder": "(☈)",
    ":king": "(♔)",
    ":queen": "(♕)",
    ":knight": "(♘)",
    ":recycle": "(♻)",
    ":scales": "(⚖)",
    ":ball": "(⚽)",
    ":golf": "(⛳)",
    ":piece": "(☮)",
    ":yy": "(☯)",
}


def get_flair() -> str:
    """Get a flair icon."""

    current_user = get_current_user()  # pylint: disable=redefined-outer-name
    current_flair = str(current_user.preferences.FLAIR)
    flair = AVAILABLE_FLAIRS.get(current_flair, current_flair)

    if (
        current_user.preferences.USE_DATETIME
        and get_user_timezone_or_invalid() != "INVALID"
    ):
        dtime = datetime.now(pytz.timezone(get_user_timezone())).strftime(
            "%Y %b %d, %H:%M"
        )

        # if there is no flair, don't add an extra space after the time
        if flair == "":
            return f"{dtime}"

        return f"{dtime} {flair}"

    return flair


def is_timezone_valid(user_tz: str) -> bool:
    """Check whether user timezone is valid.

    Parameters
    ----------
    user_tz: str
        Timezone to check for validity

    Returns
    -------
    bool
        True if timezone provided is valid
    """
    return user_tz in pytz.all_timezones


def get_user_timezone() -> str:
    """Get user timezone if it is a valid one.

    Returns
    -------
    str
        user timezone based on .env file
    """
    return get_current_user().preferences.TIMEZONE


def get_user_timezone_or_invalid() -> str:
    """Get user timezone if it is a valid one.

    Returns
    -------
    str
        user timezone based on timezone.openbb file or INVALID
    """
    user_tz = get_user_timezone()
    if is_timezone_valid(user_tz):
        return f"{user_tz}"
    return "INVALID"


def str_to_bool(value) -> bool:
    """Match a string to a boolean value."""
    if isinstance(value, bool):
        return value
    if value.lower() in {"false", "f", "0", "no", "n"}:
        return False
    if value.lower() in {"true", "t", "1", "yes", "y"}:
        return True
    raise ValueError(f"{value} is not a valid boolean value")


def get_screeninfo():
    """Get screeninfo."""
    try:
        screens = get_monitors()  # Get all available monitors
    except Exception:
        return None

    if screens:
        current_user = get_current_user()
        if (
            len(screens) - 1 < current_user.preferences.MONITOR
        ):  # Check to see if chosen monitor is detected
            monitor = 0
            console.print(
                f"Could not locate monitor {current_user.preferences.MONITOR}, using primary monitor."
            )
        else:
            monitor = current_user.preferences.MONITOR
        main_screen = screens[monitor]  # Choose what monitor to get

        return (main_screen.width, main_screen.height)

    return None


def plot_autoscale():
    """Autoscale plot."""
    current_user = get_current_user()
    screen_info = get_screeninfo()
    if current_user.preferences.USE_PLOT_AUTOSCALING and screen_info:
        x, y = screen_info  # Get screen size
        # account for ultrawide monitors
        if x / y > 1.5:
            x = x * 0.4

        x = ((x) * current_user.preferences.PLOT_WIDTH_PERCENTAGE * 10**-2) / (
            current_user.preferences.PLOT_DPI
        )  # Calculate width
        if current_user.preferences.PLOT_HEIGHT_PERCENTAGE == 100:  # If full height
            y = y - 60  # Remove the height of window toolbar
        y = ((y) * current_user.preferences.PLOT_HEIGHT_PERCENTAGE * 10**-2) / (
            current_user.preferences.PLOT_DPI
        )
    else:  # If not autoscale, use size defined in config_plot.py
        x = current_user.preferences.PLOT_WIDTH / (current_user.preferences.PLOT_DPI)
        y = current_user.preferences.PLOT_HEIGHT / (current_user.preferences.PLOT_DPI)
    return x, y


def get_last_time_market_was_open(dt):
    """Get last time the US market was open."""
    # Check if it is a weekend
    if dt.date().weekday() > 4:
        dt = get_last_time_market_was_open(dt - timedelta(hours=24))

    # Check if it is a holiday
    if dt.strftime("%Y-%m-%d") in us_holidays():
        dt = get_last_time_market_was_open(dt - timedelta(hours=24))

    dt = dt.replace(hour=21, minute=0, second=0)

    return dt


def check_file_type_saved(valid_types: Optional[List[str]] = None):
    """Provide valid types for the user to be able to select.

    Parameters
    ----------
    valid_types: List[str]
        List of valid types to export data

    Returns
    -------
    check_filenames: Optional[List[str]]
        Function that returns list of filenames to export data
    """

    def check_filenames(filenames: str = "") -> str:
        """Check if filenames are valid.

        Parameters
        ----------
        filenames: str
            filenames to be saved separated with comma

        Returns
        ----------
        str
            valid filenames separated with comma
        """
        if not filenames or not valid_types:
            return ""
        valid_filenames = list()
        for filename in filenames.split(","):
            if filename.endswith(tuple(valid_types)):
                valid_filenames.append(filename)
            else:
                console.print(
                    f"[red]Filename '{filename}' provided is not valid!\nPlease use one of the following file types:"
                    f"{','.join(valid_types)}[/red]\n"
                )
        return ",".join(valid_filenames)

    return check_filenames


def compose_export_path(func_name: str, dir_path: str) -> Path:
    """Compose export path for data from the terminal.

    Creates a path to a folder and a filename based on conditions.

    Parameters
    ----------
    func_name : str
        Name of the command that invokes this function
    dir_path : str
        Path of directory from where this function is called

    Returns
    -------
    Path
        Path variable containing the path of the exported file
    """
    now = datetime.now()
    # Resolving all symlinks and also normalizing path.
    resolve_path = Path(dir_path).resolve()
    # Getting the directory names from the path. Instead of using split/replace (Windows doesn't like that)
    # check if this is done in a main context to avoid saving with openbb_terminal
    if resolve_path.parts[-2] == "openbb_terminal":
        path_cmd = f"{resolve_path.parts[-1]}"
    else:
        path_cmd = f"{resolve_path.parts[-2]}_{resolve_path.parts[-1]}"

    default_filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{path_cmd}_{func_name}"

    full_path = get_current_user().preferences.USER_EXPORTS_DIRECTORY / default_filename

    return full_path


def ask_file_overwrite(file_path: Path) -> Tuple[bool, bool]:
    """Helper to provide a prompt for overwriting existing files.

    Returns two values, the first is a boolean indicating if the file exists and the
    second is a boolean indicating if the user wants to overwrite the file.
    """
    # Jeroen asked for a flag to overwrite no matter what
    current_user = get_current_user()
    if current_user.preferences.FILE_OVERWRITE:
        return False, True
    if get_current_system().TEST_MODE:
        return False, True
    if file_path.exists():
        overwrite = input("\nFile already exists. Overwrite? [y/n]: ").lower()
        if overwrite == "y":
            file_path.unlink(missing_ok=True)
            # File exists and user wants to overwrite
            return True, True
        # File exists and user does not want to overwrite
        return True, False
    # File does not exist
    return False, True


# This is a false positive on pylint and being tracked in pylint #3060
# pylint: disable=abstract-class-instantiated
def export_data(
    export_type: str,
    dir_path: str,
    func_name: str,
    df: pd.DataFrame = pd.DataFrame(),
    sheet_name: Optional[str] = None,
    figure: Optional[OpenBBFigure] = None,
    margin: bool = True,
) -> None:
    """Export data to a file.

    Parameters
    ----------
    export_type : str
        Type of export between: csv,json,xlsx,xls
    dir_path : str
        Path of directory from where this function is called
    func_name : str
        Name of the command that invokes this function
    df : pd.Dataframe
        Dataframe of data to save
    sheet_name : str
        If provided.  The name of the sheet to save in excel file
    figure : Optional[OpenBBFigure]
        Figure object to save as image file
    margin : bool
        Automatically adjust subplot parameters to give specified padding.
    """

    if export_type:
        saved_path = compose_export_path(func_name, dir_path).resolve()
        saved_path.parent.mkdir(parents=True, exist_ok=True)
        for exp_type in export_type.split(","):
            # In this scenario the path was provided, e.g. --export pt.csv, pt.jpg
            if "." in exp_type:
                saved_path = saved_path.with_name(exp_type)
            # In this scenario we use the default filename
            else:
                if ".OpenBB_openbb_terminal" in saved_path.name:
                    saved_path = saved_path.with_name(
                        saved_path.name.replace(
                            ".OpenBB_openbb_terminal", "OpenBBTerminal"
                        )
                    )
                saved_path = saved_path.with_suffix(f".{exp_type}")

            exists, overwrite = False, False
            is_xlsx = exp_type.endswith("xlsx")
            if sheet_name is None and is_xlsx or not is_xlsx:
                exists, overwrite = ask_file_overwrite(saved_path)

            if exists and not overwrite:
                existing = len(list(saved_path.parent.glob(saved_path.stem + "*")))
                saved_path = saved_path.with_stem(f"{saved_path.stem}_{existing + 1}")

            df = df.replace(
                {
                    r"\[yellow\]": "",
                    r"\[/yellow\]": "",
                    r"\[green\]": "",
                    r"\[/green\]": "",
                    r"\[red\]": "",
                    r"\[/red\]": "",
                    r"\[magenta\]": "",
                    r"\[/magenta\]": "",
                },
                regex=True,
            )

            df = df.applymap(revert_lambda_long_number_format)

            if exp_type.endswith("csv"):
                df.to_csv(saved_path)
            elif exp_type.endswith("json"):
                df.reset_index(drop=True, inplace=True)
                df.to_json(saved_path)
            elif exp_type.endswith("xlsx"):
                # since xlsx does not support datetimes with timezones we need to remove it
                df = remove_timezone_from_dataframe(df)

                if sheet_name is None:  # noqa: SIM223
                    df.to_excel(
                        saved_path,
                        index=True,
                        header=True,
                    )

                elif saved_path.exists():
                    with pd.ExcelWriter(
                        saved_path,
                        mode="a",
                        if_sheet_exists="new",
                        engine="openpyxl",
                    ) as writer:
                        df.to_excel(
                            writer, sheet_name=sheet_name, index=True, header=True
                        )
                else:
                    with pd.ExcelWriter(
                        saved_path,
                        engine="openpyxl",
                    ) as writer:
                        df.to_excel(
                            writer, sheet_name=sheet_name, index=True, header=True
                        )
            elif saved_path.suffix in [".jpg", ".pdf", ".png", ".svg"]:
                if figure is None:
                    console.print("No plot to export.")
                    continue
                figure.show(export_image=saved_path, margin=margin)
            else:
                console.print("Wrong export file specified.")
                continue

            console.print(f"Saved file: {saved_path}")

        if figure is not None:
            figure._exported = True  # pylint: disable=protected-access


def get_rf() -> float:
    """Use the fiscaldata.gov API to get most recent T-Bill rate.

    Returns
    -------
    rate : float
        The current US T-Bill rate
    """
    try:
        base = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service"
        end = "/v2/accounting/od/avg_interest_rates"
        filters = "?filter=security_desc:eq:Treasury Bills&sort=-record_date"
        response = request(base + end + filters)
        latest = response.json()["data"][0]
        return round(float(latest["avg_interest_rate_amt"]) / 100, 8)
    except Exception:
        return 0.02


def system_clear():
    """Clear screen."""
    os.system("cls||clear")  # nosec # noqa: S605,S607


def excel_columns() -> List[str]:
    """Return potential columns for excel.

    Returns
    -------
    letters : List[str]
        Letters to be used as excel columns
    """
    letters = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M"]
    letters += ["N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"]

    opts = (
        [f"{x}" for x in letters]
        + [f"{x}{y}" for x in letters for y in letters]
        + [f"{x}{y}{z}" for x in letters for y in letters for z in letters]
    )
    return opts


def handle_error_code(requests_obj, error_code_map):
    """Handle error code of HTTP requests.

    Parameters
    ----------
    requests_obj: Object
        Request object
    error_code_map: Dict
        Dictionary mapping of HTTP error code and output message

    """
    for error_code, error_msg in error_code_map.items():
        if requests_obj.status_code == error_code:
            console.print(error_msg)


def prefill_form(ticket_type, menu, path, command, message):
    """Pre-fill Google Form and open it in the browser."""
    form_url = "https://my.openbb.co/app/terminal/support?"

    params = {
        "type": ticket_type,
        "menu": menu,
        "path": path,
        "command": command,
        "message": message,
    }

    url_params = urllib.parse.urlencode(params)

    webbrowser.open(form_url + url_params)


def get_closing_price(ticker, days):
    """Get historical close price for n days in past for market asset.

    Parameters
    ----------
    ticker : str
        Ticker to get data for
    days : datetime
        No. of days in past

    Returns
    -------
    data : pd.DataFrame
        Historic close prices for ticker for given days
    """
    tick = yf.Ticker(ticker)
    df = tick.history(
        start=d.today() - timedelta(days=days),
        interval="1d",
    )["Close"]
    df = df.to_frame().reset_index()
    df = df.rename(columns={0: "Close"})
    df.index.name = "index"
    return df


def camel_case_split(string: str) -> str:
    """Convert a camel-case string to separate words.

    Parameters
    ----------
    string : str
        The string to be converted

    Returns
    -------
    new_string: str
        The formatted string
    """
    words = [[string[0]]]

    for c in string[1:]:
        if words[-1][-1].islower() and c.isupper():
            words.append(list(c))
        else:
            words[-1].append(c)

    results = ["".join(word) for word in words]
    return " ".join(results).title()


def is_valid_axes_count(
    axes: List[plt.Axes],
    n: int,
    custom_text: Optional[str] = None,
    prefix_text: Optional[str] = None,
    suffix_text: Optional[str] = None,
):
    """Check if axes list length is equal to n and log text if check result is false.

    Parameters
    ----------
    axes: List[plt.Axes]
        External axes (2 axes are expected in the list)
    n: int
        number of expected axes
    custom_text: Optional[str] = None
        custom text to log
    prefix_text: Optional[str] = None
        prefix text to add before text to log
    suffix_text: Optional[str] = None
        suffix text to add after text to log
    """
    if len(axes) == n:
        return True

    print_text = (
        custom_text
        if custom_text
        else f"Expected list of {n} axis item{'s' if n > 1 else ''}."
    )

    if prefix_text:
        print_text = f"{prefix_text} {print_text}"
    if suffix_text:
        print_text = f"{suffix_text} {print_text}"

    logger.error(print_text)
    console.print(f"[red]{print_text}\n[/red]")
    return False


def support_message(s: str) -> str:
    """Argparse type to check string is in valid format for the support command."""
    return s.replace('"', "")


def check_list_values(valid_values: List[str]):
    """Get valid values to test arguments given by user.

    Parameters
    ----------
    valid_values: List[str]
        List of valid values to be checked

    Returns
    -------
    check_list_values_from_valid_values_list:
        Function that ensures that the valid values go through and notifies user when value is not valid.
    """

    # Define the function with default arguments
    def check_list_values_from_valid_values_list(given_values: str) -> List[str]:
        """Check if argparse argument is an str format.

        Ensure that value1,value2,value3 and that the values value1, value2 and value3 are valid.

        Parameters
        ----------
        given_values: str
            values provided by the user

        Raises
        ------
        argparse.ArgumentTypeError
            Input number not between min and max values
        """
        success_values = list()

        values_found = (
            [val.strip() for val in given_values.split(",")]
            if "," in given_values
            else [given_values]
        )

        for value in values_found:
            # check if the value is valid
            if value in valid_values:
                success_values.append(value)
            else:
                console.print(f"[red]'{value}' is not valid.[/red]")

        if not success_values:
            log_and_raise(
                argparse.ArgumentTypeError("No correct arguments have been found")
            )
        return success_values

    # Return function handle to checking function
    return check_list_values_from_valid_values_list


def search_wikipedia(expression: str) -> None:
    """Search wikipedia for a given expression.

    Parameters
    ----------
    expression: str
        Expression to search for
    """
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{expression}"

    response = requests.request("GET", url, headers={}, data={})

    if response.status_code == 200:
        response_json = json.loads(response.text)
        res = {
            "title": response_json["title"],
            "url": f"{response_json['content_urls']['desktop']['page']}",
            "summary": response_json["extract"],
        }
    else:
        res = {
            "title": "[red]Not Found[/red]",
        }

    df = pd.json_normalize(res)

    print_rich_table(
        df,
        headers=list(df.columns),
        show_index=False,
        title=f"Wikipedia results for {expression}",
    )


def screenshot() -> None:
    """Screenshot the terminal window or the plot window.

    Parameters
    ----------
    terminal_window_target: bool
        Target the terminal window
    """
    try:
        if plt.get_fignums():
            img_buf = io.BytesIO()
            plt.savefig(img_buf, format="png")
            shot = Image.open(img_buf)
            screenshot_to_canvas(shot, plot_exists=True)

        else:
            console.print("No plots found.\n")

    except Exception as err:
        console.print(f"Cannot reach window - {err}\n")


def screenshot_to_canvas(shot, plot_exists: bool = False):
    """Frame image to OpenBB canvas.

    Parameters
    ----------
    shot
        Image to frame with OpenBB Canvas
    plot_exists: bool
        Variable to say whether the image is a plot or screenshot of terminal
    """
    WHITE_LINE_WIDTH = 3
    OUTSIDE_CANVAS_WIDTH = shot.width + 4 * WHITE_LINE_WIDTH + 5
    OUTSIDE_CANVAS_HEIGHT = shot.height + 4 * WHITE_LINE_WIDTH + 5
    UPPER_SPACE = 40
    BACKGROUND_WIDTH_SLACK = 150
    BACKGROUND_HEIGHT_SLACK = 150

    background = Image.open(
        Path(os.path.abspath(__file__), "../../images/background.png")
    )
    logo = Image.open(
        Path(os.path.abspath(__file__), "../../images/openbb_horizontal_logo.png")
    )

    try:
        if plot_exists:
            HEADER_HEIGHT = 0
            RADIUS = 8

            background = background.resize(
                (
                    shot.width + BACKGROUND_WIDTH_SLACK,
                    shot.height + BACKGROUND_HEIGHT_SLACK,
                )
            )

            x = int((background.width - OUTSIDE_CANVAS_WIDTH) / 2)
            y = UPPER_SPACE

            white_shape = (
                (x, y),
                (x + OUTSIDE_CANVAS_WIDTH, y + OUTSIDE_CANVAS_HEIGHT),
            )
            img = ImageDraw.Draw(background)
            img.rounded_rectangle(
                white_shape,
                fill="black",
                outline="white",
                width=WHITE_LINE_WIDTH,
                radius=RADIUS,
            )
            background.paste(shot, (x + WHITE_LINE_WIDTH + 5, y + WHITE_LINE_WIDTH + 5))

            # Logo
            background.paste(
                logo,
                (
                    int((background.width - logo.width) / 2),
                    UPPER_SPACE
                    + OUTSIDE_CANVAS_HEIGHT
                    + HEADER_HEIGHT
                    + int(
                        (
                            background.height
                            - UPPER_SPACE
                            - OUTSIDE_CANVAS_HEIGHT
                            - HEADER_HEIGHT
                            - logo.height
                        )
                        / 2
                    ),
                ),
                logo,
            )

            background.show(title="screenshot")

    except Exception:
        console.print("Shot failed.")


@lru_cache
def load_json(path: Path) -> Dict[str, str]:
    """Load a dictionary from a json file path.

    Parameter
    ----------
    path : Path
        The path for the json file

    Returns
    -------
    Dict[str, str]
        The dictionary loaded from json
    """
    try:
        with open(path) as file:
            return json.load(file)
    except Exception as e:
        console.print(
            f"[red]Failed to load preferred source from file: "
            f"{get_current_user().preferences.USER_DATA_SOURCES_FILE}[/red]"
        )
        console.print(f"[red]{e}[/red]")
        return {}


def list_from_str(value: str) -> List[str]:
    """Convert a string to a list.

    Parameter
    ---------
    value : str
        The string to convert

    Returns
    -------
    new_value: List[str]
        The list of strings
    """
    if value:
        return value.split(",")
    return []


def str_date_to_timestamp(date: str) -> int:
    """Transform string date to timestamp

    Parameters
    ----------
    start_date : str
        Initial date, format YYYY-MM-DD

    Returns
    -------
    date_ts : int
        Initial date timestamp (e.g., 1_614_556_800)
    """

    date_ts = int(
        datetime.strptime(date + " 00:00:00+0000", "%Y-%m-%d %H:%M:%S%z").timestamp()
    )

    return date_ts


def check_start_less_than_end(start_date: str, end_date: str) -> bool:
    """Check if start_date is equal to end_date.

    Parameters
    ----------
    start_date : str
        Initial date, format YYYY-MM-DD
    end_date : str
        Final date, format YYYY-MM-DD

    Returns
    -------
    bool
        True if start_date is not equal to end_date, False otherwise
    """
    if start_date is None or end_date is None:
        return False
    if start_date == end_date:
        console.print("[red]Start date and end date cannot be the same.[/red]")
        return True
    if start_date > end_date:
        console.print("[red]Start date cannot be greater than end date.[/red]")
        return True
    return False


# Write an abstract helper to make requests from a url with potential headers and params
def request(
    url: str, method: str = "get", timeout: int = 0, **kwargs
) -> requests.Response:
    """Abstract helper to make requests from a url with potential headers and params.

    Parameters
    ----------
    url : str
        Url to make the request to
    method : str
        HTTP method to use.  Choose from:
        delete, get, head, patch, post, put, by default "get"
    timeout : int
        How many seconds to wait for the server to send data

    Returns
    -------
    requests.Response
        Request response object

    Raises
    ------
    ValueError
        If invalid method is passed
    """
    method = method.lower()
    if method not in ["delete", "get", "head", "patch", "post", "put"]:
        raise ValueError(f"Invalid method: {method}")
    current_user = get_current_user()
    # We want to add a user agent to the request, so check if there are any headers
    # If there are headers, check if there is a user agent, if not add one.
    # Some requests seem to work only with a specific user agent, so we want to be able to override it.
    headers = kwargs.pop("headers", {})
    timeout = timeout or current_user.preferences.REQUEST_TIMEOUT

    if "User-Agent" not in headers:
        headers["User-Agent"] = get_user_agent()
    func = getattr(requests, method)
    return func(
        url,
        headers=headers,
        timeout=timeout,
        **kwargs,
    )


def remove_timezone_from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Remove timezone information from a dataframe.

    Parameters
    ----------
    df : pd.DataFrame
        The dataframe to remove timezone information from

    Returns
    -------
    pd.DataFrame
        The dataframe with timezone information removed
    """

    date_cols = []
    index_is_date = False

    # Find columns and index containing date data
    if (
        df.index.dtype.kind == "M"
        and hasattr(df.index.dtype, "tz")
        and df.index.dtype.tz is not None
    ):
        index_is_date = True

    for col, dtype in df.dtypes.items():
        if dtype.kind == "M" and hasattr(df.index.dtype, "tz") and dtype.tz is not None:
            date_cols.append(col)

    # Remove the timezone information
    for col in date_cols:
        df[col] = df[col].dt.date

    if index_is_date:
        index_name = df.index.name
        df.index = df.index.date
        df.index.name = index_name

    return df


@check_api_key(["API_OPENAI_KEY"])
def query_LLM_local(query_text, gpt_model):
    current_user = get_current_user()
    os.environ["OPENAI_API_KEY"] = current_user.credentials.API_OPENAI_KEY

    # check if index exists
    index_path = GPT_INDEX_DIRECTORY / f"index_{GPT_INDEX_VER}.json"
    old_index_paths = [
        str(x) for x in GPT_INDEX_DIRECTORY.glob("index_*.json") if x != index_path
    ]

    # define LLM
    llm_predictor = LLMPredictor(llm=ChatOpenAI(temperature=0.5, model_name=gpt_model))
    # define prompt helper
    prompt_helper = PromptHelper(context_window=4096, num_output=256)
    service_context = ServiceContext.from_defaults(
        llm_predictor=llm_predictor, prompt_helper=prompt_helper
    )

    if os.path.exists(index_path):
        # rebuild storage context
        storage_context = StorageContext.from_defaults(persist_dir=index_path)
        index = load_index_from_storage(
            service_context=service_context, storage_context=storage_context
        )
    else:
        # If the index file doesn't exist or is of incorrect version, generate a new one
        # First, remove old version(s), if any
        for path in old_index_paths:
            if os.path.isfile(path):
                os.remove(path)
            elif os.path.isdir(path):
                shutil.rmtree(path)

        # Then, generate and save new index
        # import from print console and say generating index, this might take a while
        console.print("Generating index, this might take a while....\n")

        # read in documents
        documents = SimpleDirectoryReader(GPT_INDEX_DIRECTORY / "data/").load_data()
        index = VectorStoreIndex.from_documents(
            documents, service_context=service_context
        )

        # save to disk
        console.print("Saving index to disk....\n")
        index.storage_context.persist(index_path)

    current_date = datetime.now().astimezone(pytz.timezone("America/New_York"))

    prompt_string = f"""From the cli argparse help text above, provide the terminal
        command for {query_text}. If relevant, use the examples as guidance.
        Provide the exact command along with the parent command with a "/" separation to get that information,
        and nothing else including any explanation. Don't add any other word such as 'Command to get', 'Answer'
        or the likes.  If you do not know, reply "I don't know"

        Current date: {current_date.strftime("%Y-%m-%d")}
        Current day of the week: {current_date.strftime("%A")}

        Remember:
        1. It is very important to provide the full path of the command including the parent command and loading
        the particular target before running any subsequent commands
        2. If you are asked about dates or times, load the target dates, times span during the "load" command
        before running any subsequent commands. replace all <> with the actual dates and times.  The date format should
        be YYYY-MM-DD. If there is no date included in the query, do not specify any.
        3. Country names should be snake case and lower case. example: united_states.
        4. Always use a comma to separate between countries and no spaces: example: united_states,italy,spain
        5. Always use "load" command first before running any subsequent commands. example:
        stocks/load <symbol>/ ....
        crypto/load <symbol>/ .... etc.
        6. Do not include --export unless the request asks for the data to be exported or saved to a specific file type.
        7. Do not make up any subcommands or options for the specific command.
        8. Do not provide anything that could be interpreted as investment advice.
        9. Any request asking for options refers to stocks/options.

        Only do what is asked and only provide a single command string, never more than one.
        """

    # try to get the response from the index
    try:
        query_engine = index.as_query_engine()
        response = query_engine.query(prompt_string)
        return response.response, response.source_nodes
    except Exception as e:
        # check if the error has the following "The model: `gpt-4` does not exist"
        if "The model: `gpt-4` does not exist" in str(e):
            console.print(
                "[red]You do not have access to GPT4 model with your API key."
                " Please try again with valid API Access.[/red]"
            )
            return None

        console.print(f"[red]Something went wrong with the query. {e}[/red]")
        return None, None


def query_LLM_remote(query_text: str):
    """Query askobb on gpt-3.5 turbo hosted model

    Parameters
    ----------
    query_text : str
        Query string for askobb
    """

    url = "https://api.openbb.co/askobb"

    data = {"prompt": query_text, "accessToken": get_current_user().profile.token}

    ask_obbrequest_data = request(url, method="POST", json=data, timeout=15).json()

    if "error" in ask_obbrequest_data:
        console.print(f"[red]{ask_obbrequest_data['error']}[/red]")
        return None, None

    return ask_obbrequest_data["response"], ask_obbrequest_data["source_nodes"]


def check_valid_date(date_string) -> bool:
    """ "Helper to see if we can parse the string to a date"""
    try:
        # Try to parse the string with strptime()
        datetime.strptime(
            date_string, "%Y-%m-%d"
        )  # Use the format your dates are expected to be in
        return True  # If it can be parsed, then it is a valid date string
    except ValueError:  # strptime() throws a ValueError if the string can't be parsed
        return False
