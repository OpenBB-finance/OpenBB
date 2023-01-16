"""Helper functions."""
__docformat__ = "numpy"
# pylint: disable=too-many-lines
import argparse
import io
import logging
from pathlib import Path
from typing import List, Union, Optional, Dict
from functools import lru_cache
from datetime import datetime, timedelta
from datetime import date as d
import types
from collections.abc import Iterable
import os
import re
import random
import sys
from difflib import SequenceMatcher
import webbrowser
import urllib.parse
import json

import pytz
import pandas as pd
from rich.table import Table
import iso8601
import dotenv
import matplotlib
import matplotlib.pyplot as plt
from holidays import US as us_holidays
from pandas._config.config import get_option
from pandas.plotting import register_matplotlib_converters
import pandas.io.formats.format
import requests
from screeninfo import get_monitors
import yfinance as yf
import numpy as np

from PIL import Image, ImageDraw

from openbb_terminal.rich_config import console
from openbb_terminal import feature_flags as obbff
from openbb_terminal import config_plot as cfgPlot
from openbb_terminal.core.config.paths import (
    HOME_DIRECTORY,
    USER_ENV_FILE,
    USER_EXPORTS_DIRECTORY,
)
from openbb_terminal.core.config import paths

logger = logging.getLogger(__name__)

register_matplotlib_converters()
if cfgPlot.BACKEND is not None:
    matplotlib.use(cfgPlot.BACKEND)

NO_EXPORT = 0
EXPORT_ONLY_RAW_DATA_ALLOWED = 1
EXPORT_ONLY_FIGURES_ALLOWED = 2
EXPORT_BOTH_RAW_DATA_AND_FIGURES = 3

MENU_GO_BACK = 0
MENU_QUIT = 1
MENU_RESET = 2

# Command location path to be shown in the figures depending on watermark flag
command_location = ""


# pylint: disable=R0912

# pylint: disable=global-statement
def set_command_location(cmd_loc: str):
    """Set command location.

    Parameters
    ----------
    cmd_loc: str
        Command location called by user
    """
    global command_location
    command_location = cmd_loc


