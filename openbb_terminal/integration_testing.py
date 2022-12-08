#!/usr/bin/env python
"""Main Testing Module"""
__docformat__ = "numpy"

from datetime import datetime
from pathlib import Path
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
    return [Path(x) for x in test_files_unique]


def format_failures(fails: dict, output: bool) -> None:
    """Generates the message and csv from the fails dictionary

    Parameters
    -----------
    fails: dict
        The dictionary with failure information
    output: bool
        Whether or not to save output into a CSV file
    """
    if fails:
        console.print("\n[red]Failures:[/red]\n")
        for file, exception in fails.items():
            logger.error("%s: %s failed", file, exception["exception"])
        # Write results to CSV
        if output:
            timestamp = datetime.now().timestamp()
            stamp_str = str(timestamp).replace(".", "")
            whole_path = Path(REPOSITORY_DIRECTORY / "integration_test_summary")
            whole_path.mkdir(parents=True, exist_ok=True)
            output_path = f"{stamp_str}_tests.csv"
            with open(whole_path / output_path, "w") as file:  # type: ignore
                header = ["Script File", "Type", "Error", "Stacktrace"]
                writer = csv.DictWriter(file, fieldnames=header)  # type: ignore
                writer.writeheader()
                for file, exception in fails.items():
                    clean_type = (
                        str(type(exception["exception"]))
                        .replace("<class '", "")
                        .replace("'>", "")
                    )
                    writer.writerow(
                        {
                            "Script File": file,
                            "Type": clean_type,
                            "Error": exception["exception"],
                            "Stacktrace": exception["traceback"],
                        }
                    )

            console.print(f"CSV of errors saved to {whole_path / output_path}")


def run_test_list(
    path_list: List[str], verbose: bool, special_arguments: Dict[str, str], output: bool
):
    """Run commands in test mode."""
    os.environ["DEBUG_MODE"] = "true"

    if not path_list:
        path_list = [""]
    test_files = build_test_path_list(path_list)
    SUCCESSES = 0
    FAILURES = 0
    fails = {}
    length = len(test_files)
    i = 0
    console.print("[green]OpenBB Terminal Integrated Tests:\n[/green]")
    for file in test_files:
        console.print(f"{((i/length)*100):.1f}%  {file}")
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
            fails[file] = {
                "exception": e,
                "traceback": traceback.extract_tb(exc_traceback),
            }
            FAILURES += 1
        i += 1
    format_failures(fails, output)
    console.print(
        f"Summary: [green]Successes: {SUCCESSES}[/green] [red]Failures: {FAILURES}[/red]"
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
