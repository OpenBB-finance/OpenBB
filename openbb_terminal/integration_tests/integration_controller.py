#!/usr/bin/env python
"""Main Testing Module"""
__docformat__ = "numpy"

from functools import partial
from itertools import repeat
from multiprocessing.pool import Pool
from multiprocessing import cpu_count
from tqdm import tqdm
from pathlib import Path
import re
import time
from typing import Any, List, Dict, Optional, Tuple
import traceback
import argparse
import logging
import sys
import os

from openbb_terminal.rich_config import console
from openbb_terminal.core.config.paths import PACKAGE_DIRECTORY, REPOSITORY_DIRECTORY
from openbb_terminal.terminal_controller import (
    insert_start_slash,
    terminal,
    replace_dynamic,
)
from openbb_terminal.terminal_helper import is_reset, suppress_stdout

logger = logging.getLogger(__name__)
special_arguments_values = [
    "ticker",
    "currency",
    "crypto",
    "country",
    "repo",
    "crypto_vs",
    "crypto_full",
    "currency_vs",
]

SECTION_LENGTH = 90
STYLES = [
    "[bold]",
    "[/bold]",
    "[red]",
    "[/red]",
    "[green]",
    "[/green]",
    "[bold red]",
    "[/bold red]",
]
SCRIPTS_DIRECTORY = PACKAGE_DIRECTORY / "integration_tests" / "scripts"


def to_section_title(title: str, char: str = "=") -> str:
    """Format title for test mode.

    Parameters
    ----------
    title: str
        The title to format

    Returns
    -------
    str
        The formatted title
    """
    title = " " + title + " "

    len_styles = 0
    for style in STYLES:
        if style in title:
            len_styles += len(style)

    n = int((SECTION_LENGTH - len(title) + len_styles) / 2)
    formatted_title = char * n + title + char * n
    formatted_title = formatted_title + char * (
        SECTION_LENGTH - len(formatted_title) + len_styles
    )

    return formatted_title


def convert_list_to_test_files(path_list: List[str]) -> List[Path]:
    """Converts a list of paths to test to a list of Path objects.

    Parameters
    ----------
    path_list: List[str]
        The list of paths to convert

    Returns
    -------
    List[Path]
        The list of paths as Path objects
    """
    test_files = []

    for path in path_list:
        if "openbb_terminal/integration_tests/scripts" in path:
            directory = REPOSITORY_DIRECTORY
        else:
            directory = SCRIPTS_DIRECTORY

        script_path = directory / path

        if script_path.exists():
            chosen_path = script_path
        else:
            console.print(f"[red]Path not found: {script_path}[/red]\n")
            continue

        if chosen_path.is_file() and str(chosen_path).endswith(".openbb"):
            test_files.append(str(chosen_path))
        elif chosen_path.is_dir():
            all_files = os.walk(script_path)
            for root, _, files in all_files:
                for name in files:
                    if name.endswith(".openbb"):
                        path_obj = f"{root}/{name}"
                        test_files.append(path_obj)

    return [Path(x) for x in test_files]


def build_test_path_list(path_list: List[str], skip_list: List[str]) -> List[Path]:
    """Build the paths to use in test.

    Parameters
    ----------
    path_list: List[str]
        The list of paths to test
    skip_list: List[str]
        The list of paths to skip

    Returns
    -------
    List[Path]
        The list of paths to test
    """
    if path_list == "":
        console.print("Please send a path when using test mode")
        return []

    valid_test_list = set(convert_list_to_test_files(path_list))
    valid_skip_list = set(convert_list_to_test_files(skip_list))

    console.print(f"* Collected {len(valid_test_list)} script(s)...", style="bold")

    if any(x in valid_test_list for x in valid_skip_list):
        len_skip = len(valid_skip_list)
    else:
        len_skip = 0
    console.print(f"* Skipping {len_skip} script(s)...", style="bold")

    return sorted(valid_test_list - valid_skip_list)