# pylint: disable=global-statement
def set_user_data_folder(env_file: str = ".env", path_folder: str = ""):
    """Set user data folder location.

    Parameters
    ----------
    env_file : str
        Env file to be updated
    path_folder: str
        Path folder location
    """
    dotenv.set_key(env_file, "OPENBB_USER_DATA_DIRECTORY", path_folder)
    paths.USER_DATA_DIRECTORY = Path(path_folder)


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
    if an_input:
        if an_input == "/":
            an_input = "home"
        elif an_input[0] == "/":
            an_input = "home" + an_input

    # everything from ` -f ` to the next known extension
    file_flag = r"(\ -f |\ --file )"
    up_to = r".*?"
    known_extensions = r"(\.xlsx|.csv|.xls|.tsv|.json|.yaml|.ini|.openbb|.ipynb)"
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
def print_rich_table(
    df: pd.DataFrame,
    show_index: bool = False,
    title: str = "",
    index_name: str = "",
    headers: Union[List[str], pd.Index] = None,
    floatfmt: Union[str, List[str]] = ".2f",
    show_header: bool = True,
    automatic_coloring: bool = False,
    columns_to_auto_color: List[str] = None,
    rows_to_auto_color: List[str] = None,
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
    """
    if obbff.USE_TABULATE_DF:
        table = Table(title=title, show_lines=True, show_header=show_header)

        if obbff.USE_COLOR and automatic_coloring:
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

        if show_index:
            table.add_column(index_name)

        if headers is not None:
            if isinstance(headers, pd.Index):
                headers = list(headers)
            if len(headers) != len(df.columns):
                log_and_raise(
                    ValueError("Length of headers does not match length of DataFrame")
                )
            for header in headers:
                table.add_column(str(header))
        else:
            for column in df.columns:
                table.add_column(str(column))

        if isinstance(floatfmt, list):
            if len(floatfmt) != len(df.columns):
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

        if obbff.USE_COLOR and automatic_coloring:
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


def check_positive(value) -> int:
    """Argparse type to check positive int."""
    new_value = int(value)
    if new_value <= 0:
        log_and_raise(
            argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
        )
    return new_value


def check_positive_float(value) -> float:
    """Argparse type to check positive int."""
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


def plot_view_stock(df: pd.DataFrame, symbol: str, interval: str):
    """Plot the loaded stock dataframe.

    Parameters
    ----------
    df: Dataframe
        Dataframe of prices and volumes
    symbol: str
        Symbol of ticker
    interval: str
        Stock data resolution for plotting purposes
    """
    df.sort_index(ascending=True, inplace=True)
    bar_colors = ["r" if x[1].Open < x[1].Close else "g" for x in df.iterrows()]

    try:
        fig, ax = plt.subplots(
            2,
            1,
            gridspec_kw={"height_ratios": [3, 1]},
            figsize=plot_autoscale(),
            dpi=cfgPlot.PLOT_DPI,
        )
    except Exception as e:
        console.print(e)
        console.print(
            "Encountered an error trying to open a chart window. Check your X server configuration."
        )
        logging.exception("%s", type(e).__name__)
        return

    # In order to make nice Volume plot, make the bar width = interval
    if interval == "1440min":
        bar_width = timedelta(days=1)
        title_string = "Daily"
    else:
        bar_width = timedelta(minutes=int(interval.split("m")[0]))
        title_string = f"{int(interval.split('m')[0])} min"

    ax[0].yaxis.tick_right()
    if "Adj Close" in df.columns:
        ax[0].plot(df.index, df["Adj Close"], c=cfgPlot.VIEW_COLOR)
    else:
        ax[0].plot(df.index, df["Close"], c=cfgPlot.VIEW_COLOR)
    ax[0].set_xlim(df.index[0], df.index[-1])
    ax[0].set_xticks([])
    ax[0].yaxis.set_label_position("right")
    ax[0].set_ylabel("Share Price ($)")
    ax[0].grid(axis="y", color="gainsboro", linestyle="-", linewidth=0.5)

    ax[0].spines["top"].set_visible(False)
    ax[0].spines["left"].set_visible(False)
    ax[1].bar(
        df.index, df.Volume / 1_000_000, color=bar_colors, alpha=0.8, width=bar_width
    )
    ax[1].set_xlim(df.index[0], df.index[-1])
    ax[1].yaxis.tick_right()
    ax[1].yaxis.set_label_position("right")
    ax[1].set_ylabel("Volume [1M]")
    ax[1].grid(axis="y", color="gainsboro", linestyle="-", linewidth=0.5)
    ax[1].spines["top"].set_visible(False)
    ax[1].spines["left"].set_visible(False)
    ax[1].set_xlabel("Time")
    fig.suptitle(
        symbol + " " + title_string,
        size=20,
        x=0.15,
        y=0.95,
        fontfamily="serif",
        fontstyle="italic",
    )
    if obbff.USE_ION:
        plt.ion()
    fig.tight_layout(pad=2)
    plt.setp(ax[1].get_xticklabels(), rotation=20, horizontalalignment="right")

    plt.show()


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


def lambda_long_number_format(num, round_decimal=3) -> str:
    """Format a long number."""
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
    if isinstance(num, str) and num.lstrip("-").isdigit():
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
    if granularity >= timedelta(days=1):
        intraday = False
    else:
        intraday = True
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
    if is_intraday(df):
        date_format = "%b %d %H:%M"
    else:
        date_format = "%Y-%m-%d"
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

    s_text = tweet["full_text"] if "full_text" in tweet.keys() else tweet["text"]
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

    return random.choice(user_agent_strings)  # nosec


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
    for (a, b) in replacements:
        word = word.replace(a, b)
    return word


def get_flair() -> str:
    """Get a flair icon."""
    flairs = {
        ":openbb": "(🦋)",
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

    flair = (
        flairs[str(obbff.USE_FLAIR)]
        if str(obbff.USE_FLAIR) in flairs
        else str(obbff.USE_FLAIR)
    )

    set_default_timezone()
    if obbff.USE_DATETIME and get_user_timezone_or_invalid() != "INVALID":
        dtime = datetime.now(pytz.timezone(get_user_timezone())).strftime(
            "%Y %b %d, %H:%M"
        )

        # if there is no flair, don't add an extra space after the time
        if flair == "":
            return f"{dtime}"

        return f"{dtime} {flair}"

    return flair


def set_default_timezone() -> None:
    """Set a default (America/New_York) timezone if one doesn't exist."""
    dotenv.load_dotenv(USER_ENV_FILE)
    user_tz = os.getenv("OPENBB_TIMEZONE")
    if not user_tz:
        dotenv.set_key(USER_ENV_FILE, "OPENBB_TIMEZONE", "America/New_York")


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
    dotenv.load_dotenv(USER_ENV_FILE, override=True)
    user_tz = os.getenv("OPENBB_TIMEZONE")
    if user_tz:
        return user_tz
    return ""


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


def replace_user_timezone(user_tz: str) -> None:
    """Replace user timezone.

    Parameters
    ----------
    user_tz: str
        User timezone to set
    """
    if is_timezone_valid(user_tz):
        dotenv.set_key(USER_ENV_FILE, "OPENBB_TIMEZONE", user_tz)
        console.print("Timezone successfully updated", "\n")
    else:
        console.print("Timezone selected is not valid", "\n")


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
    screens = get_monitors()  # Get all available monitors
    if len(screens) - 1 < cfgPlot.MONITOR:  # Check to see if chosen monitor is detected
        monitor = 0
        console.print(
            f"Could not locate monitor {cfgPlot.MONITOR}, using primary monitor."
        )
    else:
        monitor = cfgPlot.MONITOR
    main_screen = screens[monitor]  # Choose what monitor to get

    return (main_screen.width, main_screen.height)


def plot_autoscale():
    """Autoscale plot."""
    if obbff.USE_PLOT_AUTOSCALING:
        x, y = get_screeninfo()  # Get screen size
        x = ((x) * cfgPlot.PLOT_WIDTH_PERCENTAGE * 10**-2) / (
            cfgPlot.PLOT_DPI
        )  # Calculate width
        if cfgPlot.PLOT_HEIGHT_PERCENTAGE == 100:  # If full height
            y = y - 60  # Remove the height of window toolbar
        y = ((y) * cfgPlot.PLOT_HEIGHT_PERCENTAGE * 10**-2) / (cfgPlot.PLOT_DPI)
    else:  # If not autoscale, use size defined in config_plot.py
        x = cfgPlot.PLOT_WIDTH / (cfgPlot.PLOT_DPI)
        y = cfgPlot.PLOT_HEIGHT / (cfgPlot.PLOT_DPI)
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


def check_file_type_saved(valid_types: List[str] = None):
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

    full_path = USER_EXPORTS_DIRECTORY / default_filename

    return full_path


def export_data(
    export_type: str, dir_path: str, func_name: str, df: pd.DataFrame = pd.DataFrame()
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
    """
    if export_type:
        export_path = compose_export_path(func_name, dir_path)
        export_folder = str(export_path.parent)
        export_filename = export_path.name
        export_path.parent.mkdir(parents=True, exist_ok=True)
        for exp_type in export_type.split(","):
            # In this scenario the path was provided, e.g. --export pt.csv, pt.jpg
            if "." in exp_type:
                saved_path = os.path.join(export_folder, exp_type)
            # In this scenario we use the default filename
            else:
                if ".OpenBB_openbb_terminal" in export_filename:
                    export_filename = export_filename.replace(
                        ".OpenBB_openbb_terminal", "OpenBBTerminal"
                    )
                saved_path = os.path.join(
                    export_folder, f"{export_filename}.{exp_type}"
                )

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

            if exp_type.endswith("csv"):
                df.to_csv(saved_path)
            elif exp_type.endswith("json"):
                df.reset_index(drop=True, inplace=True)
                df.to_json(saved_path)
            elif exp_type.endswith("xlsx"):
                df.to_excel(saved_path, index=True, header=True)
            elif exp_type.endswith("png"):
                plt.savefig(saved_path)
            elif exp_type.endswith("jpg"):
                plt.savefig(saved_path)
            elif exp_type.endswith("pdf"):
                plt.savefig(saved_path)
            elif exp_type.endswith("svg"):
                plt.savefig(saved_path)
            else:
                console.print("\nWrong export file specified.")

            console.print(f"\nSaved file: {saved_path}")


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
        response = requests.get(base + end + filters)
        latest = response.json()["data"][0]
        return round(float(latest["avg_interest_rate_amt"]) / 100, 8)
    except Exception:
        return 0.02


def system_clear():
    """Clear screen."""
    os.system("cls||clear")  # nosec


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
    form_url = "https://openbb.co/support?"

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


def choice_check_after_action(action=None, choices=None):
    """Return an action class that checks choice after action call.

    Does that for argument of argparse.ArgumentParser.add_argument function.

    Parameters
    ----------
    action : Union[class, function]
        Action for set args before check choices.
        If action is class, it must implement argparse.Action methods
        If action is function, it takes 4 args(parser, namespace, values, option_string)
        and needs to return value to set dest

    choices : Union[Iterable, function]
        A container of values that should be allowed.
        If choices is function, it takes 1 args(value) to check and
        return bool that value is allowed or not

    Returns
    -------
    Class
        Class extended argparse.Action
    """
    if isinstance(choices, Iterable):

        def choice_checker(value):
            return value in choices

    elif isinstance(choices, types.FunctionType):
        choice_checker = choices
    else:
        raise NotImplementedError("choices argument must be iterable or function")

    if isinstance(action, type):

        class ActionClass(action):
            def __call__(self, parser, namespace, values, option_string=None):
                super().__call__(parser, namespace, values, option_string)
                if not choice_checker(getattr(namespace, self.dest)):
                    raise ValueError(
                        f"{getattr(namespace, self.dest)} is not in {choices}"
                    )

    elif isinstance(action, types.FunctionType):

        class ActionClass(argparse.Action):
            def __call__(self, parser, namespace, values, option_string=None):
                setattr(
                    namespace,
                    self.dest,
                    action(parser, namespace, values, option_string),
                )
                if not choice_checker(getattr(namespace, self.dest)):
                    raise ValueError(
                        f"{getattr(namespace, self.dest)} is not in {choices}"
                    )

    else:
        raise NotImplementedError("action argument must be class or function")

    return ActionClass


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

    if custom_text:
        print_text = custom_text
    else:
        print_text = f"Expected list of {n} axis item{'s' if n>1 else ''}."

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

        if "," in given_values:
            values_found = [val.strip() for val in given_values.split(",")]
        else:
            values_found = [given_values]

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
            "url": f"[blue]{response_json['content_urls']['desktop']['page']}[/blue]",
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

    except Exception as e:
        console.print(f"Cannot reach window - {e}\n")


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
def load_json(path: str) -> Dict[str, str]:
    """Load a dictionary from a json file path.

    Parameter
    ----------
    path : str
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
            f"{obbff.PREFERRED_DATA_SOURCE_FILE}[/red]"
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
