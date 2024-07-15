"""Utils."""

import argparse
import os
import random
import re
import shutil
import sys
from contextlib import contextmanager
from datetime import (
    datetime,
)
from pathlib import Path
from typing import TYPE_CHECKING, Dict, List, Optional, Tuple, Union

import numpy as np
import pandas as pd
import requests
from openbb_cli.config.constants import AVAILABLE_FLAIRS, ENV_FILE_SETTINGS
from openbb_cli.session import Session
from openbb_core.app.model.obbject import OBBject
from pytz import all_timezones, timezone
from rich.table import Table

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import OpenBBFigure

# pylint: disable=R1702,R0912


# pylint: disable=too-many-statements,no-member,too-many-branches,C0302

session = Session()


def remove_file(path: Path) -> bool:
    """Remove path.

    Parameters
    ----------
    path : Path
        The file path.

    Returns
    -------
    bool
        The status of the removal.
    """
    # TODO: Check why module level import leads to circular import.
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        return True
    except Exception:
        session.console.print(
            f"\n[bold red]Failed to remove {path}"
            "\nPlease delete this manually![/bold red]"
        )
        return False


def print_goodbye():
    """Print a goodbye message when quitting the terminal."""
    # LEGACY GOODBYE MESSAGES - You'll live in our hearts forever.
    # "An informed ape, is a strong ape."
    # "Remember that stonks only go up."
    # "Diamond hands."
    # "Apes together strong."
    # "This is our way."
    # "Keep the spacesuit ape, we haven't reached the moon yet."
    # "I am not a cat. I'm an ape."
    # "We like the terminal."
    # "...when offered a flight to the moon, nobody asks about what seat."

    text = """
[param]Thank you for using the OpenBB Platform CLI and being part of this journey.[/param]

We hope you'll find the new OpenBB Platform CLI a valuable tool.

To stay tuned, sign up for our newsletter: [cmds]https://openbb.co/newsletter.[/]

Please feel free to check out our other products:

[bold]OpenBB Terminal Pro[/]: [cmds]https://openbb.co/products/pro[/cmds]
[bold]OpenBB Platform:[/]     [cmds]https://openbb.co/products/platform[/cmds]
[bold]OpenBB Bot[/]:          [cmds]https://openbb.co/products/bot[/cmds]
    """
    session.console.print(text)


def print_guest_block_msg():
    """Block guest users from using the cli."""
    if session.is_local():
        session.console.print(
            "[info]You are currently logged as a guest.[/info]\n"
            "[info]Login to use this feature.[/info]\n\n"
            "[info]If you don't have an account, you can create one here: [/info]"
            f"[cmds]{session.settings.HUB_URL + '/register'}\n[/cmds]"
        )


def bootup():
    """Bootup the cli."""
    if sys.platform == "win32":
        # Enable VT100 Escape Sequence for WINDOWS 10 Ver. 1607
        os.system("")  # nosec # noqa: S605,S607

    try:
        if os.name == "nt":
            # pylint: disable=E1101
            sys.stdin.reconfigure(encoding="utf-8")  # type: ignore
            # pylint: disable=E1101
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
    except Exception as e:
        session.console.print(e, "\n")


def welcome_message():
    """Print the welcome message.

    Prints first welcome message, help and a notification if updates are available.
    """
    session.console.print(
        f"\nWelcome to OpenBB Platform CLI v{session.settings.VERSION}"
    )


def reset(queue: Optional[List[str]] = None):
    """Reset the CLI.

    Allows for checking code without quitting.
    """
    session.console.print("resetting...")
    debug = session.settings.DEBUG_MODE
    dev = session.settings.DEV_BACKEND

    try:
        # remove the hub routines
        if not session.is_local():
            remove_file(
                Path(session.user.preferences.export_directory, "routines", "hub")
            )

            # if not get_current_user().profile.remember:
            #     Local.remove(HIST_FILE_PROMPT)

        # we clear all openbb_cli modules from sys.modules
        for module in list(sys.modules.keys()):
            parts = module.split(".")
            if parts[0] == "openbb_cli":
                del sys.modules[module]

        queue_list = ["/".join(queue) if len(queue) > 0 else ""]  # type: ignore
        # pylint: disable=import-outside-toplevel
        # we run the cli again
        if session.is_local():
            from openbb_cli.controllers.cli_controller import main

            main(debug, dev, queue_list, module="")  # type: ignore
        else:
            from openbb_cli.controllers.cli_controller import launch

            launch(queue=queue_list)

    except Exception as e:
        session.console.print(f"Unfortunately, resetting wasn't possible: {e}\n")
        print_goodbye()


