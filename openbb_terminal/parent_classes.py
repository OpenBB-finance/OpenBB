"""Parent Classes"""
__docformat__ = "numpy"

# pylint: disable= C0301

from abc import ABCMeta, abstractmethod
import argparse
import re
import os
import difflib
import logging

from typing import Union, List, Dict, Any
from datetime import datetime, timedelta

from prompt_toolkit.completion import NestedCompleter
from prompt_toolkit.styles import Style
from prompt_toolkit.formatted_text import HTML
from rich.markdown import Markdown
import pandas as pd
import numpy as np

from openbb_terminal.decorators import log_start_end

from openbb_terminal.menu import session
from openbb_terminal import feature_flags as obbff
from openbb_terminal.helper_funcs import (
    system_clear,
    get_flair,
    valid_date,
    parse_known_args_and_warn,
    set_command_location,
    prefill_form,
    support_message,
)
from openbb_terminal.config_terminal import theme
from openbb_terminal.rich_config import console
from openbb_terminal.stocks import stocks_helper
from openbb_terminal.cryptocurrency import cryptocurrency_helpers

logger = logging.getLogger(__name__)


controllers: Dict[str, Any] = {}

CRYPTO_SOURCES = {
    "bin": "Binance",
    "cg": "CoinGecko",
    "cp": "CoinPaprika",
    "cb": "Coinbase",
    "yf": "YahooFinance",
}

SUPPORT_TYPE = ["bug", "suggestion", "question", "generic"]


