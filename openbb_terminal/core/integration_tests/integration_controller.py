#!/usr/bin/env python
"""Main Testing Module"""
__docformat__ = "numpy"

import argparse
import logging
import os
import re
import sys
import time
from functools import partial
from multiprocessing import cpu_count
from multiprocessing.pool import Pool
from pathlib import Path
from traceback import FrameSummary, extract_tb, format_list
from typing import Any, Callable, Dict, List, Optional, Tuple

from matplotlib import pyplot as plt

from openbb_terminal.core.config.paths import (
    MISCELLANEOUS_DIRECTORY,
    REPOSITORY_DIRECTORY,
)
from openbb_terminal.core.integration_tests.integration_test_coverage import (
    get_coverage_all_controllers,
)
from openbb_terminal.core.integration_tests.utils import (
    SECTION_LENGTH,
    to_section_title,
)
from openbb_terminal.core.models import (
    CredentialsModel,
    PreferencesModel,
    ProfileModel,
    SourcesModel,
    SystemModel,
    UserModel,
)
from openbb_terminal.core.session.current_system import (
    get_current_system,
    set_current_system,
    set_system_variable,
)
from openbb_terminal.core.session.current_user import get_current_user, set_current_user
from openbb_terminal.core.session.utils import load_dict_to_model
from openbb_terminal.helper_funcs import check_non_negative
from openbb_terminal.rich_config import console
from openbb_terminal.routine_functions import is_reset
from openbb_terminal.terminal_controller import (
    insert_start_slash,
    replace_dynamic,
    terminal,
)
from openbb_terminal.terminal_helper import suppress_stdout

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

SCRIPTS_DIRECTORY = MISCELLANEOUS_DIRECTORY / "integration_tests_scripts"


TEST_FILES = sorted(list(SCRIPTS_DIRECTORY.glob("**/*.openbb")))


def get_test_from_index(idx: str) -> Path:
    """Get the test from the index.

    Parameters
    ----------
    idx: int
        The index of the test

    Returns
    -------
    Path
        The path to the test
    """
    try:
        return TEST_FILES[int(idx)]
    except IndexError:
        console.print(
            f"[red]Index {idx} not found, must be between 0 and {len(TEST_FILES)-1}.[/red]"
        )
        raise


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
        if path.startswith(
            str(Path("openbb_terminal", "core", "integration_tests", "scripts"))
        ):
            script_path = REPOSITORY_DIRECTORY / path
        elif path.isnumeric():
            try:
                script_path = get_test_from_index(path)
            except IndexError:
                continue
        else:
            script_path = SCRIPTS_DIRECTORY / path

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
    final_list = sorted(valid_test_list - valid_skip_list)
    # Just display number of skips if the skip path is in valid_test_list
    len_skip = len(valid_test_list) - len(final_list)

    console.print(f"\n* Collected {len(valid_test_list)} script(s)...", style="bold")
    console.print(f"* Skipping {len_skip} script(s)...", style="bold")

    return final_list


def collect_test_files(path_list: List[str], skip_list: List[str]) -> List[Path]:
    """Collects the test files from the scripts directory

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
    console.print(f"Collecting scripts from: {SCRIPTS_DIRECTORY}\n")

    if not path_list:
        path_list = [""]
    return build_test_path_list(path_list, skip_list)


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
        file_cmds = (
            [f"export {export_folder}{' '.join(file_cmds)}"]
            if export_folder
            else [" ".join(file_cmds)]
        )

        if verbose:
            terminal(file_cmds, test_mode=True)
        else:
            with suppress_stdout():
                terminal(file_cmds, test_mode=True)


def run_test(
    file: Path,
    verbose: bool = False,
    special_arguments: Optional[Dict[str, str]] = None,
    user: Optional[Dict] = None,
    system: Optional[Dict] = None,
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
        The name of the file and the exception
    """

    if user:
        profile = user.get("profile", {})
        credentials = user.get("credentials", {})
        preferences = user.get("preferences", {})
        sources = user.get("sources", {})
        user_model = UserModel(
            profile=load_dict_to_model(profile, ProfileModel),
            credentials=load_dict_to_model(credentials, CredentialsModel),  # type: ignore
            preferences=load_dict_to_model(preferences, PreferencesModel),
            sources=load_dict_to_model(sources, SourcesModel),
        )
        set_current_user(user_model)

    if system:
        set_current_system(load_dict_to_model(system, SystemModel))

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
            "traceback": extract_tb(exc_traceback),
        }

    return file_short_name, exception