@contextmanager
def suppress_stdout():
    """Suppress the stdout."""
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = devnull
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr


def first_time_user() -> bool:
    """Check whether a user is a first time user.

    A first time user is someone with an empty .env file.
    If this is true, it also adds an env variable to make sure this does not run again.

    Returns
    -------
    bool
        Whether or not the user is a first time user
    """
    if ENV_FILE_SETTINGS.stat().st_size == 0:
        session.settings.set_item("PREVIOUS_USE", True)
        return True
    return False


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

    commands = an_input.split("/") if "timezone" not in an_input else [an_input]

    for command_num, command in enumerate(commands):
        if command == commands[command_num] == commands[-1] == "":
            return list(filter(None, commands))
        matching_placeholders = [tag for tag in placeholders if tag in command]
        if len(matching_placeholders) > 0:
            for tag in matching_placeholders:
                commands[command_num] = command.replace(tag, placeholders[tag])
    return commands


def return_colored_value(value: str):
    """Return the string value based on condition.

    Return it with green, yellow, red or white color based on
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

    MAX_COLS = session.settings.ALLOWED_NUMBER_OF_COLUMNS
    MAX_ROWS = session.settings.ALLOWED_NUMBER_OF_ROWS

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
                df[col] = df[col].apply(pd.to_numeric)
        except (ValueError, TypeError):
            df[col] = df[col].astype(str)

    def _get_headers(_headers: Union[List[str], pd.Index]) -> List[str]:
        """Check if headers are valid and return them."""
        output = _headers
        if isinstance(_headers, pd.Index):
            output = list(_headers)
        if len(output) != len(df.columns):
            raise ValueError("Length of headers does not match length of DataFrame.")
        return output  # type: ignore

    if session.settings.USE_INTERACTIVE_DF:
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

        session._backend.send_table(  # type: ignore  # pylint: disable=protected-access
            df_table=df_outgoing,
            title=title,
            theme=session.user.preferences.table_style,
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

    exceeds_allowed_columns = len(df.columns) > MAX_COLS
    exceeds_allowed_rows = len(df) > MAX_ROWS

    if exceeds_allowed_columns:
        original_columns = df.columns.tolist()
        trimmed_columns = df.columns.tolist()[:MAX_COLS]
        df = df[trimmed_columns]
        trimmed_columns = [
            col for col in original_columns if col not in trimmed_columns
        ]

    if exceeds_allowed_rows:
        n_rows = len(df.index)
        max_rows = MAX_ROWS
        df = df[:max_rows]
        trimmed_rows_count = n_rows - max_rows

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
            raise (
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
        session.console.print(table)
    else:
        session.console.print(df.to_string(col_space=0))

    if exceeds_allowed_columns:
        session.console.print(
            f"[yellow]\nAllowed number of columns exceeded ({session.settings.ALLOWED_NUMBER_OF_COLUMNS}).\n"
            f"The following columns were removed from the output: {', '.join(trimmed_columns)}.\n[/yellow]"
        )

    if exceeds_allowed_rows:
        session.console.print(
            f"[yellow]\nAllowed number of rows exceeded ({session.settings.ALLOWED_NUMBER_OF_ROWS}).\n"
            f"{trimmed_rows_count} rows were removed from the output.\n[/yellow]"
        )

    if exceeds_allowed_columns or exceeds_allowed_rows:
        session.console.print(
            "Use the `--export` flag to analyse the full output on a file."
        )


def check_non_negative(value) -> int:
    """Argparse type to check non negative int."""
    new_value = int(value)
    if new_value < 0:
        raise argparse.ArgumentTypeError(f"{value} is negative")
    return new_value


def check_positive(value) -> int:
    """Argparse type to check positive int."""
    new_value = int(value)
    if new_value <= 0:
        raise argparse.ArgumentTypeError(f"{value} is an invalid positive int value")
    return new_value


def validate_register_key(value: str) -> str:
    """Validate the register key to ensure it does not contain the reserved word 'OBB'."""
    if "OBB" in value:
        raise argparse.ArgumentTypeError(
            "The register key cannot contain the reserved word 'OBB'."
        )
    return str(value)


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


def get_flair() -> str:
    """Get a flair icon."""
    current_flair = str(session.settings.FLAIR)
    flair = AVAILABLE_FLAIRS.get(current_flair, current_flair)
    return flair


def get_dtime() -> str:
    """Get a datetime string."""
    dtime = ""
    if session.settings.USE_DATETIME and get_user_timezone_or_invalid() != "INVALID":
        dtime = datetime.now(timezone(get_user_timezone())).strftime("%Y %b %d, %H:%M")
    return dtime


def get_flair_and_username() -> str:
    """Get a flair icon and username."""
    flair = get_flair()
    if dtime := get_dtime():
        dtime = f"{dtime} "

    username = getattr(session.user.profile.hub_session, "username", "")
    if username:
        username = f"[{username}] "

    return f"{dtime}{username}{flair}"


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
    return user_tz in all_timezones


def get_user_timezone() -> str:
    """Get user timezone if it is a valid one.

    Returns
    -------
    str
        user timezone based on .env file
    """
    return session.settings.TIMEZONE


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
                session.console.print(
                    f"[red]Filename '{filename}' provided is not valid!\nPlease use one of the following file types:"
                    f"{','.join(valid_types)}[/red]\n"
                )
        return ",".join(valid_filenames)

    return check_filenames


def remove_timezone_from_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Remove timezone information from a dataframe.

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
    # check if this is done in a main context to avoid saving with openbb_cli
    if resolve_path.parts[-2] == "openbb_cli":
        path_cmd = f"{resolve_path.parts[-1]}"
    else:
        path_cmd = f"{resolve_path.parts[-2]}_{resolve_path.parts[-1]}"

    default_filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{path_cmd}_{func_name}"

    full_path = Path(session.user.preferences.export_directory) / default_filename

    return full_path


def ask_file_overwrite(file_path: Path) -> Tuple[bool, bool]:
    """Provide a prompt for overwriting existing files.

    Returns two values, the first is a boolean indicating if the file exists and the
    second is a boolean indicating if the user wants to overwrite the file.
    """
    if session.settings.FILE_OVERWRITE:
        return False, True
    if session.settings.TEST_MODE:
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
def save_to_excel(df, saved_path, sheet_name, start_row=0, index=True, header=True):
    """Save a Pandas DataFrame to an Excel file.

    Args:
        df: A Pandas DataFrame.
        saved_path: The path to the Excel file to save to.
        sheet_name: The name of the sheet to save the DataFrame to.
        start_row: The row number to start writing the DataFrame at.
        index: Whether to write the DataFrame index to the Excel file.
        header: Whether to write the DataFrame header to the Excel file.
    """
    overwrite_options = {
        "o": "replace",
        "a": "overlay",
        "n": "new",
    }

    if not saved_path.exists():
        with pd.ExcelWriter(saved_path, engine="openpyxl") as writer:
            df.to_excel(writer, sheet_name=sheet_name, index=index, header=header)

    else:
        with pd.ExcelFile(saved_path) as reader:
            overwrite_option = "n"
            if sheet_name in reader.sheet_names:
                overwrite_option = input(
                    "\nSheet already exists. Overwrite/Append/New? [o/a/n]: "
                ).lower()
                start_row = 0
                if overwrite_option == "a":
                    existing_df = pd.read_excel(saved_path, sheet_name=sheet_name)
                    start_row = existing_df.shape[0] + 1

            with pd.ExcelWriter(
                saved_path,
                mode="a",
                if_sheet_exists=overwrite_options[overwrite_option],
                engine="openpyxl",
            ) as writer:
                df.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    startrow=start_row,
                    index=index,
                    header=False if overwrite_option == "a" else header,
                )


# This is a false positive on pylint and being tracked in pylint #3060
# pylint: disable=abstract-class-instantiated
def export_data(
    export_type: str,
    dir_path: str,
    func_name: str,
    df: pd.DataFrame = pd.DataFrame(),
    sheet_name: Optional[str] = None,
    figure: Optional["OpenBBFigure"] = None,
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
                if ".OpenBB_openbb_cli" in saved_path.name:
                    saved_path = saved_path.with_name(
                        saved_path.name.replace(".OpenBB_openbb_cli", "OpenBBCLI")
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
                else:
                    save_to_excel(df, saved_path, sheet_name)

            elif saved_path.suffix in [".jpg", ".png"]:
                if figure is None:
                    session.console.print("No plot to export.")
                    continue
                figure.show(export_image=saved_path, margin=margin)
            else:
                session.console.print("Wrong export file specified.")
                continue

            if saved_path.exists():
                session.console.print(f"Saved file: {saved_path}")
            else:
                session.console.print(f"Failed to save file: {saved_path}")

        if figure is not None:
            figure._exported = True  # pylint: disable=protected-access


def system_clear():
    """Clear screen."""
    os.system("cls||clear")  # nosec # noqa: S605,S607


# Write an abstract helper to make requests from a url with potential headers and params
def request(
    url: str, method: str = "get", timeout: int = 0, **kwargs
) -> requests.Response:
    """Make requests from a url with potential headers and params.

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
    # We want to add a user agent to the request, so check if there are any headers
    # If there are headers, check if there is a user agent, if not add one.
    # Some requests seem to work only with a specific user agent, so we want to be able to override it.
    headers = kwargs.pop("headers", {})
    timeout = timeout or session.user.preferences.request_timeout

    if "User-Agent" not in headers:
        headers["User-Agent"] = get_user_agent()
    func = getattr(requests, method)
    return func(
        url,
        headers=headers,
        timeout=timeout,
        **kwargs,
    )