def collect_test_files(path_list: List[str], skip_list: List[str]) -> List[Path]:
    """Collects the test files from the scripts directory

    Parameters
    ----------
    path_list: List[str]
        The list of paths to test
    skip_list: List[str]
        The list of paths to skip
    """

    console.print(f"Collecting scripts from: {SCRIPTS_DIRECTORY}\n")

    if not path_list:
        path_list = [""]
    test_files = build_test_path_list(path_list, skip_list)

    return test_files


def run_scripts(
    path: Path,
    verbose: bool = False,
    special_arguments: Optional[Dict[str, str]] = None,
):
    """Run given .openbb scripts.

    Parameters
    ----------
    path : str
        The location of the .openbb file
    verbose : bool
        Whether to run tests in verbose mode
    special_arguments: Optional[Dict[str, str]]
        Replace `${key=default}` with `value` for every key in the dictionary
    """
    if not path.exists():
        console.print(f"Path '{path}' doesn't exist.\n")

    with path.open() as fp:
        raw_lines = [x for x in fp if (not is_reset(x)) and ("#" not in x) and x]
        raw_lines = [
            raw_line.strip("\n") for raw_line in raw_lines if raw_line.strip("\n")
        ]

        # Handle new testing arguments:
        if special_arguments:
            lines = []
            for line in raw_lines:
                new_line = re.sub(
                    r"\${[^{]+=[^{]+}",
                    lambda x: replace_dynamic(x, special_arguments),  # type: ignore
                    line,
                )
                lines.append(new_line)

        else:
            lines = raw_lines

        if "exit" not in lines[-1]:
            lines.append("exit")

        export_folder = ""
        if "export" in lines[0]:
            export_folder = lines[0].split("export ")[1].rstrip()
            lines = lines[1:]

        simulate_argv = f"/{'/'.join([line.rstrip() for line in lines])}"
        file_cmds = simulate_argv.replace("//", "/home/").split()
        file_cmds = insert_start_slash(file_cmds) if file_cmds else file_cmds
        if export_folder:
            file_cmds = [f"export {export_folder}{' '.join(file_cmds)}"]
        else:
            file_cmds = [" ".join(file_cmds)]

        if verbose:
            terminal(file_cmds, test_mode=True)
        else:
            with suppress_stdout():
                terminal(file_cmds, test_mode=True)


def run_test(
    file: Path,
    verbose: bool = False,
    special_arguments: Optional[Dict[str, str]] = None,
) -> Tuple[str, Optional[Dict[str, Any]]]:
    """Run tests in a single process.

    Parameters
    ----------
    file: Path
        The path to the file to test
    verbose: bool
        Whether to run tests in verbose mode
    special_arguments: Optional[Dict[str, str]]
        Replace `${key=default}` with `value` for every key in the dictionary

    Returns
    -------
    Tuple[str, Optional[Dict[str, Any]]]
        The name of the file and the exception if any
    """

    file_short_name = str(file).replace(str(SCRIPTS_DIRECTORY), "")[1:]

    try:
        run_scripts(
            file,
            verbose=verbose,
            special_arguments=special_arguments,
        )
        exception = None
    except Exception as e:
        _, _, exc_traceback = sys.exc_info()
        exception = {
            "exception": e,
            "traceback": traceback.extract_tb(exc_traceback),
        }

    return file_short_name, exception


def display_test_progress(i, test_files, n_failures, file_short_name):
    percentage = f"{(i + 1)/len(test_files):.0%}"
    percentage_with_spaces = "[" + (4 - len(percentage)) * " " + percentage + "]"
    spaces = SECTION_LENGTH - len(file_short_name) - len(percentage_with_spaces)
    console.print(
        f"{file_short_name}" + spaces * " " + f"{percentage_with_spaces}",
        style="green" if not n_failures else "red",
    )