class BaseController(metaclass=ABCMeta):

    CHOICES_COMMON = [
        "cls",
        "home",
        "h",
        "?",
        "help",
        "q",
        "quit",
        "..",
        "exit",
        "r",
        "reset",
        "support",
    ]

    CHOICES_COMMANDS: List[str] = []
    CHOICES_MENUS: List[str] = []
    SUPPORT_CHOICES: Dict = {}
    COMMAND_SEPARATOR = "/"
    KEYS_MENU = "keys" + COMMAND_SEPARATOR
    TRY_RELOAD = False
    PATH: str = ""
    FILE_PATH: str = ""

    def __init__(self, queue: List[str] = None) -> None:
        """
        This is the base class for any controller in the codebase.
        It's used to simplify the creation of menus.

        queue: List[str]
            The current queue of jobs to process separated by "/"
            E.g. /stocks/load gme/dps/sidtc/../exit
        """
        self.check_path()
        self.path = [x for x in self.PATH.split("/") if x != ""]

        self.queue = queue if (queue and self.PATH != "/") else list()

        controller_choices = self.CHOICES_COMMANDS + self.CHOICES_MENUS
        if controller_choices:
            self.controller_choices = controller_choices + self.CHOICES_COMMON
        else:
            self.controller_choices = self.CHOICES_COMMON

        self.completer: Union[None, NestedCompleter] = None

        self.parser = argparse.ArgumentParser(
            add_help=False, prog=self.path[-1] if self.PATH != "/" else "terminal"
        )

        self.parser.add_argument("cmd", choices=self.controller_choices)

        theme.applyMPLstyle()

        # Terminal-wide support command auto-completion

        # Remove common choices from list of support commands
        self.support_commands = [
            c for c in self.controller_choices if c not in self.CHOICES_COMMON
        ]

        support_choices: dict = {c: {} for c in self.controller_choices}

        support_choices = {c: None for c in (["generic"] + self.support_commands)}

        support_choices["--command"] = {
            c: None for c in (["generic"] + self.support_commands)
        }

        support_choices["-c"] = {c: None for c in (["generic"] + self.support_commands)}

        support_choices["--type"] = {c: None for c in (SUPPORT_TYPE)}

        self.SUPPORT_CHOICES = support_choices

    def check_path(self) -> None:
        path = self.PATH
        if path[0] != "/":
            raise ValueError("Path must begin with a '/' character.")
        if path[-1] != "/":
            raise ValueError("Path must end with a '/' character.")
        if not re.match("^[a-z/]*$", path):
            raise ValueError(
                "Path must only contain lowercase letters and '/' characters."
            )

    def load_class(self, class_ins, *args, **kwargs):
        """Checks for an existing instance of the controller before creating a new one"""
        self.save_class()
        arguments = len(args) + len(kwargs)
        if class_ins.PATH in controllers and arguments == 1 and obbff.REMEMBER_CONTEXTS:
            old_class = controllers[class_ins.PATH]
            old_class.queue = self.queue
            return old_class.menu()
        return class_ins(*args, **kwargs).menu()

    def save_class(self) -> None:
        """Saves the current instance of the class to be loaded later"""
        if obbff.REMEMBER_CONTEXTS:
            controllers[self.PATH] = self

    def custom_reset(self) -> List[str]:
        """This will be replaced by any children with custom_reset functions"""
        return []

    @abstractmethod
    def print_help(self) -> None:
        raise NotImplementedError("Must override print_help.")

    def contains_keys(self, string_to_check: str) -> bool:
        if self.KEYS_MENU in string_to_check or self.KEYS_MENU in self.PATH:
            return True
        return False

    def log_queue(self) -> None:
        joined_queue = self.COMMAND_SEPARATOR.join(self.queue)
        if self.queue and not self.contains_keys(joined_queue):
            logger.info(
                "QUEUE: {'path': '%s', 'queue': '%s'}",
                self.PATH,
                joined_queue,
            )

    def log_cmd_and_queue(
        self, known_cmd: str, other_args_str: str, the_input: str
    ) -> None:
        if not self.contains_keys(the_input):
            logger.info(
                "CMD: {'path': '%s', 'known_cmd': '%s', 'other_args': '%s', 'input': '%s'}",
                self.PATH,
                known_cmd,
                other_args_str,
                the_input,
            )
        if the_input not in self.KEYS_MENU:
            self.log_queue()

    @log_start_end(log=logger)
    def switch(self, an_input: str) -> List[str]:
        """Process and dispatch input

        Returns
        -------
        List[str]
            List of commands in the queue to execute
        """

        # Empty command
        if not an_input:
            pass
        #    console.print("")

        # Navigation slash is being used first split commands
        elif "/" in an_input:
            actions = an_input.split("/")

            # Absolute path is specified
            if not actions[0]:
                actions[0] = "home"

            # Add all instructions to the queue
            for cmd in actions[::-1]:
                if cmd:
                    self.queue.insert(0, cmd)

        # Single command fed, process
        else:
            (known_args, other_args) = self.parser.parse_known_args(an_input.split())

            # Redirect commands to their correct functions
            if known_args.cmd:
                if known_args.cmd in ("..", "q"):
                    known_args.cmd = "quit"
                elif known_args.cmd in ("?", "h"):
                    known_args.cmd = "help"
                elif known_args.cmd == "r":
                    known_args.cmd = "reset"

            set_command_location(f"{self.PATH}{known_args.cmd}")
            self.log_cmd_and_queue(known_args.cmd, ";".join(other_args), an_input)

            # This is what mutes portfolio issue
            getattr(
                self,
                "call_" + known_args.cmd,
                lambda _: "Command not recognized!",
            )(other_args)

        self.log_queue()

        return self.queue

    @log_start_end(log=logger)
    def call_cls(self, _) -> None:
        """Process cls command"""
        system_clear()

    @log_start_end(log=logger)
    def call_home(self, _) -> None:
        """Process home command"""
        self.save_class()
        console.print("")
        for _ in range(self.PATH.count("/") - 1):
            self.queue.insert(0, "quit")

    @log_start_end(log=logger)
    def call_help(self, _) -> None:
        """Process help command"""
        self.print_help()

    @log_start_end(log=logger)
    def call_quit(self, _) -> None:
        """Process quit menu command"""
        self.save_class()
        console.print("")
        self.queue.insert(0, "quit")

    @log_start_end(log=logger)
    def call_exit(self, _) -> None:
        # Not sure how to handle controller loading here
        """Process exit terminal command"""
        console.print("")
        for _ in range(self.PATH.count("/")):
            self.queue.insert(0, "quit")

    @log_start_end(log=logger)
    def call_reset(self, _) -> None:
        """Process reset command. If you would like to have customization in the
        reset process define a method `custom_reset` in the child class.
        """
        if self.PATH != "/":
            if self.custom_reset():
                self.queue = self.custom_reset() + self.queue
            else:
                for val in self.path[::-1]:
                    self.queue.insert(0, val)
            self.queue.insert(0, "reset")
            for _ in range(len(self.path)):
                self.queue.insert(0, "quit")

    @log_start_end(log=logger)
    def call_resources(self, _) -> None:
        """Process resources command"""
        if os.path.isfile(self.FILE_PATH):
            with open(self.FILE_PATH) as f:
                console.print(Markdown(f.read()))
            console.print("")
        else:
            console.print("No resources available.\n")

    @log_start_end(log=logger)
    def call_support(self, other_args: List[str]) -> None:
        """Process support command"""

        self.save_class()
        console.print("")

        path_split = [x for x in self.PATH.split("/") if x != ""]
        main_menu = path_split[0] if len(path_split) else "home"

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="support",
            description="Submit your support request",
        )

        parser.add_argument(
            "-c",
            "--command",
            action="store",
            dest="command",
            required="-h" not in other_args,
            choices=["generic"] + self.support_commands,
            help="Command that needs support",
        )

        parser.add_argument(
            "--msg",
            "-m",
            action="store",
            type=support_message,
            nargs="+",
            dest="msg",
            required=False,
            default="",
            help="Message to send. Enclose it with double quotes",
        )

        parser.add_argument(
            "--type",
            "-t",
            action="store",
            dest="type",
            required=False,
            choices=SUPPORT_TYPE,
            default="generic",
            help="Support ticket type",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            prefill_form(
                ticket_type=ns_parser.type,
                menu=main_menu,
                command=ns_parser.command,
                message=" ".join(ns_parser.msg),
                path=self.PATH,
            )

    def menu(self, custom_path_menu_above: str = ""):
        an_input = "HELP_ME"

        while True:
            # There is a command in the queue
            if self.queue and len(self.queue) > 0:
                # If the command is quitting the menu we want to return in here
                if self.queue[0] in ("q", "..", "quit"):
                    # Go back to the root in order to go to the right directory because
                    # there was a jump between indirect menus
                    if custom_path_menu_above:
                        self.queue.insert(1, custom_path_menu_above)

                    if len(self.queue) > 1:
                        return self.queue[1:]

                    if obbff.ENABLE_EXIT_AUTO_HELP:
                        return ["help"]
                    return []

                # Consume 1 element from the queue
                an_input = self.queue[0]
                self.queue = self.queue[1:]

                # Print location because this was an instruction and we want user to know the action
                if (
                    an_input
                    and an_input != "home"
                    and an_input.split(" ")[0] in self.controller_choices
                ):
                    console.print(f"{get_flair()} {self.PATH} $ {an_input}")

            # Get input command from user
            else:
                # Display help menu when entering on this menu from a level above
                if an_input == "HELP_ME":
                    self.print_help()

                try:
                    # Get input from user using auto-completion
                    if session and obbff.USE_PROMPT_TOOLKIT:
                        if bool(obbff.TOOLBAR_HINT):
                            an_input = session.prompt(
                                f"{get_flair()} {self.PATH} $ ",
                                completer=self.completer,
                                search_ignore_case=True,
                                bottom_toolbar=HTML(
                                    '<style bg="ansiblack" fg="ansiwhite">[h]</style> help menu    '
                                    '<style bg="ansiblack" fg="ansiwhite">[q]</style> return to previous menu    '
                                    '<style bg="ansiblack" fg="ansiwhite">[e]</style> exit terminal    '
                                    '<style bg="ansiblack" fg="ansiwhite">[cmd -h]</style>'
                                    ' see usage and available options         <style bg="#0000EE">'
                                    f"https://openbb-finance.github.io/OpenBBTerminal/terminal{self.PATH}</style>"
                                ),
                                style=Style.from_dict(
                                    {
                                        "bottom-toolbar": "#ffffff bg:#333333",
                                    }
                                ),
                            )
                        else:
                            an_input = session.prompt(
                                f"{get_flair()} {self.PATH} $ ",
                                completer=self.completer,
                                search_ignore_case=True,
                            )
                    # Get input from user without auto-completion
                    else:
                        an_input = input(f"{get_flair()} {self.PATH} $ ")
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"

            try:
                # Process the input command
                self.queue = self.switch(an_input)

            except SystemExit:
                if not self.contains_keys(an_input):
                    logger.exception(
                        "The command '%s' doesn't exist on the %s menu.",
                        an_input,
                        self.PATH,
                    )
                console.print(
                    f"\nThe command '{an_input}' doesn't exist on the {self.PATH} menu.\n",
                    end="",
                )
                similar_cmd = difflib.get_close_matches(
                    an_input.split(" ")[0] if " " in an_input else an_input,
                    self.controller_choices,
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
                            self.queue = []
                            console.print("\n")
                            continue
                        an_input = candidate_input
                    else:
                        an_input = similar_cmd[0]
                    if not self.contains_keys(an_input):
                        logger.warning("Replacing by %s", an_input)
                    console.print(f" Replacing by '{an_input}'.")
                    self.queue.insert(0, an_input)
                else:
                    if self.TRY_RELOAD and obbff.RETRY_WITH_LOAD:
                        console.print(f"Trying `load {an_input}`")
                        self.queue.insert(0, "load " + an_input)
                    console.print("")


class StockBaseController(BaseController, metaclass=ABCMeta):
    def __init__(self, queue):
        """
        This is a base class for Stock Controllers that use a load function.
        """
        super().__init__(queue)
        self.stock = pd.DataFrame()
        self.interval = "1440min"
        self.ticker = ""
        self.start = ""
        self.suffix = ""  # To hold suffix for Yahoo Finance
        self.add_info = stocks_helper.additional_info_about_ticker("")
        self.TRY_RELOAD = True

    def call_load(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load stock ticker to perform analysis on. When the data source"
            + " is syf', an Indian ticker can be"
            + " loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in"
            + " https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html.",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            action="store",
            dest="ticker",
            required="-h" not in other_args,
            help="Stock ticker",
        )
        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=1100)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the stock",
        )
        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            default=datetime.now().strftime("%Y-%m-%d"),
            dest="end",
            help="The ending date (format YYYY-MM-DD) of the stock",
        )
        parser.add_argument(
            "-i",
            "--interval",
            action="store",
            dest="interval",
            type=int,
            default=1440,
            choices=[1, 5, 15, 30, 60],
            help="Intraday stock minutes",
        )
        parser.add_argument(
            "--source",
            action="store",
            dest="source",
            choices=["yf", "av", "iex", "polygon"]
            if "-i" not in other_args or "--interval" not in other_args
            else ["yf", "polygon"],
            default="yf",
            help="Source of historical data.",
        )
        parser.add_argument(
            "-p",
            "--prepost",
            action="store_true",
            default=False,
            dest="prepost",
            help="Pre/After market hours. Only works for 'yf' source, and intraday data",
        )
        parser.add_argument(
            "-f",
            "--file",
            default=None,
            help="Path to load custom file.",
            dest="filepath",
            type=str,
        )
        parser.add_argument(
            "-m",
            "--monthly",
            action="store_true",
            default=False,
            help="Load monthly data",
            dest="monthly",
        )
        parser.add_argument(
            "-w",
            "--weekly",
            action="store_true",
            default=False,
            help="Load weekly data",
            dest="weekly",
        )
        parser.add_argument(
            "-r",
            "--iexrange",
            dest="iexrange",
            help="Range for using the iexcloud api.  Note that longer range requires more tokens in account",
            choices=["ytd", "1y", "2y", "5y", "6m"],
            type=str,
            default="ytd",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if ns_parser.weekly and ns_parser.monthly:
                console.print(
                    "[red]Only one of monthly or weekly can be selected.[/red]\n."
                )
                return
            if ns_parser.filepath is None:
                df_stock_candidate = stocks_helper.load(
                    ns_parser.ticker,
                    ns_parser.start,
                    ns_parser.interval,
                    ns_parser.end,
                    ns_parser.prepost,
                    ns_parser.source,
                    weekly=ns_parser.weekly,
                    monthly=ns_parser.monthly,
                )
            else:
                # This seems to block the .exe since the folder needs to be manually created
                # This block basically makes sure that we only look for the file if the -f flag is used
                # If we add files in the argparse choices, it will fail for the .exe even if no -f is used
                try:
                    if ns_parser.filepath not in os.listdir(
                        os.path.join("custom_imports", "stocks")
                    ):
                        console.print(
                            f"[red]{ns_parser.filepath} not found in custom_imports/stocks/ folder[/red].\n"
                        )
                        return
                except Exception as e:
                    console.print(e)
                    return

                df_stock_candidate = stocks_helper.load_custom(
                    os.path.join(
                        os.path.join("custom_imports", "stocks"), ns_parser.filepath
                    )
                )
                if df_stock_candidate.empty:
                    return
            if not df_stock_candidate.empty:
                self.stock = df_stock_candidate
                self.add_info = stocks_helper.additional_info_about_ticker(
                    ns_parser.ticker
                )
                console.print(self.add_info)
                if (
                    ns_parser.interval == 1440
                    and ns_parser.filepath is None
                    and self.PATH == "/stocks/"
                ):
                    stocks_helper.show_quick_performance(self.stock, ns_parser.ticker)
                if "." in ns_parser.ticker:
                    self.ticker, self.suffix = ns_parser.ticker.upper().split(".")
                else:
                    self.ticker = ns_parser.ticker.upper()
                    self.suffix = ""

                if ns_parser.source == "iex":
                    self.start = self.stock.index[0].to_pydatetime()
                else:
                    self.start = ns_parser.start
                self.interval = f"{ns_parser.interval}min"

                if self.PATH in ["/stocks/qa/", "/stocks/pred/"]:
                    self.stock["Returns"] = self.stock["Adj Close"].pct_change()
                    self.stock["LogRet"] = np.log(self.stock["Adj Close"]) - np.log(
                        self.stock["Adj Close"].shift(1)
                    )
                    self.stock["LogPrice"] = np.log(self.stock["Adj Close"])
                    self.stock = self.stock.rename(columns={"Adj Close": "AdjClose"})
                    self.stock = self.stock.dropna()
                    self.stock.columns = [x.lower() for x in self.stock.columns]
                    console.print("")


class CryptoBaseController(BaseController, metaclass=ABCMeta):
    def __init__(self, queue):
        """
        This is a base class for Crypto Controllers that use a load function.
        """
        super().__init__(queue)

        self.symbol = ""
        self.current_df = pd.DataFrame()
        self.current_currency = ""
        self.source = ""
        self.current_interval = ""
        self.price_str = ""
        self.resolution = "1D"
        self.TRY_RELOAD = True

    def call_load(self, other_args):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load crypto currency to perform analysis on."
            "CoinGecko is used as source for price and YahooFinance for volume.",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="Coin to get. Must be coin symbol (e.g., btc, eth)",
            dest="coin",
            type=str,
            required="-h" not in other_args,
        )

        parser.add_argument(
            "-d",
            "--days",
            default="365",
            dest="days",
            help="Data up to number of days ago",
            choices=["1", "7", "14", "30", "90", "180", "365"],
        )
        parser.add_argument(
            "--vs",
            help="Quote currency (what to view coin vs)",
            dest="vs",
            default="usd",
            type=str,
            choices=["usd", "eur"],
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            (self.current_df) = cryptocurrency_helpers.load(
                symbol_search=ns_parser.coin.lower(),
                days=int(ns_parser.days),
                vs=ns_parser.vs,
            )
            if not self.current_df.empty:
                self.current_interval = "1day"
                self.current_currency = ns_parser.vs
                self.symbol = ns_parser.coin.lower()
                cryptocurrency_helpers.show_quick_performance(
                    self.current_df, self.symbol, self.current_currency
                )
            else:
                console.print(
                    f"\n[red]Could not find [bold]{ns_parser.coin}[/bold] in [bold]CoinGecko[/bold]. Make sure you search for symbol (e.g., btc) and not full name (e.g., bitcoin)[/red]\n"  # noqa: E501
                )
