#!/usr/bin/env python
"""Main Terminal Module"""
__docformat__ = "numpy"

import sys
import os
import difflib
import logging
import argparse
import platform
from typing import List
import pytz


from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal.rich_config import console
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    get_flair,
    get_user_timezone_or_invalid,
    replace_user_timezone,
)

from gamestonk_terminal.loggers import setup_logging
from gamestonk_terminal.menu import session

from gamestonk_terminal.terminal_helper import (
    about_us,
    bootup,
    welcome_message,
    print_goodbye,
    reset,
    update_terminal,
    suppress_stdout,
    is_reset,
)

# pylint: disable=too-many-public-methods,import-outside-toplevel

logger = logging.getLogger(__name__)


class TerminalController(BaseController):
    """Terminal Controller class"""

    CHOICES_COMMANDS = [
        "update",
        "about",
        "keys",
        "settings",
        "tz",
    ]
    CHOICES_MENUS = [
        "stocks",
        "economy",
        "crypto",
        "portfolio",
        "forex",
        "etf",
        "jupyter",
        "funds",
        "alternative",
        "custom",
    ]

    PATH = "/"

    all_timezones = pytz.all_timezones

    def __init__(self, jobs_cmds: List[str] = None):
        """Constructor"""
        super().__init__(jobs_cmds)

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: None for c in self.controller_choices}
            choices["tz"] = {c: None for c in self.all_timezones}
            self.completer = NestedCompleter.from_nested_dict(choices)

        self.queue: List[str] = list()

        if jobs_cmds:
            self.queue = " ".join(jobs_cmds).split("/")

        self.update_succcess = False

    def print_help(self):
        """Print help"""
        console.print(
            text=f"""
[info]Multiple jobs queue (where each '/' denotes a new command).[/info]
    E.g. '/stocks $ disc/ugs -n 3/../load tsla/candle'

[info]If you want to jump from crypto/ta to stocks you can use an absolute path that starts with a slash (/).[/info]
    E.g. '/crypto/ta $ /stocks'

[info]The previous logic also holds for when launching the terminal.[/info]
    E.g. '$ python terminal.py /stocks/disc/ugs -n 3/../load tsla/candle'

[info]The main commands you should be aware when navigating through the terminal are:[/info][cmds]
    cls             clear the screen
    help / h / ?    help menu
    quit / q / ..   quit this menu and go one menu above
    exit            exit the terminal
    reset / r       reset the terminal and reload configs from the current location
    resources       only available on main contexts (not sub-menus)

    about           about us
    update          update terminal automatically
    tz              set different timezone[/cmds][menu]
>   settings        set feature flags and style charts
>   keys            set API keys and check their validity[/menu]

[param]Timezone:[/param] {get_user_timezone_or_invalid()}
[menu]
>   stocks
>   crypto
>   etf
>   economy
>   forex
>   funds
>   alternative
>   portfolio
>   jupyter
>   custom[/menu]
    """,
            menu="Home",
        )

    def call_update(self, _):
        """Process update command"""
        self.update_succcess = not update_terminal()

    def call_keys(self, _):
        """Process keys command"""
        from gamestonk_terminal.keys_controller import KeysController

        self.queue = self.load_class(KeysController, self.queue)

    def call_settings(self, _):
        """Process settings command"""
        from gamestonk_terminal.settings_controller import SettingsController

        self.queue = self.load_class(SettingsController, self.queue)

    def call_about(self, _):
        """Process about command"""
        about_us()

    def call_stocks(self, _):
        """Process stocks command"""
        from gamestonk_terminal.stocks.stocks_controller import StocksController

        self.queue = self.load_class(StocksController, self.queue)

    def call_crypto(self, _):
        """Process crypto command"""
        from gamestonk_terminal.cryptocurrency.crypto_controller import CryptoController

        self.queue = self.load_class(CryptoController, self.queue)

    def call_economy(self, _):
        """Process economy command"""
        from gamestonk_terminal.economy.economy_controller import EconomyController

        self.queue = self.load_class(EconomyController, self.queue)

    def call_etf(self, _):
        """Process etf command"""
        from gamestonk_terminal.etf.etf_controller import ETFController

        self.queue = self.load_class(ETFController, self.queue)

    def call_funds(self, _):
        """Process etf command"""
        from gamestonk_terminal.mutual_funds.mutual_fund_controller import (
            FundController,
        )

        self.queue = self.load_class(FundController, self.queue)

    def call_forex(self, _):
        """Process forex command"""
        from gamestonk_terminal.forex.forex_controller import ForexController

        self.queue = self.load_class(ForexController, self.queue)

    def call_jupyter(self, _):
        """Process jupyter command"""
        from gamestonk_terminal.jupyter.jupyter_controller import JupyterController

        self.queue = self.load_class(JupyterController, self.queue)

    def call_alternative(self, _):
        """Process alternative command"""
        from gamestonk_terminal.alternative.alt_controller import (
            AlternativeDataController,
        )

        self.queue = self.load_class(AlternativeDataController, self.queue)

    def call_custom(self, _):
        """Process custom command"""
        from gamestonk_terminal.custom.custom_controller import (
            CustomDataController,
        )

        self.queue = CustomDataController(self.queue).menu()

    def call_portfolio(self, _):
        """Process portfolio command"""
        from gamestonk_terminal.portfolio.portfolio_controller import (
            PortfolioController,
        )

        self.queue = self.load_class(PortfolioController, self.queue)

    def call_tz(self, other_args: List[str]):
        """Process tz command"""
        other_args.append(self.queue[0])
        self.queue = self.queue[1:]
        replace_user_timezone("/".join(other_args))


