#!/usr/bin/env python
"""Main Terminal Module"""
__docformat__ = "numpy"

import os
import difflib
import logging
import sys
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
    check_api_keys,
    print_goodbye,
    reset,
    update_terminal,
)

# pylint: disable=too-many-public-methods,import-outside-toplevel

logger = logging.getLogger(__name__)

DEBUG_MODE = False


class TerminalController(BaseController):
    """Terminal Controller class"""

    CHOICES_COMMANDS = [
        "update",
        "about",
        "keys",
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
            # close the eyes if the user forgets the initial `/`
            if len(jobs_cmds) > 0:
                if jobs_cmds[0][0] != "/":
                    jobs_cmds[0] = f"/{jobs_cmds[0]}"

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
    keys            check for status of API keys
    tz              set different timezone[/cmds]

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
        check_api_keys()

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

    logger.info("Terminal started")

    ret_code = 1
    t_controller = TerminalController(jobs_cmds)
    an_input = ""

    if not jobs_cmds:
        bootup()

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
            # Display help menu when entering on this menu from a level above
            if not an_input:
                t_controller.print_help()

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
                ret_code = reset(
                    t_controller.queue if len(t_controller.queue) > 0 else []
                )
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


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if "--debug" in sys.argv:
            os.environ["DEBUG_MODE"] = "true"
            sys.argv.remove("--debug")
        else:
            os.environ["DEBUG_MODE"] = "false"
        if len(sys.argv) > 1 and ".gst" in sys.argv[1]:
            if os.path.isfile(sys.argv[1]):
                with open(sys.argv[1]) as fp:
                    simulate_argv = f"/{'/'.join([line.rstrip() for line in fp])}"
                    terminal(simulate_argv.replace("//", "/home/").split())
            else:
                console.print(
                    f"The file '{sys.argv[1]}' doesn't exist. Launching terminal without any configuration.\n"
                )
                terminal()
        else:
            terminal(sys.argv[1:])
    else:
        os.environ["DEBUG_MODE"] = "false"
        terminal()
