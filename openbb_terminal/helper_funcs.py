"""Helper functions."""

__docformat__ = "numpy"

# pylint: disable=too-many-lines

# IMPORTS STANDARD LIBRARY
# IMPORTS STANDARD
import argparse
import io
import logging
import os
import random
import re
from datetime import (
    datetime,
)
from pathlib import Path
from typing import Dict, List, Optional, Union

# IMPORTS THIRDPARTY
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import pandas.io.formats.format
import pytz
import requests
from pandas.plotting import register_matplotlib_converters
from PIL import Image, ImageDraw
from rich.table import Table

from openbb_terminal import plots_backend
from openbb_terminal.core.config.paths import (
    MISCELLANEOUS_DIRECTORY,
)

# IMPORTS INTERNAL
from openbb_terminal.core.session.current_user import get_current_user
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

ALLOWED_NUMBER_OF_ROWS = 366
ALLOWED_NUMBER_OF_COLUMNS = 15

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
    limit: Optional[int] = 1000,
    columns_keep_types: Optional[List[str]] = None,
    use_tabulate_df: bool = True,
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
    columns_keep_types: Optional[List[str]]
        Columns to keep their types, i.e. not convert to numeric
    """
    if export:
        return

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

    exceeds_allowed_columns = len(df.columns) > ALLOWED_NUMBER_OF_COLUMNS
    exceeds_allowed_rows = len(df) > ALLOWED_NUMBER_OF_ROWS

    if exceeds_allowed_columns:
        original_columns = df.columns.tolist()
        trimmed_columns = df.columns.tolist()[:ALLOWED_NUMBER_OF_COLUMNS]
        df = df[trimmed_columns]
        trimmed_columns = [
            col for col in original_columns if col not in trimmed_columns
        ]

    if exceeds_allowed_rows:
        n_rows = len(df.index)
        trimmed_rows = df.index.tolist()[:ALLOWED_NUMBER_OF_ROWS]
        df = df.loc[trimmed_rows]
        trimmed_rows_count = n_rows - ALLOWED_NUMBER_OF_ROWS

    if use_tabulate_df:
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
                (
                    str(x)
                    if not isinstance(x, float) and not isinstance(x, np.float64)
                    else (
                        f"{x:{floatfmt[idx]}}"
                        if isinstance(floatfmt, list)
                        else (
                            f"{x:.2e}"
                            if 0 < abs(float(x)) <= 0.0001
                            else f"{x:floatfmt}"
                        )
                    )
                )
                for idx, x in enumerate(values)
            ]
            table.add_row(*row_idx)
        console.print(table)
    else:
        console.print(df.to_string(col_space=0))

    if exceeds_allowed_columns:
        console.print(
            f"[yellow]\nAllowed number of columns exceeded ({ALLOWED_NUMBER_OF_COLUMNS}).\n"
            f"The following columns were removed from the output: {', '.join(trimmed_columns)}.\n[/yellow]"
        )

    if exceeds_allowed_rows:
        console.print(
            f"[yellow]\nAllowed number of rows exceeded ({ALLOWED_NUMBER_OF_ROWS}).\n"
            f"{trimmed_rows_count} rows were removed from the output.\n[/yellow]"
        )

    if exceeds_allowed_columns or exceeds_allowed_rows:
        console.print("Use the `--export` flag to analyse the full output on a file.")


def check_non_negative(value) -> int:
    """Argparse type to check non negative int."""
    new_value = int(value)
    if new_value < 0:
        log_and_raise(argparse.ArgumentTypeError(f"{value} is negative"))
    return new_value


def check_positive(value) -> int:
    """Argparse type to check positive int."""
    new_value = int(value)
    if new_value <= 0:
        log_and_raise(
            argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
        )
    return new_value


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


def system_clear():
    """Clear screen."""
    os.system("cls||clear")  # nosec # noqa: S605,S607


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