def display_test_progress(
    i: int, n: int, n_failures: int, file_short_name: str, verbose: bool = False
):
    """Displays the progress of the tests

    Parameters
    ----------
    i: int
        The index of the test
    n: int
        The total number of tests
    n_failures: int
        The number of failures
    file_short_name: str
        The name of the file
    verbose: bool
        Whether to run tests in verbose mode
    """

    style = "red" if n_failures else "green"
    if verbose:
        console.print("^", style=style)
        console.print("^", style=style)
        console.print("^", style=style)
    percentage = f"{(i + 1)/n:.0%}"
    percentage_with_spaces = "[" + (4 - len(percentage)) * " " + percentage + "]"
    spaces = SECTION_LENGTH - len(file_short_name) - len(percentage_with_spaces)
    console.print(
        f"{file_short_name}" + spaces * " " + f"{percentage_with_spaces}",
        style=style,
    )
    if verbose and i != n - 1:
        console.print("- " * int(SECTION_LENGTH / 2), style=style)


def run_test_files(
    test_files: List[Path],
    verbose: bool = False,
    special_arguments: Optional[Dict[str, str]] = None,
    subprocesses: Optional[int] = None,
    ordered: bool = False,
) -> Tuple[int, int, Dict[str, Dict[str, Any]], float]:
    """Runs the test scripts and returns the fails dictionary

    Parameters
    ----------
    test_files: List[Path]
        The list of files to test
    verbose: bool
        Whether or not to print the output of the scripts
    special_arguments: Optional[Dict[str, str]]
        The special arguments to use in the scripts
    subprocesses: Optional[int]
        The number of subprocesses to use to run the tests
    ordered: bool
        Multiprocessing is not ordered by default. Use this flag to run the tests in order

    Returns
    -------
    Tuple[int, int, Dict[str, Dict[str, Any]], float]
    """
    n_successes = 0
    n_failures = 0
    fails: Dict[str, Dict[str, Any]] = {}

    if test_files:
        n = len(test_files)

        start = time.time()

        if subprocesses == 0:
            console.print(
                f"* Running {n} script(s) sequentially...\n",
                style="bold",
            )
            for i, file in enumerate(test_files):
                file_short_name, exception = run_test(
                    file, verbose=verbose, special_arguments=special_arguments
                )
                if exception:
                    n_failures += 1
                    fails[file_short_name] = exception
                else:
                    n_successes += 1

                display_test_progress(i, n, n_failures, file_short_name, verbose)
        else:
            if not subprocesses:
                subprocesses = min(n, cpu_count())

            console.print(
                f"* Running {n} script(s) in {subprocesses} parallel subprocess(es)...\n",
                style="bold",
            )
            with Pool(processes=subprocesses) as pool:
                # Choosing chunksize: line 477 .../lib/python3.9/multiprocessing/pool.py
                chunksize, extra = divmod(n, subprocesses * 4)
                if extra:
                    chunksize += 1

                runner: Callable = pool.imap if ordered else pool.imap_unordered

                for i, result in enumerate(
                    runner(
                        partial(
                            run_test,
                            verbose=verbose,
                            special_arguments=special_arguments,
                            # We inject user and system as dict because pickle cannot
                            # serialize nested classes and the new process has to be
                            # aware of the current user and system, otherwise it will
                            # pick the defaults.
                            user=get_current_user().to_dict(),
                            system=get_current_system().to_dict(),
                        ),
                        test_files,
                        chunksize=chunksize,
                    )
                ):
                    file_short_name, exception = result
                    if exception:
                        n_failures += 1
                        fails[file_short_name] = exception
                    else:
                        n_successes += 1

                    display_test_progress(i, n, n_failures, file_short_name, verbose)

        end = time.time()
        seconds = end - start
    else:
        console.print("[yellow]* No tests to run.[/yellow]\n", style="bold")
        seconds = 0.0

    return n_successes, n_failures, fails, seconds


def display_failures(fails: Dict[str, Dict[str, Any]]):
    """Generates the failures section of the test report

    Parameters
    ----------
    fails: Dict[str, Dict[str, Any]]
        The dictionary with failure information
    """
    if fails:
        console.print("\n" + to_section_title("FAILURES"))
        for file, exception in fails.items():
            title = f"[bold red]{file}[/bold red]"
            console.print(to_section_title(title=title, char="-"), style="red")

            console.print("[bold red]\nTraceback:[/bold red]")
            formatted_tb = format_list(exception["traceback"])
            style = ""
            for i, line in enumerate(formatted_tb):
                if "openbb_terminal" not in line:
                    style = "rgb(128,128,128)"
                elif (
                    i == len(formatted_tb) - 1
                    or "openbb_terminal" not in formatted_tb[i + 1]
                ):
                    style = "yellow"

                console.print(line, end="", style=style)

            console.print(
                f"[bold red]Exception type:[/bold red] {exception['exception'].__class__.__name__}"
            )
            console.print(f"[bold red]Detail:[/bold red] {exception['exception']}")
            console.print("- " * int(SECTION_LENGTH / 2))


