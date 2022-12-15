#!/usr/bin/env python
"""Main Testing Module"""
__docformat__ = "numpy"

from pathlib import Path
import re
import time
from typing import List, Dict, Optional, Tuple
import traceback
import argparse
import logging
import sys
import os

from openbb_terminal.rich_config import console
from openbb_terminal.core.config.paths import PACKAGE_DIRECTORY
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

LENGTH = 90
GRAY = "rgb(128,128,128)"
YELLOW = "yellow"
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
SCRIPTS_FOLDER_PATH = PACKAGE_DIRECTORY / "integration_tests" / "scripts"


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

    n = int((LENGTH - len(title) + len_styles) / 2)
    formatted_title = char * n + title + char * n
    formatted_title = formatted_title + char * (
        LENGTH - len(formatted_title) + len_styles
    )

    return formatted_title


def build_test_path_list(path_list: List[str]) -> List[Path]:
    """Build the paths to use in test mode.

    Parameters
    ----------
    path_list: List[str]
        The list of paths to test

    Returns
    -------
    List[Path]
        The list of paths to test
    """
    if path_list == "":
        console.print("Please send a path when using test mode")
        return []

    test_files = []

    for path in path_list:
        script_path = SCRIPTS_FOLDER_PATH / path

        if script_path.exists():
            chosen_path = script_path
        else:
            console.print(f"\n[red]Can't find: {script_path}[/red]\n")
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

    test_files_unique = set(test_files)
    final_path_list = [Path(x) for x in test_files_unique]
    return sorted(final_path_list)


def collect_test_files(path_list: List[str]) -> List[Path]:
    """Collects the test files from the scripts directory

    Parameters
    ----------
    path_list: List[str]
        The list of paths to test
    """

    if not path_list:
        path_list = [""]
    test_files = build_test_path_list(path_list)
    console.print(f"Collecting scripts from: {SCRIPTS_FOLDER_PATH}\n")
    console.print(f"Collected {len(test_files)} script(s)\n", style="bold")

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


def run_test_files(
    test_files: list, verbose: bool, special_arguments: dict
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

    Returns
    -------
    fails: dict
        The dictionary with failure information
    """

    start = time.time()

    if test_files:
        console.print("Running script(s)...\n", style="bold")

    os.environ["DEBUG_MODE"] = "true"
    SUCCESSES = 0
    FAILURES = 0
    fails = {}
    for i, file in enumerate(test_files):

        file_short_name = str(file).replace(str(SCRIPTS_FOLDER_PATH), "")[1:]

        try:
            run_scripts(
                file,
                verbose=verbose,
                special_arguments=special_arguments,
            )
            SUCCESSES += 1
        except Exception as e:
            _, _, exc_traceback = sys.exc_info()
            fails[file_short_name] = {
                "exception": e,
                "traceback": traceback.extract_tb(exc_traceback),
            }
            FAILURES += 1

        # Test performance
        percentage = f"{(i + 1)/len(test_files):.0%}"
        percentage_with_spaces = "[" + (4 - len(percentage)) * " " + percentage + "]"
        spaces = LENGTH - len(file_short_name) - len(percentage_with_spaces)
        console.print(
            f"{file_short_name}" + spaces * " " + f"{percentage_with_spaces}",
            style="green" if not FAILURES else "red",
        )

    end = time.time()
    seconds = end - start

    return SUCCESSES, FAILURES, fails, seconds


def display_failures(fails: dict) -> None:
    """Generates the message and csv from the fails dictionary

    Parameters
    -----------
    fails: dict
        The dictionary with failure information
    output: bool
        Whether or not to save output into a CSV file
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
                    style = GRAY
                elif i == len(formatted_tb) - 1:
                    style = YELLOW
                elif "openbb_terminal" not in formatted_tb[i + 1]:
                    style = YELLOW

                console.print(line, end="", style=style)

            console.print(
                f"[bold red]Exception type:[/bold red] {exception['exception'].__class__.__name__}"
            )
            console.print(f"[bold red]Detail:[/bold red] {exception['exception']}")
            console.print("- " * int(LENGTH / 2))


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

            broken_cmd = "unknown"
            for _, frame in reversed(list(enumerate(exception["traceback"]))):
                if "_controller.py" in frame.filename and "call_" in frame.name:
                    broken_cmd = frame.name.split("_")[1]
                    break

            console.print(f"FAILED {file} -> command: {broken_cmd}")

    failures = (
        f"[bold][red]{n_failures} failed, [/red][/bold]" if n_failures > 0 else ""
    )
    successes = f"[green]{n_successes} passed[/green]" if n_successes > 0 else ""
    console.print(
        to_section_title(failures + successes + " in " + f"{(seconds):.2f}s"),
        style="green" if not n_failures else "red",
    )


def run_test_list(
    path_list: List[str], verbose: bool, special_arguments: Dict[str, str]
) -> None:
    """Run commands in test mode.

    Workflow:
    1. Collect scripts
    2. Run tests
    3. Display failures
    4. Display summary

    Parameters
    ----------
    path_list: list
        The list of paths to test
    verbose: bool
        Whether or not to print the output of the scripts
    special_arguments: dict
        The special arguments to use in the scripts
    """

    console.print(to_section_title("integration test session starts"), style="bold")

    test_files = collect_test_files(path_list)

    SUCCESSES, FAILURES, fails, seconds = run_test_files(
        test_files, verbose, special_arguments
    )
    display_failures(fails)
    display_summary(fails, SUCCESSES, FAILURES, seconds)


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
        "-v",
        "--verbose",
        help="Enable verbose output for debugging",
        dest="verbose",
        action="store_true",
        default=False,
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

    ns_parser, unknown_args = parser.parse_known_args()

    # This is to allow the dev to send a path without the -p flag
    if not ns_parser.path and unknown_args:
        ns_parser.path = unknown_args

    special_args_dict = {x: getattr(ns_parser, x) for x in special_arguments_values}

    run_test_list(
        path_list=ns_parser.path,
        verbose=ns_parser.verbose,
        special_arguments=special_args_dict,
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