def run_test_files(
    test_files: list,
    verbose: bool = False,
    special_arguments: dict = None,
    processes: Optional[int] = None,
) -> Tuple[int, int, Dict[str, Dict[str, object]], float]:
    """Runs the test scripts and returns the fails dictionary

    Parameters
    -----------
    test_files: list
        The list of paths to test
    verbose: bool
        Whether or not to print the output of the scripts
    special_arguments: dict
        The special arguments to use in the scripts
    processes: Optional[int]
        The number of processes to use

    Returns
    -------
    fails: dict
        The dictionary with failure information
    """

    os.environ["DEBUG_MODE"] = "true"
    n_successes = 0
    n_failures = 0
    fails: Dict[str, Dict[str, object]] = {}

    if test_files:

        start = time.time()

        # If we run multiple scripts with just one process as terminal caches
        # imports and test scripts will not be independent.
        # For example a ticker loaded in a previous test might be available
        # in the next test, even if the test script doesn't import it.
        console.print(
            f"* Running script(s) in {processes} subprocess(es)...\n", style="bold"
        )
        with Pool(processes=processes) as pool:
            for i, result in enumerate(
                pool.imap(
                    partial(
                        run_test, verbose=verbose, special_arguments=special_arguments
                    ),
                    test_files,
                )
            ):
                file_short_name, exception = result
                if exception:
                    n_failures += 1
                    fails[file_short_name] = exception
                else:
                    n_successes += 1
                display_test_progress(i, test_files, n_failures, file_short_name)

        end = time.time()
        seconds = end - start
    else:
        console.print("[yellow]* No tests to run.[/yellow]\n", style="bold")
        seconds = 0.0

    return n_successes, n_failures, fails, seconds


def display_failures(fails: dict) -> None:
    """Generates the failures section of the test report

    Parameters
    -----------
    fails: dict
        The dictionary with failure information
    """
    if fails:
        console.print("\n" + to_section_title("FAILURES"))
        for file, exception in fails.items():
            title = f"[bold red]{file}[/bold red]"
            console.print(to_section_title(title=title, char="-"), style="red")

            console.print("[bold red]\nTraceback:[/bold red]")
            formatted_tb = traceback.format_list(exception["traceback"])
            style = ""
            for i, line in enumerate(formatted_tb):
                if "openbb_terminal" not in line:
                    style = "rgb(128,128,128)"
                elif i == len(formatted_tb) - 1:
                    style = "yellow"
                elif "openbb_terminal" not in formatted_tb[i + 1]:
                    style = "yellow"

                console.print(line, end="", style=style)

            console.print(
                f"[bold red]Exception type:[/bold red] {exception['exception'].__class__.__name__}"
            )
            console.print(f"[bold red]Detail:[/bold red] {exception['exception']}")
            console.print("- " * int(SECTION_LENGTH / 2))


def display_summary(
    fails: dict,
    n_successes: int,
    n_failures: int,
    seconds: float,
) -> None:
    """Generates the summary message

    Parameters
    ----------
    fails: dict
        The dictionary with failure information
    n_successes: int
        The number of successes
    n_failures: int
        The number of failures
    seconds: float
        The number of seconds it took to run the tests
    """

    if fails:
        console.print("\n" + to_section_title("integration test summary"))

        for file, exception in fails.items():

            # Assuming the broken command is the last one called in the traceback
            broken_cmd = "unknown"
            for _, frame in reversed(list(enumerate(exception["traceback"]))):
                if "_controller.py" in frame.filename and "call_" in frame.name:
                    broken_cmd = frame.name.split("_")[1]
                    break

            console.print(f"FAILED {file} -> command: {broken_cmd}")

    if n_successes or n_failures:
        failures = (
            f"[bold][red]{n_failures} failed, [/red][/bold]" if n_failures > 0 else ""
        )
        successes = f"[green]{n_successes} passed [/green]" if n_successes > 0 else ""

        m, s = divmod(seconds, 60)
        elapsed_time = ""
        if m > 0:
            elapsed_time += f"{m:.0f}m:"
        elapsed_time += f"{s:.2f}s"

        console.print(
            to_section_title(failures + successes + "in " + elapsed_time),
            style="green" if not n_failures else "red",
        )