def terminal(jobs_cmds: List[str] = None):
    """Terminal Menu"""
    setup_logging()
    logger.info("START")
    logger.info("Python: %s", platform.python_version())
    logger.info("OS: %s", platform.system())

    if jobs_cmds is not None and jobs_cmds:
        logger.info("INPUT: %s", "/".join(jobs_cmds))

    ret_code = 1
    t_controller = TerminalController(jobs_cmds)
    an_input = ""

    bootup()
    if not jobs_cmds:
        welcome_message()
        t_controller.print_help()

    while ret_code:
        if gtff.ENABLE_QUICK_EXIT:
            console.print("Quick exit enabled")
            break

        # There is a command in the queue
        if t_controller.queue and len(t_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if t_controller.queue[0] in ("q", "..", "quit"):
                print_goodbye()
                break

            if gtff.ENABLE_EXIT_AUTO_HELP and len(t_controller.queue) > 1:
                t_controller.queue = t_controller.queue[1:]

            # Consume 1 element from the queue
            an_input = t_controller.queue[0]
            t_controller.queue = t_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in t_controller.CHOICES_COMMANDS:
                console.print(f"{get_flair()} / $ {an_input}")

        # Get input command from user
        else:
            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} / $ ",
                        completer=t_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    print_goodbye()
                    break
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} / $ ")

        try:
            # Process the input command
            t_controller.queue = t_controller.switch(an_input)
            if an_input in ("q", "quit", "..", "exit"):
                print_goodbye()
                break

            # Check if the user wants to reset application
            if an_input in ("r", "reset") or t_controller.update_succcess:
                ret_code = reset(t_controller.queue if t_controller.queue else [])
                if ret_code != 0:
                    print_goodbye()
                    break

        except SystemExit:
            console.print(
                f"\nThe command '{an_input}' doesn't exist on the / menu", end=""
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                t_controller.controller_choices,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                    if candidate_input == an_input:
                        an_input = ""
                        t_controller.queue = []
                        console.print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                console.print(f" Replacing by '{an_input}'.")
                t_controller.queue.insert(0, an_input)
            else:
                console.print("\n")


def insert_start_slash(cmds: List[str]) -> List[str]:
    if not cmds[0].startswith("/"):
        cmds[0] = f"/{cmds[0]}"
    if cmds[0].startswith("/home"):
        cmds[0] = f"/{cmds[0][5:]}"
    return cmds


def run_scripts(path: str, test_mode: bool = False, verbose: bool = False):
    """Runs a given .gst scripts

    Parameters
    ----------
    path : str
        The location of the .gst file
    test_mode : bool
        Whether the terminal is in test mode
    verbose : bool
        Whether to run tests in verbose mode
    """
    if os.path.isfile(path):
        with open(path) as fp:
            lines = [x for x in fp if not test_mode or not is_reset(x)]

            if test_mode and "exit" not in lines[-1]:
                lines.append("exit")

            simulate_argv = f"/{'/'.join([line.rstrip() for line in lines])}"
            file_cmds = simulate_argv.replace("//", "/home/").split()

            file_cmds = insert_start_slash(file_cmds) if file_cmds else file_cmds
            if not test_mode:
                terminal(file_cmds)
                # TODO: Add way to track how many commands are tested
            else:
                if verbose:
                    terminal(file_cmds)
                else:
                    with suppress_stdout():
                        terminal(file_cmds)
    else:
        console.print(f"File '{path}' doesn't exist. Launching base terminal.\n")
        if not test_mode:
            terminal()


def main(debug: bool, test: bool, filtert: str, paths: List[str], verbose: bool):
    """
    Runs the terminal with various options

    Parameters
    ----------
    debug : bool
        Whether to run the terminal in debug mode
    test : bool
        Whether to run the terminal in integrated test mode
    filtert : str
        Filter test files with given string in name
    paths : List[str]
        The paths to run for scripts or to test
    verbose : bool
        Whether to show output from tests
    """

    if test:
        os.environ["DEBUG_MODE"] = "true"

        if paths == []:
            console.print("Please send a path when using test mode")
            return
        test_files = []
        for path in paths:
            if "gst" in path:
                file = os.path.join(os.path.abspath(os.path.dirname(__file__)), path)
                test_files.append(file)
            else:
                folder = os.path.join(os.path.abspath(os.path.dirname(__file__)), path)
                files = [
                    f"{folder}/{name}"
                    for name in os.listdir(folder)
                    if os.path.isfile(os.path.join(folder, name))
                    and name.endswith(".gst")
                    and (filtert in f"{folder}/{name}")
                ]
                test_files += files
        test_files.sort()
        SUCCESSES = 0
        FAILURES = 0
        fails = {}
        length = len(test_files)
        i = 0
        console.print("[green]Gamestonk Terminal Integrated Tests:\n[/green]")
        for file in test_files:
            file = file.replace("//", "/")
            file_name = file[file.rfind("GamestonkTerminal") :].replace("\\", "/")
            console.print(f"{file_name}  {((i/length)*100):.1f}%")
            try:
                if not os.path.isfile(file):
                    raise ValueError("Given file does not exist")
                run_scripts(file, test_mode=True, verbose=verbose)
                SUCCESSES += 1
            except Exception as e:
                fails[file] = e
                FAILURES += 1
            i += 1
        if fails:
            console.print("\n[red]Failures:[/red]\n")
            for key, value in fails.items():
                file_name = key[key.rfind("GamestonkTerminal") :].replace("\\", "/")
                console.print(f"{file_name}: {value}\n")
        console.print(
            f"Summary: [green]Successes: {SUCCESSES}[/green] [red]Failures: {FAILURES}[/red]"
        )
    else:
        if debug:
            os.environ["DEBUG_MODE"] = "true"
        if isinstance(paths, list) and paths[0].endswith(".gst"):
            run_scripts(paths[0])
        elif paths:
            argv_cmds = list([" ".join(paths).replace(" /", "/home/")])
            argv_cmds = insert_start_slash(argv_cmds) if argv_cmds else argv_cmds
            terminal(argv_cmds)
        else:
            terminal()


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        prog="terminal",
        description="The gamestonk terminal.",
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        default=False,
        help="Runs the terminal in debug mode.",
    )
    parser.add_argument(
        "-p",
        "--path",
        help="The path or .gst file to run.",
        dest="path",
        nargs="+",
        default="",
        type=str,
    )
    parser.add_argument(
        "-t",
        "--test",
        dest="test",
        action="store_true",
        default=False,
        help="Whether to run in test mode.",
    )
    parser.add_argument(
        "-f",
        "--filter",
        help="Send a keyword to filter in file name",
        dest="filtert",
        default="",
        type=str,
    )
    parser.add_argument(
        "-v", "--verbose", dest="verbose", action="store_true", default=False
    )

    if sys.argv[1:] and "-" not in sys.argv[1][0]:
        sys.argv.insert(1, "-p")
    ns_parser = parser.parse_args()
    main(
        ns_parser.debug,
        ns_parser.test,
        ns_parser.filtert,
        ns_parser.path,
        ns_parser.verbose,
    )
