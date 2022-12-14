#!/usr/bin/env python
"""Main Testing Module"""
__docformat__ = "numpy"

from datetime import datetime
from pathlib import Path
import time
from typing import List, Dict
import traceback
import argparse
import logging
import csv
import sys
import os

from openbb_terminal.rich_config import console
from openbb_terminal.core.config.paths import (
    MISCELLANEOUS_DIRECTORY,
    REPOSITORY_DIRECTORY,
)
from openbb_terminal.terminal_controller import run_scripts

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


def build_test_path_list(path_list: List[str]) -> List[Path]:
    """Build the paths to use in test mode."""
    if path_list == "":
        console.print("Please send a path when using test mode")
        return []

    test_files = []

    for path in path_list:
        script_path = MISCELLANEOUS_DIRECTORY / "scripts" / path

        if script_path.exists():
            chosen_path = script_path
        else:
            console.print(f"\n[red]Can't find the file: {script_path}[/red]\n")
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
    return final_path_list


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
        console.print("\n" + to_title("FAILURES"))
        for file, exception in fails.items():
            title = f"[bold]{file}[/bold]"
            console.print(to_title(title=title, char="-"), style="red")

            for frame in exception["traceback"]:
                summary = repr(frame).replace("FrameSummary file", "File")
                internal = "openbb_terminal" in summary
                console.print(
                    f"{summary}",
                    style="rgb(128,128,128)" if not internal else "",
                )
                console.print(
                    f"[yellow]>>[/yellow] {frame.filename}:{frame.lineno}",
                    style="rgb(128,128,128)" if not internal else "",
                )

            console.print(
                f"[bold red]\nException type:[/bold red] {exception['exception'].__class__.__name__}"
            )
            console.print(f"[bold red]Detail:[/bold red] {exception['exception']}")
            console.print("- " * int(LENGTH / 2))


def to_title(title: str, char: str = "=") -> str:
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

    STYLES = [
        "[bold]",
        "[/bold]",
        "[red]",
        "[/red]",
        "[green]",
        "[/green]",
    ]
    len_styles = 0
    for style in STYLES:
        if style in title:
            len_styles += len(style)

    n = int((LENGTH - len(title) + len_styles) / 2)
    formatted_title = char * n + title + char * n
    formatted_title = char * (LENGTH - len(formatted_title)) + formatted_title
    return formatted_title


def run_test_list(
    path_list: List[str], verbose: bool, special_arguments: Dict[str, str], output: bool
):
    """Run commands in test mode."""

    # Test header
    console.print(to_title("integration test session starts"), style="bold")

    os.environ["DEBUG_MODE"] = "true"

    if not path_list:
        path_list = [""]
    test_files = build_test_path_list(path_list)
    length = len(test_files)
    scripts_location = MISCELLANEOUS_DIRECTORY / "scripts"
    console.print(f"Collecting scripts from: {scripts_location}\n")
    console.print(f"collected {length} scripts\n", style="bold")

    SUCCESSES = 0
    FAILURES = 0
    fails = {}
    start = time.time()
    for i, file in enumerate(test_files):

        file_short_name = str(file).replace(str(MISCELLANEOUS_DIRECTORY), "")
        file_short_name = file_short_name[1:]

        try:
            run_scripts(
                file,
                test_mode=True,
                verbose=verbose,
                special_arguments=special_arguments,
                output=output,
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
        percentage = f"{(i + 1)/length:.0%}"
        percentage_with_spaces = "[" + (4 - len(percentage)) * " " + percentage + "]"
        spacing = LENGTH - len(file_short_name) - len(percentage_with_spaces)
        console.print(
            f"{file_short_name}" + spacing * " " + f"{percentage_with_spaces}",
            style="green" if not FAILURES else "red",
        )
    end = time.time()

    # Test failures
    display_failures(fails)

    # Test summary
    if fails:
        console.print("\n" + to_title("integration test summary"))

        for file, exception in fails.items():
            exception_name = exception["exception"].__class__.__name__
            console.print(f"FAILED {file}::{exception_name}")

    failures = f"[bold][red]{FAILURES} failed, [/red][/bold]" if FAILURES > 0 else ""
    successes = f"[green]{SUCCESSES} passed[/green]" if SUCCESSES > 0 else ""
    seconds = f"{(end - start):.2f} s"
    console.print(
        to_title(failures + successes + " in " + seconds),
        style="green" if not FAILURES else "red",
    )


def parse_args_and_run():
    """Parse input arguments and run integration tests."""
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="testing",
        description="Integration tests for the OpenBB Terminal.",
    )
    parser.add_argument(
        "-f",
        "--file",
        help=(
            "The path or .openbb file to run. Starts at "
            "OpenBBTerminal/openbb_terminal/miscellaneous/scripts"
        ),
        dest="path",
        nargs="+",
        default="",
        type=str,
    )
    parser.add_argument(
        "-t",
        "--test",
        action="store_true",
        help=(
            "Run the terminal in testing mode. Also run this option and '-h'"
            " to see testing argument options."
        ),
    )
    parser.add_argument(
        "--no-output",
        action="store_true",
        default=False,
        dest="no_output",
        help="Blocks creation of CSV files and logs",
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

    ns_parser, _ = parser.parse_known_args()
    special_args_dict = {x: getattr(ns_parser, x) for x in special_arguments_values}
    run_test_list(
        path_list=ns_parser.path,
        verbose=ns_parser.verbose,
        special_arguments=special_args_dict,
        output=not ns_parser.no_output,
    )


if __name__ == "__main__":
    parse_args_and_run()