def run_test_session(
    path_list: List[str],
    skip_list: List[str],
    special_arguments: Dict[str, str],
    verbose: bool = False,
    processes: Optional[int] = None,
) -> None:
    """Run the integration test session

    Workflow:
    1. Collect scripts
    2. Run tests
    3. Display failures
    4. Display summary

    Parameters
    ----------
    path_list: list
        The list of paths to test
    skip_list: list
        The list of paths to skip
    special_arguments: dict
        The special arguments to use in the scripts
    verbose: bool
        Whether or not to print the output of the scripts
    multiprocessing: bool
        Whether or not to run the tests in parallel
    """

    console.print(to_section_title("integration test session starts"), style="bold")

    test_files = collect_test_files(path_list, skip_list)
    n_successes, n_failures, fails, seconds = run_test_files(
        test_files, verbose, special_arguments, processes
    )
    display_failures(fails)
    display_summary(fails, n_successes, n_failures, seconds)


def parse_args_and_run():
    """Parse input arguments and run integration tests."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="testing",
        description="Integration tests for the OpenBB Terminal.",
    )
    parser.add_argument(
        "-p",
        "--path",
        help=(
            "The path to scripts or .openbb file to run."
            "Scripts must be run from 'openbb_terminal/integration_tests/scripts/'."
            " Usage examples for this flag:"
            " (1) `... -p test_keys_.openbb`,"
            " (2) `... -p forex/test_forex_load.openbb`,"
            " (3) `... -p test_keys_.openbb forex`,"
            " (4) `... -p test_keys_.openbb forex etf`."
            " If no path is provided, all scripts will be run."
        ),
        dest="path",
        nargs="+",
        default="",
        type=str,
    )
    parser.add_argument(
        "-s",
        "--skip",
        help=(
            "The path to scripts or .openbb file to run."
            "Scripts must be run from 'openbb_terminal/integration_tests/scripts/'."
            " Usage examples for this flag:"
            " (1) `... -s test_keys_.openbb`,"
            " (2) `... -s forex/test_forex_load.openbb`,"
            " (3) `... -s test_keys_.openbb forex`,"
            " (4) `... -s test_keys_.openbb forex etf`."
            " If no path is provided, all scripts will be run."
        ),
        dest="skip",
        nargs="+",
        default="",
        type=str,
    )
    # This is the list of special arguments a user can send
    for arg in special_arguments_values:
        parser.add_argument(
            f"--{arg}",
            help=f"Change the default values for {arg}",
            dest=arg,
            type=str,
            default="",
        )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Whether or not to print the output of the scripts",
        dest="verbose",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--processes",
        help="The number of processes to use to run the tests",
        dest="processes",
        type=int,
        default=cpu_count(),
    )
    ns_parser, unknown_args = parser.parse_known_args()

    # This is to allow the dev to send a path without the -p flag
    if not ns_parser.path and unknown_args:
        ns_parser.path = unknown_args

    special_args_dict = {x: getattr(ns_parser, x) for x in special_arguments_values}

    if ns_parser.verbose and ns_parser.processes > 1:
        console.print(
            "WARNING: verbose mode and multiprocessing are not compatible. The output of the scripts would be mixed up. Setting processes to 1...\n",
            style="yellow",
        )
        ns_parser.processes = 1

    run_test_session(
        path_list=ns_parser.path,
        skip_list=ns_parser.skip,
        special_arguments=special_args_dict,
        verbose=ns_parser.verbose,
        processes=ns_parser.processes,
    )


def main():
    """Run the integration tests."""

    if "-t" in sys.argv:
        sys.argv.remove("-t")
    if "--test" in sys.argv:
        sys.argv.remove("--test")

    parse_args_and_run()


if __name__ == "__main__":
    main()
