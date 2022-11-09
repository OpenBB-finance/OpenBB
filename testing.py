#!/usr/bin/env python
"""Main Testing Module"""
__docformat__ = "numpy"

from datetime import datetime
from pathlib import Path
from typing import List
import argparse
import logging
import csv
import sys
import os

from openbb_terminal.rich_config import console
from openbb_terminal.core.config.paths import MISCELLANEOUS_DIRECTORY
from openbb_terminal.terminal_controller import run_scripts

logger = logging.getLogger(__name__)


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
            files = os.walk(script_path)
            for root, _, files in files:
                for name in files:
                    if name.endswith(".openbb"):
                        path_obj = f"{root}/{name}"
                        test_files.append(path_obj)

    test_files_unique = set(test_files)
    return [Path(x) for x in test_files_unique]


def run_test_list(path_list: List[str], verbose: bool):
    """Run commands in test mode."""
    os.environ["DEBUG_MODE"] = "true"

    if not path_list:
        path_list = [""]
    test_files = build_test_path_list(path_list)
    print(test_files)
    SUCCESSES = 0
    FAILURES = 0
    fails = {}
    length = len(test_files)
    i = 0
    console.print("[green]OpenBB Terminal Integrated Tests:\n[/green]")
    for file in test_files:
        console.print(f"{((i/length)*100):.1f}%  {file}")
        try:
            run_scripts(file, test_mode=True, verbose=verbose)
            SUCCESSES += 1
        except Exception as e:
            fails[file] = e
            FAILURES += 1
        i += 1
    if fails:
        console.print("\n[red]Failures:[/red]\n")
        for file, exception in fails.items():
            logger.error("%s: %s failed", file, exception)
        # Write results to CSV
        timestamp = datetime.now().timestamp()
        output_path = f"{timestamp}_tests.csv"
        with open(output_path, "w") as file:  # type: ignore
            header = ["File", "Error"]
            writer = csv.DictWriter(file, fieldnames=header)  # type: ignore
            writer.writeheader()
            for file, exception in fails.items():
                writer.writerow({"File": file, "Error": exception})

        console.print(f"CSV of errors saved to {output_path}")

    console.print(
        f"Summary: [green]Successes: {SUCCESSES}[/green] [red]Failures: {FAILURES}[/red]"
    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="testing",
        description="Integration tests for the OpenBB Terminal.",
    )
    parser.add_argument(
        "--file",
        help="The path or .openbb file to run. Starts at OpenBBTermina/openbb_terminal/miscellaneous/scripts",
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
    if sys.argv[1:] and "-" not in sys.argv[1][0]:
        sys.argv.insert(1, "--file")
    ns_parser, _ = parser.parse_known_args()
    run_test_list(path_list=ns_parser.path, verbose=ns_parser.verbose)