def display_summary(
    fails: Dict[str, Dict[str, Any]],
    n_successes: int,
    n_failures: int,
    seconds: float,
):
    """Generates the summary message

    Parameters
    ----------
    fails: Dict[str, Dict[str, Any]]
        The dictionary with failure information
    n_successes: int
        The number of successes
    n_failures: int
        The number of failures
    seconds: float
        The number of seconds it took to run the tests
    """

    if fails:
        console.print("\n" + to_section_title("Integration Test Summary"))

        for file, exception in fails.items():
            # Assuming the broken command is the last one called in the traceback
            broken_cmd = "unknown"
            frame: FrameSummary
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
    special_arguments: Optional[Dict[str, str]] = None,
    verbose: bool = False,
    subprocesses: Optional[int] = None,
    ordered: bool = False,
):
    """Run the integration test session

    Workflow:
    1. Collect test scripts
    2. Run test scripts
    3. Display failures traceback and detail, if any
    4. Display test summary

    Parameters
    ----------
    path_list: List[str]
        The list of paths to test
    skip_list: List[str]
        The list of paths to skip
    special_arguments: Optional[Dict[str, str]]
        The special arguments to use in the scripts
    verbose: bool
        Whether or not to print the output of the scripts
    subprocesses
        The number of subprocesses to use to run the tests
    ordered: bool
        Multiprocessing is not ordered by default. Use this flag to run the tests in order.
    """
    console.print(to_section_title("integration test session starts"), style="bold")
    test_files = collect_test_files(path_list, skip_list)
    n_successes, n_failures, fails, seconds = run_test_files(
        test_files, verbose, special_arguments, subprocesses, ordered
    )
    display_failures(fails)
    display_summary(fails, n_successes, n_failures, seconds)


def display_available_scripts(path_list: List[str], skip_list: List[str]):
    """Display the available scripts

    Parameters
    ----------
    path_list: List[str]
        The list of paths to test
    skip_list: List[str]
        The list of paths to skip
    """
    test_files = collect_test_files(path_list, skip_list)
    console.print("\nAvailable scripts:", style="yellow")
    for i, file in enumerate(test_files):
        console.print(f"{i}. " + str(file).replace(str(SCRIPTS_DIRECTORY), "")[1:])
    console.print("")


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
    parser.add_argument(
        "-v",
        "--verbose",
        help="Whether or not to print the output of the scripts."
        " To use it you must use just 1 subprocess.",
        dest="verbose",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "--subproc",
        help="The number of subprocesses to use to run the tests."
        " Default is the minimum between number of collected scripts and CPUs.",
        dest="subprocesses",
        type=check_non_negative,
        default=None,
    )
    parser.add_argument(
        "-l",
        "--list",
        help="List available scripts",
        dest="list_",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-o",
        "--ordered",
        help="Display results in test starting order.",
        dest="ordered",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-c",
        "--coverage",
        help="Display integration test coverage.",
        dest="coverage",
        action="store_true",
        default=False,
    )
    for arg in special_arguments_values:
        parser.add_argument(
            f"--{arg}",
            help=f"Change the default values for {arg}",
            dest=arg,
            type=str,
            default="",
        )

    ns_parser, unknown_args = parser.parse_known_args()

    if ns_parser.coverage:
        return get_coverage_all_controllers()

    # Allow the tester to send a path without the -p flag
    if not ns_parser.path and unknown_args:
        ns_parser.path = [u for u in unknown_args if u[0] != "-"]

    special_args_dict = {x: getattr(ns_parser, x) for x in special_arguments_values}

    if ns_parser.verbose and (
        ns_parser.subprocesses is None or ns_parser.subprocesses > 1
    ):
        console.print(
            "WARNING: verbose mode and multiprocessing are not compatible. "
            "Several processes running simultaneously will mix the output of the "
            "scripts in the screen. Consider running with --subproc 0.\n",
            style="yellow",
        )

    if ns_parser.list_:
        return display_available_scripts(ns_parser.path, ns_parser.skip)

    return run_test_session(
        path_list=ns_parser.path,
        skip_list=ns_parser.skip,
        special_arguments=special_args_dict,
        verbose=ns_parser.verbose,
        subprocesses=ns_parser.subprocesses,
        ordered=ns_parser.ordered,
    )


def main():
    """Run the integration tests."""

    if "-t" in sys.argv:
        sys.argv.remove("-t")
    if "--test" in sys.argv:
        sys.argv.remove("--test")

    # User
    current_user = get_current_user()
    current_user.preferences.ENABLE_EXIT_AUTO_HELP = False
    current_user.preferences.USE_PROMPT_TOOLKIT = False
    current_user.preferences.REMEMBER_CONTEXTS = False
    current_user.preferences.PLOT_ENABLE_PYWRY = False
    current_user.preferences.USE_INTERACTIVE_DF = False
    set_current_user(current_user)

    # System
    set_system_variable("HEADLESS", True)
    set_system_variable("DEBUG_MODE", True)
    set_system_variable("LOG_COLLECT", False)

    # Portfolio optimization - automatically close matplotlib figures
    plt.ion()

    # Run integration tests
    parse_args_and_run()


if __name__ == "__main__":
    main()