def parse_unknown_args_to_dict(unknown_args: Optional[List[str]]) -> Dict[str, str]:
    """Parse unknown arguments to a dictionary."""
    unknown_args_dict = {}
    if unknown_args:
        for idx, arg in enumerate(unknown_args):
            if arg.startswith("--"):
                if idx + 1 < len(unknown_args):
                    try:
                        unknown_args_dict[arg.replace("--", "")] = (
                            eval(  # noqa: S307, E501 pylint: disable=eval-used
                                unknown_args[idx + 1]
                            )
                        )
                    except Exception:
                        unknown_args_dict[arg] = unknown_args[idx + 1]
                else:
                    session.console.print(
                        f"Missing value for argument {arg}. Skipping this argument."
                    )
    return unknown_args_dict


def handle_obbject_display(
    obbject: OBBject,
    chart: bool = False,
    export: str = "",
    sheet_name: str = "",
    **kwargs,
):
    """Handle the display of an OBBject."""
    df: pd.DataFrame = pd.DataFrame()
    fig: Optional[OpenBBFigure] = None
    if chart:
        try:
            if obbject.chart:
                obbject.show(**kwargs)
            else:
                obbject.charting.to_chart(**kwargs)  # type: ignore
            if export:
                fig = obbject.chart.fig  # type: ignore
                df = obbject.to_dataframe()
        except Exception as e:
            session.console.print(f"Failed to display chart: {e}")
    elif session.settings.USE_INTERACTIVE_DF:
        obbject.charting.table()  # type: ignore
    else:
        df = obbject.to_dataframe()
        print_rich_table(
            df=df,
            show_index=True,
            title=obbject.extra.get("command", ""),
            export=bool(export),
        )
    if export and not df.empty:
        if sheet_name and isinstance(sheet_name, list):
            sheet_name = sheet_name[0]

        func_name = (
            obbject.extra.get("command", "")
            .replace("/", "_")
            .replace(" ", "_")
            .replace("--", "_")
        )
        export_data(
            export_type=",".join(export),
            dir_path=os.path.dirname(os.path.abspath(__file__)),
            func_name=func_name,
            df=df,
            sheet_name=sheet_name,
            figure=fig,
        )
    elif export and df.empty:
        session.console.print("[yellow]No data to export.[/yellow]")
