"""Utils."""

import argparse
import ast
import os
import random
import re
import shutil
import sqlite3
import sys
from contextlib import contextmanager
from datetime import (
    datetime,
)
from pathlib import Path
from typing import TYPE_CHECKING, Optional
from zoneinfo import ZoneInfo, available_timezones

import numpy as np
import pandas as pd
import requests
from openbb_core.app.model.obbject import OBBject

all_timezones = available_timezones()
from rich.table import Table

from openbb_cli.config.constants import AVAILABLE_FLAIRS, ENV_FILE_SETTINGS
from openbb_cli.session import Session

if TYPE_CHECKING:
    from openbb_charting.core.openbb_figure import (  # ty: ignore[unresolved-import]
        OpenBBFigure,
    )


class SQLiteTable:
    """Lazy-loading wrapper for SQLite tables.

    Stores connection info and loads data only when accessed.
    """

    def __init__(self, db_path: str, table_name: str, row_count: int = 0):
        """Initialize SQLite table wrapper.

        Args:
            db_path: Path to SQLite database file
            table_name: Name of the table
            row_count: Number of rows (from metadata)
        """
        self.db_path = db_path
        self.table_name = table_name
        self.row_count = row_count
        self._cached_df: pd.DataFrame | None = None

    @property
    def _quoted_name(self) -> str:
        """Return the table name quoted for safe SQL interpolation."""
        return '"' + self.table_name.replace('"', '""') + '"'

    def to_dataframe(self, use_cache: bool = True) -> pd.DataFrame:
        """Load table data from SQLite database.

        Args:
            use_cache: If True, return cached DataFrame if available

        Returns
        -------
            DataFrame containing table data
        """
        if use_cache and self._cached_df is not None:
            return self._cached_df

        conn = sqlite3.connect(self.db_path)
        try:
            sql = f"SELECT * FROM {self._quoted_name}"  # noqa: S608
            df = pd.read_sql_query(sql, conn)
            if use_cache:
                self._cached_df = df
            return df
        finally:
            conn.close()

    def get_schema(self) -> list[tuple]:
        """Get table schema (column names and types).

        Returns
        -------
            List of (column_name, type, notnull, default, pk) tuples
        """
        conn = sqlite3.connect(self.db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({self._quoted_name})")
            return cursor.fetchall()
        finally:
            conn.close()

    def query(self, where: str = "", limit: int | None = None) -> pd.DataFrame:
        """Execute SQL query with optional filters.

        Args:
            where: SQL WHERE clause (without WHERE keyword)
            limit: Maximum number of rows to return

        Returns
        -------
            DataFrame with query results
        """
        sql = f"SELECT * FROM {self._quoted_name}"  # noqa: S608
        if where:
            sql += f" WHERE {where}"
        if limit:
            sql += f" LIMIT {limit}"

        conn = sqlite3.connect(self.db_path)
        try:
            return pd.read_sql_query(sql, conn)
        finally:
            conn.close()


def extract_dataframe(obbject) -> pd.DataFrame:
    """Extract DataFrame from OBBject without using to_dataframe().

    This function manually extracts results from OBBject to have full control
    over the conversion process and avoid built-in assumptions.

    Args:
        obbject: OBBject instance or other data

    Returns
    -------
        DataFrame extracted from results
    """
    results = (
        obbject.model_dump().get("results")
        if hasattr(obbject, "model_dump")
        else obbject
    )

    if results is None:
        return pd.DataFrame()
    elif isinstance(results, SQLiteTable):
        return results.to_dataframe()
    elif isinstance(results, pd.DataFrame):
        return results
    elif isinstance(results, list):
        return pd.DataFrame(results)
    elif isinstance(results, dict):
        return pd.DataFrame([results])
    else:
        return pd.DataFrame({"value": [results]})


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
    try:
        if os.path.isfile(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        return True
    except Exception:
        session.console.print(
            f"\n[bold red]Failed to remove {path}\nPlease delete this manually![/bold red]"
        )
        return False


def print_goodbye():
    """Print a goodbye message when quitting the terminal."""
    text = """
[param]Thank you for using the OpenBB Platform CLI and being part of this journey.[/param]

To stay tuned, sign up for our newsletter: [cmds]https://openbb.co/newsletter.[/]

Please feel free to check out our other products:

[bold]OpenBB Workspace[/]:    [cmds]https://openbb.co[/cmds]
[bold]ODP Desktop Application:[/]      [cmds]https://docs.openbb.co/odp/[/cmds]
[bold]ODP Python Package:[/]     [cmds]https://docs.openbb.co/platform[/cmds]
"""
    session.console.print(text)


def bootup():
    """Bootup the cli."""
    if sys.platform == "win32":  # pragma: no cover
        os.system("")  # noqa: S605, S607

    try:
        if os.name == "nt":  # pragma: no cover — Windows-only stdin/stdout reconfigure
            sys.stdin.reconfigure(encoding="utf-8")
            sys.stdout.reconfigure(encoding="utf-8")
    except Exception as e:  # pragma: no cover — bootup catch-all defensive path
        session.console.print(e, "\n")


def welcome_message():
    """Print the welcome message.

    Prints first welcome message, help and a notification if updates are available.
    """
    session.console.print(
        f"\nWelcome to OpenBB Platform CLI v{session.settings.VERSION}"
    )


def reset(queue: list[str] | None = None):
    """Reset the CLI.

    Allows for checking code without quitting.
    """
    session.console.print("resetting...")
    debug = session.settings.DEBUG_MODE
    dev = session.settings.DEV_BACKEND

    try:
        for module in list(sys.modules.keys()):
            parts = module.split(".")
            if parts[0] == "openbb_cli":
                del sys.modules[module]

        queue_list = ["/".join(queue) if len(queue) > 0 else ""]  # ty: ignore[invalid-argument-type, no-matching-overload]

        from openbb_cli.controllers.cli_controller import main

        main(debug, dev, queue_list, module="")

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


def parse_and_split_input(an_input: str, custom_filters: list) -> list[str]:
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
    if an_input and an_input == "/":
        an_input = "home"

    file_flag = r"(\ -f |\ --file )"
    up_to = r".*?"
    known_extensions = (
        r"(\.(xlsx|csv|xls|tsv|json|yaml|ini|openbb|ipynb|db|sqlite|sqlite3))"
    )
    optional_args = r"(?:\ [^/]+)*?"
    unix_path_arg_exp = f"({file_flag}{up_to}{known_extensions}{optional_args})"

    custom_filter = ""
    for exp in custom_filters:
        if exp is not None:
            custom_filter += f"|{exp}"
            del exp

    slash_filter_exp = f"({unix_path_arg_exp}){custom_filter}"

    filter_input = True
    placeholders: dict[str, str] = {}
    while filter_input:
        match = re.search(pattern=slash_filter_exp, string=an_input)
        if match is not None:
            placeholder = f"{{placeholder{len(placeholders) + 1}}}"
            placeholders[placeholder] = an_input[match.span()[0] : match.span()[1]]  # noqa:E203
            an_input = (
                an_input[: match.span()[0]] + placeholder + an_input[match.span()[1] :]
            )  # noqa:E203
        else:
            filter_input = False

    commands = an_input.split("/") if "timezone" not in an_input else [an_input]

    for command_num, command in enumerate(commands):
        if command == commands[-1] == "":
            return list(filter(None, commands))
        matching_placeholders = [tag for tag in placeholders if tag in command]
        if len(matching_placeholders) > 0:
            for tag in matching_placeholders:
                commands[command_num] = command.replace(tag, placeholders[tag])
    return list(filter(None, commands))


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

    if len(values) == 1:
        if float(values[0]) > 0:
            return f"[green]{value}[/green]"

        if float(values[0]) < 0:
            return f"[red]{value}[/red]"

        if float(values[0]) == 0:
            return f"[yellow]{value}[/yellow]"

    return f"{value}"


def print_rich_table(  # noqa: PLR0912
    df: pd.DataFrame,
    show_index: bool = False,
    title: str = "",
    index_name: str = "",
    headers: list[str] | pd.Index | None = None,
    floatfmt: str | list[str] = ".2f",
    show_header: bool = True,
    automatic_coloring: bool = False,
    columns_to_auto_color: list[str] | None = None,
    rows_to_auto_color: list[str] | None = None,
    export: bool = False,
    limit: int | None = 1000,
    columns_keep_types: list[str] | None = None,
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

    df = df.copy()

    show_index = not isinstance(df.index, pd.RangeIndex) and show_index
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

    def _get_headers(_headers: list[str] | pd.Index) -> list[str]:
        """Check if headers are valid and return them."""
        output = _headers
        if isinstance(_headers, pd.Index):
            output = list(_headers)
        if len(output) != len(df.columns):
            raise ValueError("Length of headers does not match length of DataFrame.")
        return output  # ty: ignore[invalid-return-type]

    if session.settings.USE_INTERACTIVE_DF and session.backend is not None:
        df_outgoing = df.copy()
        if headers is not None:
            df_outgoing.columns = _get_headers(headers)

        if show_index and index_name not in df_outgoing.columns:
            df_outgoing.index.name = index_name or "Index"
            df_outgoing = df_outgoing.reset_index()

        for col in df_outgoing.columns:
            if col == "":
                df_outgoing = df_outgoing.rename(columns={col: "  "})

        try:
            session.backend.send_table(
                df_table=df_outgoing,
                title=title,
                theme=session.user.preferences.table_style,
            )
            return
        except Exception:  # noqa: S110
            pass

    df = df.copy() if not limit else df.copy().iloc[:limit]
    if automatic_coloring:
        if columns_to_auto_color:
            for col in columns_to_auto_color:
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: return_colored_value(str(x)))
        if rows_to_auto_color:
            for row in rows_to_auto_color:
                if row in df.index:
                    df.loc[row] = df.loc[row].apply(
                        lambda x: return_colored_value(str(x))
                    )

        if columns_to_auto_color is None and rows_to_auto_color is None:
            df = df.map(lambda x: return_colored_value(str(x)))

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


def get_user_data_directory() -> Path:
    """Get the OpenBBUserData directory path."""
    return Path(session.user.preferences.data_directory)


def get_data_files_for_completion() -> list[str]:
    """Get list of data files in OpenBBUserData for tab completion.

    Returns list of file paths relative to OpenBBUserData directory.
    Includes CSV, JSON, and Excel files.
    """
    try:
        user_data_dir = get_user_data_directory()
        if not user_data_dir.exists():
            return []

        files = []
        for file_path in user_data_dir.rglob("*"):
            if file_path.is_file() and file_path.suffix.lower() in [
                ".csv",
                ".json",
                ".xlsx",
                ".xls",
                ".db",
                ".sqlite",
                ".sqlite3",
            ]:
                rel_path = file_path.relative_to(user_data_dir)
                files.append(str(rel_path).replace("\\", "/"))

        return sorted(files)
    except Exception:
        return []


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

    return random.choice(user_agent_strings)  # noqa: S311


def get_flair() -> str:
    """Get a flair icon."""
    current_flair = str(session.settings.FLAIR)
    flair = AVAILABLE_FLAIRS.get(current_flair, current_flair)
    return flair


def get_dtime() -> str:
    """Get a datetime string."""
    dtime = ""
    if session.settings.USE_DATETIME and get_user_timezone_or_invalid() != "INVALID":
        dtime = datetime.now(ZoneInfo(get_user_timezone())).strftime("%Y %b %d, %H:%M")
    return dtime


def get_flair_and_username() -> str:
    """Get a flair icon and username."""
    flair = get_flair()
    if dtime := get_dtime():
        dtime = f"{dtime} "

    return f"{dtime}{flair}"


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


def check_file_type_saved(valid_types: list[str] | None = None):
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
        -------
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

    if (
        df.index.dtype.kind == "M"
        and hasattr(df.index.dtype, "tz")
        and df.index.dtype.tz is not None
    ):
        index_is_date = True

    for col, dtype in df.dtypes.items():
        if dtype.kind == "M" and hasattr(df.index.dtype, "tz") and dtype.tz is not None:
            date_cols.append(col)

    for col in date_cols:
        df[col] = df[col].dt.date

    if index_is_date:
        index_name = df.index.name
        df.index = df.index.date  # ty: ignore[unresolved-attribute]
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
    resolve_path = Path(dir_path).resolve()
    if resolve_path.parts[-2] == "openbb_cli":
        path_cmd = f"{resolve_path.parts[-1]}"
    else:
        path_cmd = f"{resolve_path.parts[-2]}_{resolve_path.parts[-1]}"

    default_filename = f"{now.strftime('%Y%m%d_%H%M%S')}_{path_cmd}_{func_name}"

    full_path = Path(session.user.preferences.export_directory) / default_filename

    return full_path


def ask_file_overwrite(file_path: Path) -> tuple[bool, bool]:
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
            return True, True
        return True, False
    return False, True


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
                if_sheet_exists=overwrite_options[overwrite_option],  # ty: ignore[invalid-argument-type]
                engine="openpyxl",
            ) as writer:
                df.to_excel(
                    writer,
                    sheet_name=sheet_name,
                    startrow=start_row,
                    index=index,
                    header=False if overwrite_option == "a" else header,
                )


def export_data(  # noqa: PLR0912
    export_type: str,
    dir_path: str,
    func_name: str,
    df: pd.DataFrame = pd.DataFrame(),
    sheet_name: str | None = None,
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
            if "." in exp_type:
                saved_path = saved_path.with_name(exp_type)
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
            elif saved_path.suffix in [".db", ".sqlite", ".sqlite3"]:
                import sqlite3

                table_name = sheet_name if sheet_name else "data"

                conn = sqlite3.connect(saved_path)
                try:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                        (table_name,),
                    )
                    table_exists = cursor.fetchone() is not None

                    if table_exists:
                        choice = input(
                            f"\nTable '{table_name}' exists. Overwrite/Append/New? [o/a/n]: "
                        ).lower()
                        if choice == "o":
                            df.to_sql(
                                table_name, conn, if_exists="replace", index=False
                            )
                        elif choice == "a":
                            df.to_sql(table_name, conn, if_exists="append", index=False)
                        elif choice == "n":
                            i = 1
                            new_name = f"{table_name}_{i}"
                            while True:
                                cursor.execute(
                                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                                    (new_name,),
                                )
                                if cursor.fetchone() is None:
                                    break
                                i += 1
                                new_name = f"{table_name}_{i}"
                            df.to_sql(new_name, conn, if_exists="fail", index=False)
                            table_name = new_name
                        else:
                            session.console.print("Invalid choice. Skipping.")
                            continue
                    else:
                        df.to_sql(table_name, conn, if_exists="fail", index=False)
                finally:
                    conn.close()
            else:
                session.console.print("Wrong export file specified.")
                continue

            if saved_path.exists():
                session.console.print(f"Saved file: {saved_path}")
            else:
                session.console.print(f"Failed to save file: {saved_path}")

        if figure is not None:
            figure._exported = True


def system_clear():
    """Clear screen."""
    os.system("cls||clear")  # noqa: S605, S607


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


def parse_unknown_args_to_dict(unknown_args: list[str] | None) -> dict[str, str]:
    """Parse unknown arguments to a dictionary."""
    unknown_args_dict = {}
    if unknown_args:
        for idx, arg in enumerate(unknown_args):
            if arg.startswith("--"):
                if idx + 1 < len(unknown_args):
                    try:
                        unknown_args_dict[arg.replace("--", "")] = ast.literal_eval(
                            unknown_args[idx + 1]
                        )
                    except (ValueError, SyntaxError):
                        unknown_args_dict[arg.replace("--", "")] = unknown_args[idx + 1]
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
    fig: OpenBBFigure | None = None

    if isinstance(getattr(obbject, "results", None), SQLiteTable):
        sqlite_tbl: SQLiteTable = obbject.results  # ty: ignore[invalid-assignment]
        obbject.results = sqlite_tbl.to_dataframe()

    if chart:
        try:
            if obbject.chart:
                obbject.show(**kwargs)
            else:
                obbject.charting.to_chart(**kwargs)  # ty: ignore[unresolved-attribute]
            if export:
                fig = obbject.chart.fig  # ty: ignore[unresolved-attribute]
                df = extract_dataframe(obbject)
        except Exception as e:
            session.console.print(f"Failed to display chart: {e}")
    elif session.settings.USE_INTERACTIVE_DF:
        # ``charting`` is an accessor ``openbb-charting`` registers
        # lazily on ``OBBject``. When it isn't installed (spec-mode
        # CLI without the charting extension) the attribute access
        # raises ``AttributeError`` from pydantic — fall back to the
        # plain DataFrame display so ``results -i N`` still surfaces
        # the rows.
        try:
            obbject.charting.table()  # ty: ignore[unresolved-attribute]
        except AttributeError:
            df = extract_dataframe(obbject)
            session.output_adapter.display(
                data=df,
                title=obbject.extra.get("command", ""),
                export=bool(export),
                chart=False,
            )
    else:
        df = extract_dataframe(obbject)
        session.output_adapter.display(
            data=df,
            title=obbject.extra.get("command", ""),
            export=bool(export),
            chart=False,
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
