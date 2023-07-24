"""Parent Classes."""
__docformat__ = "numpy"

# pylint: disable=C0301,C0302,R0902,global-statement,too-many-boolean-expressions

# IMPORTS STANDARD
import argparse
import difflib
import json
import logging
import os
import re
from abc import ABCMeta, abstractmethod
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

# IMPORTS THIRDPARTY
import numpy as np
import openai
import pandas as pd
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.styles import Style
from rich.markdown import Markdown

# IMPORTS INTERNAL
import openbb_terminal.core.session.local_model as Local
from openbb_terminal import config_terminal
from openbb_terminal.account.show_prompt import get_show_prompt
from openbb_terminal.core.completer.choices import build_controller_choice_map
from openbb_terminal.core.config.paths import HIST_FILE_PATH
from openbb_terminal.core.session import hub_model as Hub
from openbb_terminal.core.session.current_user import get_current_user, is_local
from openbb_terminal.core.session.routines_handler import read_routine
from openbb_terminal.cryptocurrency import cryptocurrency_helpers
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    check_file_type_saved,
    check_positive,
    export_data,
    get_flair,
    parse_and_split_input,
    prefill_form,
    query_LLM_local,
    query_LLM_remote,
    screenshot,
    search_wikipedia,
    set_command_location,
    support_message,
    system_clear,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.rich_config import console, get_ordered_list_sources
from openbb_terminal.stocks import stocks_helper
from openbb_terminal.terminal_helper import (
    is_auth_enabled,
    open_openbb_documentation,
    print_guest_block_msg,
)

from .helper_classes import TerminalStyle as _TerminalStyle

logger = logging.getLogger(__name__)

# pylint: disable=R0912

NO_EXPORT = 0
EXPORT_ONLY_RAW_DATA_ALLOWED = 1
EXPORT_ONLY_FIGURES_ALLOWED = 2
EXPORT_BOTH_RAW_DATA_AND_FIGURES = 3

controllers: Dict[str, Any] = {}

CRYPTO_SOURCES = {
    "bin": "Binance",
    "CoinGecko": "CoinGecko",
    "cp": "CoinPaprika",
    "cb": "Coinbase",
    "YahooFinance": "YahooFinance",
}

SUPPORT_TYPE = ["bug", "suggestion", "question", "generic"]


# TODO: We should try to avoid these global variables
RECORD_SESSION = False
SESSION_RECORDED = list()
SESSION_RECORDED_NAME = ""
SESSION_RECORDED_DESCRIPTION = ""
SESSION_RECORDED_TAGS = ""
SESSION_RECORDED_PUBLIC = False


class BaseController(metaclass=ABCMeta):
    """Base class for a terminal controller."""

    CHOICES_COMMON = [
        "cls",
        "home",
        "about",
        "h",
        "?",
        "help",
        "q",
        "quit",
        "..",
        "e",
        "exit",
        "r",
        "reset",
        "support",
        "wiki",
        "record",
        "stop",
        "screenshot",
        "askobb",
        "hold",
    ]

    if is_auth_enabled():
        CHOICES_COMMON += ["whoami"]

    CHOICES_COMMANDS: List[str] = []
    CHOICES_MENUS: List[str] = []
    SUPPORT_CHOICES: dict = {}
    ABOUT_CHOICES: dict = {}
    HOLD_CHOICES: dict = {}
    NEWS_CHOICES: dict = {}
    COMMAND_SEPARATOR = "/"
    KEYS_MENU = "keys" + COMMAND_SEPARATOR
    TRY_RELOAD = False
    PATH: str = ""
    FILE_PATH: str = ""
    CHOICES_GENERATION = False

    @property
    def choices_default(self):
        choices = (
            build_controller_choice_map(controller=self)
            if self.CHOICES_GENERATION
            else {}
        )

        return choices

    def __init__(self, queue: Optional[List[str]] = None) -> None:
        """Create the base class for any controller in the codebase.

        Used to simplify the creation of menus.

        queue: List[str]
            The current queue of jobs to process separated by "/"
            E.g. /stocks/load gme/dps/sidtc/../exit
        """
        self.check_path()
        self.path = [x for x in self.PATH.split("/") if x != ""]
        self.queue = (
            self.parse_input(an_input="/".join(queue))
            if (queue and self.PATH != "/")
            else list()
        )

        controller_choices = self.CHOICES_COMMANDS + self.CHOICES_MENUS
        if controller_choices:
            self.controller_choices = controller_choices + self.CHOICES_COMMON
        else:
            self.controller_choices = self.CHOICES_COMMON

        self.completer: Union[None, NestedCompleter] = None

        self.parser = argparse.ArgumentParser(
            add_help=False,
            prog=self.path[-1] if self.PATH != "/" else "terminal",
        )
        self.parser.exit_on_error = False  # type: ignore
        self.parser.add_argument("cmd", choices=self.controller_choices)

        # Add in about options
        self.ABOUT_CHOICES = {
            c: None for c in self.CHOICES_COMMANDS + self.CHOICES_MENUS
        }

        # Remove common choices from list of support commands
        self.support_commands = [
            c for c in self.controller_choices if c not in self.CHOICES_COMMON
        ]

        # Add in support options
        support_choices: dict = {c: {} for c in self.controller_choices}

        support_choices = {c: None for c in (["generic"] + self.support_commands)}

        support_choices["--command"] = {
            c: None for c in (["generic"] + self.support_commands)
        }

        support_choices["-c"] = {c: None for c in (["generic"] + self.support_commands)}

        support_choices["--type"] = {c: None for c in (SUPPORT_TYPE)}

        self.SUPPORT_CHOICES = support_choices

        self.HELP_CHOICES = {
            c: None for c in ["on", "off", "-s", "--sameaxis", "--title"]
        }

        # Add in news options
        news_choices = [
            "--term",
            "-t",
            "--sources",
            "-s",
            "--help",
            "-h",
            "--tag",
            "--taglist",
            "--sourcelist",
        ]
        self.NEWS_CHOICES = {c: None for c in news_choices}

    def check_path(self) -> None:
        """Check if command path is valid."""
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
        """Check for an existing instance of the controller before creating a new one."""
        current_user = get_current_user()
        self.save_class()
        arguments = len(args) + len(kwargs)
        # Due to the 'arguments == 1' condition, we actually NEVER load a class
        # that has arguments (The 1 argument corresponds to self.queue)
        # Advantage: If the user changes something on one controller and then goes to the
        # controller below, it will create such class from scratch bringing all new variables
        # in and considering latest changes.
        # Disadvantage: If the user goes on a controller below and we have been there before
        # it will not load that previous class, but create a new one from scratch.
        # SCENARIO: If the user is in stocks and does load AAPL/ta the TA menu will get AAPL,
        # and if then the user goes back to the stocks menu using .. that menu will have AAPL
        # Now, if "arguments == 1" condition exists, if the user does "load TSLA" and then
        # goes into "TA", the "TSLA" ticker will appear. If that condition doesn't exist
        # the previous class will be loaded and even if the user changes the ticker on
        # the stocks context it will not impact the one of TA menu - unless changes are done.
        # An exception is made for forecasting because it is built to handle multiple loaded
        # tickers.
        if class_ins.PATH in controllers and class_ins.PATH == "/forecast/":
            old_class = controllers[class_ins.PATH]
            old_class.queue = self.queue
            old_class.load(*args[:-1], **kwargs)
            return old_class.menu()
        if (
            class_ins.PATH in controllers
            and arguments == 1
            and current_user.preferences.REMEMBER_CONTEXTS
        ):
            old_class = controllers[class_ins.PATH]
            old_class.queue = self.queue
            return old_class.menu()
        # Add another case so options data is saved
        if (
            class_ins.PATH == "/stocks/options/"
            and current_user.preferences.REMEMBER_CONTEXTS
            and "/stocks/options/" in controllers
        ):
            old_class = controllers[class_ins.PATH]
            old_class.queue = self.queue
            return old_class.menu()
        return class_ins(*args, **kwargs).menu()

    def call_hold(self, other_args: List[str]) -> None:
        self.save_class()
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="hold",
            description="Turn on figure holding.  This will stop showing images until hold off is run.",
        )
        parser.add_argument(
            "-o",
            "--option",
            choices=["on", "off"],
            type=str,
            default="off",
            dest="option",
        )
        parser.add_argument(
            "-s",
            "--sameaxis",
            action="store_true",
            default=False,
            help="Put plots on the same axis.  Best when numbers are on similar scales",
            dest="axes",
        )
        parser.add_argument(
            "--title",
            type=str,
            default="",
            dest="title",
            nargs="+",
            help="When using hold off, this sets the title for the figure.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-o")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
        )
        if ns_parser:
            if ns_parser.option == "on":
                config_terminal.HOLD = True
                config_terminal.COMMAND_ON_CHART = False
                if ns_parser.axes:
                    config_terminal.set_same_axis()
                else:
                    config_terminal.set_new_axis()
            if ns_parser.option == "off":
                config_terminal.HOLD = False
                if config_terminal.get_current_figure() is not None:
                    # create a subplot
                    fig = config_terminal.get_current_figure()
                    if fig is None:
                        return
                    if not fig.has_subplots and not config_terminal.make_new_axis():
                        fig.set_subplots(1, 1, specs=[[{"secondary_y": True}]])

                    if config_terminal.make_new_axis():
                        for i, trace in enumerate(fig.select_traces()):
                            trace.yaxis = f"y{i+1}"

                            if i != 0:
                                fig.update_layout(
                                    {
                                        f"yaxis{i+1}": dict(
                                            side="left",
                                            overlaying="y",
                                            showgrid=True,
                                            showline=False,
                                            zeroline=False,
                                            automargin=True,
                                            ticksuffix="       " * (i - 1)
                                            if i > 1
                                            else "",
                                            tickfont=dict(
                                                size=18,
                                                color=_TerminalStyle().get_colors()[i],
                                            ),
                                            title=dict(
                                                font=dict(
                                                    size=15,
                                                ),
                                                standoff=0,
                                            ),
                                        ),
                                    }
                                )
                        # pylint: disable=undefined-loop-variable
                        fig.update_layout(margin=dict(l=30 * i))

                    else:
                        fig.update_yaxes(title="")

                    if any(config_terminal.get_legends()):
                        for trace, new_name in zip(
                            fig.select_traces(), config_terminal.get_legends()
                        ):
                            if new_name:
                                trace.name = new_name

                    fig.update_layout(title=" ".join(ns_parser.title))
                    fig.show()
                    config_terminal.COMMAND_ON_CHART = True

                    config_terminal.set_current_figure(None)
                    config_terminal.reset_legend()

    def call_askobb(self, other_args: List[str]) -> None:
        """Accept user input as a string and return the most appropriate Terminal command"""
        self.save_class()
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="askobb",
            description="Accept input as a string and return the most appropriate Terminal command",
        )
        parser.add_argument(
            "--prompt",
            "-p",
            action="store",
            type=str,
            nargs="+",
            dest="question",
            required="-h" not in other_args and "--help" not in other_args,
            default="",
            help="Question for Askobb LLM",
        )

        parser.add_argument(
            "--model",
            "-m",
            action="store",
            type=str,
            dest="gpt_model",
            required=False,
            default="gpt-3.5-turbo",
            choices=["gpt-3.5-turbo", "gpt-4"],
            help="GPT Model to use for Askobb LLM (default: gpt-3.5-turbo) or gpt-4 (beta)",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
        )

        if ns_parser:
            # check if user has passed a question with 2 or more words
            if len(ns_parser.question) < 2:
                console.print("[red]Please enter a prompt with more than 1 word[/red]")
            else:
                api_key = get_current_user().credentials.API_OPENAI_KEY
                if ns_parser.gpt_model == "gpt-4" and api_key == "REPLACE_ME":
                    console.print(
                        "[red]GPT-4 only available with local OPENAI Key.\n[/]"
                    )
                    return

                if api_key == "REPLACE_ME":
                    response, source_nodes = query_LLM_remote(
                        " ".join(ns_parser.question)
                    )

                else:
                    if ns_parser.gpt_model != "gpt-4":
                        console.print(
                            "[yellow]Using local OpenAI Key"
                            ".  Please remove from OpenBB Hub to query askobb remotely.[/]\n"
                        )
                    # This is needed to avoid authentication error
                    openai.api_key = api_key
                    response, source_nodes = query_LLM_local(
                        " ".join(ns_parser.question), ns_parser.gpt_model
                    )

                feedback = ""
                if response is not None:
                    # check that "I don't know" and "Sorry" is not the response
                    if all(
                        phrase not in response
                        for phrase in [
                            "I don't know",
                            "Sorry",
                            "I am not sure",
                            "no terminal command provided",
                            "no available",
                            "no command provided",
                            "no information",
                            "does not contain",
                            "I cannot provide",
                        ]
                    ):
                        console.print(
                            f"[green]Suggested Command:[/green] /{response}\n"
                        )

                        console.print(
                            "[yellow]Would you like to run this command?(y/n/fb)[/yellow]"
                        )
                        user_response = input()
                        if user_response == "y":
                            self.queue.append("home/" + response)
                        elif user_response == "n":
                            console.print("Please refine your question and try again.")
                        elif user_response == "fb":
                            console.print(
                                "\n[yellow]Please enter your feedback on askobb:[/] "
                            )
                            feedback = input()
                            if feedback:
                                console.print(
                                    "\n[green]Thank you for your feedback![/]"
                                )

                    else:
                        console.print(
                            "[red]askobb could not respond with an appropriate answer.[/red]"
                        )
                        console.print("Please refine your question and try again.")

                logger.info(
                    "ASKOBB: %s ",
                    json.dumps(
                        {
                            "Question": " ".join(ns_parser.question),
                            "Model": ns_parser.gpt_model,
                            "Response": response,
                            "Nodes": str(source_nodes),
                            "Feedback": feedback,
                        }
                    ),
                )

    def save_class(self) -> None:
        """Save the current instance of the class to be loaded later."""
        if get_current_user().preferences.REMEMBER_CONTEXTS:
            controllers[self.PATH] = self

    def custom_reset(self) -> List[str]:
        """Implement custom reset.

        This will be replaced by any children with custom_reset functions.
        """
        return []

    @abstractmethod
    def print_help(self) -> None:
        """Print help placeholder."""
        raise NotImplementedError("Must override print_help.")

    def parse_input(self, an_input: str) -> list:
        """Parse controller input.

        Splits the command chain from user input into a list of individual commands
        while respecting the forward slash in the command arguments.

        In the default scenario only unix-like paths are handles by the parser.
        Override this function in the controller classes that inherit from this one to
        resolve edge cases specific to command arguments on those controllers.

        When handling edge cases add additional regular expressions to the list.

        Parameters
        ----------
        an_input : str
            User input string

        Returns
        ----------
        list
            Command queue as list
        """
        custom_filters: list = []
        commands = parse_and_split_input(
            an_input=an_input, custom_filters=custom_filters
        )
        return commands

    def contains_keys(self, string_to_check: str) -> bool:
        """Check if string contains keys."""
        if self.KEYS_MENU in string_to_check or self.KEYS_MENU in self.PATH:
            return True
        return False

    def log_queue(self) -> None:
        """Log command queue."""
        if self.queue:
            joined_queue = self.COMMAND_SEPARATOR.join(self.queue)
            if not self.contains_keys(joined_queue):
                queue = {"path": self.PATH, "queue": joined_queue}
                logger.info(
                    "QUEUE: %s", json.dumps(queue, default=str, ensure_ascii=False)
                )

    def log_cmd_and_queue(
        self, known_cmd: str, other_args_str: str, the_input: str
    ) -> None:
        """Log command and command queue.

        Parameters
        ----------
        known_cmd : str
            Current command
        other_args_str : str
            Command arguments
        the_input : str
            Raw command input (command queue)
        """
        if not self.contains_keys(the_input):
            cmd = {
                "path": self.PATH,
                "known_cmd": known_cmd,
                "other_args": other_args_str,
                "input": the_input,
            }
            logger.info("CMD: %s", json.dumps(cmd))

        if the_input not in self.KEYS_MENU:
            self.log_queue()

    @log_start_end(log=logger)
    def switch(self, an_input: str) -> List[str]:
        """Process and dispatch input.

        Returns
        ----------
        List[str]
            list of commands in the queue to execute
        """
        actions = self.parse_input(an_input)

        if an_input and an_input != "reset":
            console.print()

        # Empty command
        if len(actions) == 0:
            pass

        # Navigation slash is being used first split commands
        elif len(actions) > 1:
            # Absolute path is specified
            if not actions[0]:
                actions[0] = "home"

            # Add all instructions to the queue
            for cmd in actions[::-1]:
                if cmd:
                    self.queue.insert(0, cmd)

        # Single command fed, process
        else:
            try:
                (known_args, other_args) = self.parser.parse_known_args(
                    an_input.split()
                )
            except Exception as exc:
                raise SystemExit from exc

            if RECORD_SESSION:
                SESSION_RECORDED.append(an_input)

            # Redirect commands to their correct functions
            if known_args.cmd:
                if known_args.cmd in ("..", "q"):
                    known_args.cmd = "quit"
                elif known_args.cmd in ("e"):
                    known_args.cmd = "exit"
                elif known_args.cmd in ("?", "h"):
                    known_args.cmd = "help"
                elif known_args.cmd == "r":
                    known_args.cmd = "reset"

            set_command_location(f"{self.PATH}{known_args.cmd}")
            self.log_cmd_and_queue(known_args.cmd, ";".join(other_args), an_input)

            getattr(
                self,
                "call_" + known_args.cmd,
                lambda _: "Command not recognized!",
            )(other_args)

        self.log_queue()

        if (
            an_input
            and an_input != "reset"
            and (
                not self.queue or (self.queue and self.queue[0] not in ("quit", "help"))
            )
        ):
            console.print()

        return self.queue

    @log_start_end(log=logger)
    def call_cls(self, _) -> None:
        """Process cls command."""
        system_clear()

    @log_start_end(log=logger)
    def call_home(self, _) -> None:
        """Process home command."""
        self.save_class()
        if (
            self.PATH.count("/") == 1
            and get_current_user().preferences.ENABLE_EXIT_AUTO_HELP
        ):
            self.print_help()
        for _ in range(self.PATH.count("/") - 1):
            self.queue.insert(0, "quit")

    @log_start_end(log=logger)
    def call_help(self, _) -> None:
        """Process help command."""
        self.print_help()

    @log_start_end(log=logger)
    def call_about(self, other_args: List[str]) -> None:
        """Process about command."""
        description = "Display the documentation of the menu or command."
        if self.CHOICES_COMMANDS and self.CHOICES_MENUS:
            description += (
                f" E.g. 'about {self.CHOICES_COMMANDS[0]}' opens a guide about the command "
                f"{self.CHOICES_COMMANDS[0]} and 'about {self.CHOICES_MENUS[0]}' opens a guide about the "
                f"menu {self.CHOICES_MENUS[0]}."
            )

        parser = argparse.ArgumentParser(
            add_help=False, prog="about", description=description
        )
        parser.add_argument(
            "-c",
            "--command",
            type=str,
            dest="command",
            default=None,
            help="Obtain documentation on the given command or menu",
            choices=self.CHOICES_COMMANDS + self.CHOICES_MENUS + self.CHOICES_COMMON,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            arg_type = ""
            if ns_parser.command in self.CHOICES_COMMANDS:
                arg_type = "command"
            elif ns_parser.command in self.CHOICES_MENUS:
                arg_type = "menu"

            open_openbb_documentation(
                self.PATH, command=ns_parser.command, arg_type=arg_type
            )

    @log_start_end(log=logger)
    def call_quit(self, _) -> None:
        """Process quit menu command."""
        self.save_class()
        self.queue.insert(0, "quit")

    @log_start_end(log=logger)
    def call_exit(self, _) -> None:
        # Not sure how to handle controller loading here
        """Process exit terminal command."""
        self.save_class()
        for _ in range(self.PATH.count("/")):
            self.queue.insert(0, "quit")

        if not is_local():
            Local.remove(get_current_user().preferences.USER_ROUTINES_DIRECTORY / "hub")
            if not get_current_user().profile.remember:
                Local.remove(HIST_FILE_PATH)

    @log_start_end(log=logger)
    def call_reset(self, _) -> None:
        """Process reset command.

        If you would like to have customization in the reset process define a method
        `custom_reset` in the child class.
        """
        self.save_class()
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
    def call_resources(self, other_args: List[str]) -> None:
        """Process resources command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="resources",
            description="Display available markdown resources.",
        )
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser:
            if os.path.isfile(self.FILE_PATH):
                with open(self.FILE_PATH) as f:
                    console.print(Markdown(f.read()))

            else:
                console.print("No resources available.\n")

    @log_start_end(log=logger)
    def call_support(self, other_args: List[str]) -> None:
        """Process support command."""
        self.save_class()

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

        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser:
            prefill_form(
                ticket_type=ns_parser.type,
                menu=main_menu,
                command=ns_parser.command,
                message=" ".join(ns_parser.msg),
                path=self.PATH,
            )

    @log_start_end(log=logger)
    def call_wiki(self, other_args: List[str]) -> None:
        """Process wiki command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="wiki",
            description="Search Wikipedia",
        )
        parser.add_argument(
            "--expression",
            "-e",
            action="store",
            nargs="+",
            dest="expression",
            required=True,
            default="",
            help="Expression to search for",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-e")

        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser and ns_parser.expression:
            expression = " ".join(ns_parser.expression)
            search_wikipedia(expression)

    @log_start_end(log=logger)
    def call_record(self, other_args) -> None:
        """Process record command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="record",
            description="Start recording session into .openbb routine file",
        )
        parser.add_argument(
            "-n",
            "--name",
            action="store",
            dest="name",
            type=str,
            default=datetime.now().strftime("%Y%m%d_%H%M%S_routine.openbb"),
            help="Routine file name to be saved.",
        )
        parser.add_argument(
            "-d",
            "--description",
            type=str,
            dest="description",
            help="The description of the routine",
            default="",
            nargs="+",
        )
        parser.add_argument(
            "-t",
            "--tags",
            type=str,
            dest="tags",
            help="The tags of the routine",
            default="",
            nargs="+",
        )
        parser.add_argument(
            "-p",
            "--public",
            dest="public",
            action="store_true",
            help="Whether the routine should be public or not",
            default=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser:
            global RECORD_SESSION
            global SESSION_RECORDED_NAME
            global SESSION_RECORDED_DESCRIPTION
            global SESSION_RECORDED_TAGS
            global SESSION_RECORDED_PUBLIC

            SESSION_RECORDED_NAME = (
                ns_parser.name
                if ".openbb" in ns_parser.name
                else ns_parser.name + ".openbb"
            )

            SESSION_RECORDED_DESCRIPTION = " ".join(ns_parser.description)
            SESSION_RECORDED_TAGS = " ".join(ns_parser.tags) if ns_parser.tags else ""
            SESSION_RECORDED_PUBLIC = ns_parser.public

            console.print(
                "[green]The session is successfully being recorded."
                + " Remember to 'stop' before exiting terminal!\n[/green]"
            )
            RECORD_SESSION = True

    @log_start_end(log=logger)
    def call_stop(self, _) -> None:
        """Process stop command."""
        global RECORD_SESSION
        global SESSION_RECORDED

        if not RECORD_SESSION:
            console.print(
                "[red]There is no session being recorded. Start one using 'record'[/red]\n"
            )
        elif not SESSION_RECORDED:
            console.print(
                "[red]There is no session to be saved. Run at least 1 command after starting 'record'[/red]\n"
            )
        else:
            current_user = get_current_user()
            routine_file = os.path.join(
                current_user.preferences.USER_ROUTINES_DIRECTORY, SESSION_RECORDED_NAME
            )

            if os.path.isfile(routine_file):
                routine_file = os.path.join(
                    current_user.preferences.USER_ROUTINES_DIRECTORY,
                    datetime.now().strftime("%Y%m%d_%H%M%S_") + SESSION_RECORDED_NAME,
                )

            # Writing to file
            with open(routine_file, "w") as file1:
                # Writing data to a file
                file1.writelines([c + "\n\n" for c in SESSION_RECORDED[:-1]])

            console.print(
                f"[green]Your routine has been recorded and saved here: {routine_file}[/green]\n"
            )

            if not is_local():
                routine = read_routine(file_name=routine_file)
                if routine is not None:
                    name = SESSION_RECORDED_NAME.split(sep=".openbb", maxsplit=-1)[0]
                    kwargs = {
                        "auth_header": current_user.profile.get_auth_header(),
                        "name": name,
                        "description": SESSION_RECORDED_DESCRIPTION,
                        "routine": routine,
                        "tags": SESSION_RECORDED_TAGS,
                        "public": SESSION_RECORDED_PUBLIC,
                    }
                    response = Hub.upload_routine(**kwargs)  # type: ignore
                    if response is not None and response.status_code == 409:
                        i = console.input(
                            "A routine with the same name already exists, "
                            "do you want to replace it? (y/n): "
                        )
                        console.print("")
                        if i.lower() in ["y", "yes"]:
                            kwargs["override"] = True  # type: ignore
                            response = Hub.upload_routine(**kwargs)  # type: ignore
                        else:
                            console.print("[info]Aborted.[/info]")

            # Clear session to be recorded again
            RECORD_SESSION = False
            SESSION_RECORDED = list()

    @log_start_end(log=logger)
    def call_screenshot(self, other_args: List[str]) -> None:
        """Process screenshot command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="screenshot",
            description="Screenshot terminal window or plot figure open into an OpenBB frame. "
            "Default target is plot if there is one open, otherwise it's terminal window. "
            " In case the user wants the terminal window, it can be forced with '-t` or '--terminal' flag passed.",
        )
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser:
            screenshot()

    @log_start_end(log=logger)
    def call_whoami(self, other_args: List[str]) -> None:
        """Process whoami command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="whoami",
            description="Show current user",
        )
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser:
            current_user = get_current_user()
            local_user = is_local()
            if not local_user:
                console.print(f"[info]email:[/info] {current_user.profile.email}")
                console.print(f"[info]uuid:[/info] {current_user.profile.uuid}")
            else:
                print_guest_block_msg()

    @staticmethod
    def parse_simple_args(parser: argparse.ArgumentParser, other_args: List[str]):
        """Parse list of arguments into the supplied parser.

        Parameters
        ----------
        parser: argparse.ArgumentParser
            Parser with predefined arguments
        other_args: List[str]
            List of arguments to parse

        Returns
        -------
        ns_parser:
            Namespace with parsed arguments
        """
        current_user = get_current_user()

        parser.add_argument(
            "-h", "--help", action="store_true", help="show this help message"
        )

        if current_user.preferences.USE_CLEAR_AFTER_CMD:
            system_clear()

        try:
            (ns_parser, l_unknown_args) = parser.parse_known_args(other_args)
        except SystemExit:
            # In case the command has required argument that isn't specified
            console.print("\n")
            return None

        if ns_parser.help:
            txt_help = parser.format_help()
            console.print(f"[help]{txt_help}[/help]")
            return None

        if l_unknown_args:
            console.print(
                f"The following args couldn't be interpreted: {l_unknown_args}\n"
            )

        return ns_parser

    @classmethod
    def parse_known_args_and_warn(
        cls,
        parser: argparse.ArgumentParser,
        other_args: List[str],
        export_allowed: int = NO_EXPORT,
        raw: bool = False,
        limit: int = 0,
    ):
        """Parse list of arguments into the supplied parser.

        Parameters
        ----------
        parser: argparse.ArgumentParser
            Parser with predefined arguments
        other_args: List[str]
            list of arguments to parse
        export_allowed: int
            Choose from NO_EXPORT, EXPORT_ONLY_RAW_DATA_ALLOWED,
            EXPORT_ONLY_FIGURES_ALLOWED and EXPORT_BOTH_RAW_DATA_AND_FIGURES
        raw: bool
            Add the --raw flag
        limit: int
            Add a --limit flag with this number default

        Returns
        ----------
        ns_parser:
            Namespace with parsed arguments
        """
        parser.add_argument(
            "-h", "--help", action="store_true", help="show this help message"
        )

        if config_terminal.HOLD:
            parser.add_argument(
                "--legend",
                type=str,
                dest="hold_legend_str",
                default="",
                nargs="+",
                help="Label for legend when hold is on.",
            )

        if export_allowed > NO_EXPORT:
            choices_export = []
            help_export = "Does not export!"

            if export_allowed == EXPORT_ONLY_RAW_DATA_ALLOWED:
                choices_export = ["csv", "json", "xlsx"]
                help_export = "Export raw data into csv, json, xlsx"
            elif export_allowed == EXPORT_ONLY_FIGURES_ALLOWED:
                choices_export = ["png", "jpg", "pdf", "svg"]
                help_export = "Export figure into png, jpg, pdf, svg "
            else:
                choices_export = ["csv", "json", "xlsx", "png", "jpg", "pdf", "svg"]
                help_export = "Export raw data into csv, json, xlsx and figure into png, jpg, pdf, svg "

            parser.add_argument(
                "--export",
                default="",
                type=check_file_type_saved(choices_export),
                dest="export",
                help=help_export,
            )

            # If excel is an option, add the sheet name
            if export_allowed in [
                EXPORT_ONLY_RAW_DATA_ALLOWED,
                EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            ]:
                parser.add_argument(
                    "--sheet-name",
                    dest="sheet_name",
                    default=None,
                    nargs="+",
                    help="Name of excel sheet to save data to. Only valid for .xlsx files.",
                )

        if raw:
            parser.add_argument(
                "--raw",
                dest="raw",
                action="store_true",
                default=False,
                help="Flag to display raw data",
            )
        if limit > 0:
            parser.add_argument(
                "-l",
                "--limit",
                dest="limit",
                default=limit,
                help="Number of entries to show in data.",
                type=check_positive,
            )
        sources = get_ordered_list_sources(f"{cls.PATH}{parser.prog}")
        # Allow to change source if there is more than one
        if len(sources) > 1:
            parser.add_argument(
                "--source",
                action="store",
                dest="source",
                choices=sources,
                default=sources[0],  # the first source from the list is the default
                help="Data source to select from",
            )

        current_user = get_current_user()

        if current_user.preferences.USE_CLEAR_AFTER_CMD:
            system_clear()

        try:
            (ns_parser, l_unknown_args) = parser.parse_known_args(other_args)

            if export_allowed in [
                EXPORT_ONLY_RAW_DATA_ALLOWED,
                EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            ]:
                ns_parser.is_image = any(
                    ext in ns_parser.export for ext in ["png", "svg", "jpg", "pdf"]
                )

        except SystemExit:
            # In case the command has required argument that isn't specified

            return None

        if ns_parser.help:
            txt_help = parser.format_help() + "\n"
            if parser.prog != "about":
                txt_help += (
                    f"For more information and examples, use 'about {parser.prog}' "
                    f"to access the related guide.\n"
                )
            console.print(f"[help]{txt_help}[/help]")
            return None

        # This protects against the hidden loads in stocks/fa
        if parser.prog != "load" and config_terminal.HOLD:
            config_terminal.set_last_legend(" ".join(ns_parser.hold_legend_str))

        if l_unknown_args:
            console.print(
                f"The following args couldn't be interpreted: {l_unknown_args}"
            )
        return ns_parser

    def menu(self, custom_path_menu_above: str = ""):
        """Enter controller menu."""

        current_user = get_current_user()
        an_input = "HELP_ME"

        while True:
            # There is a command in the queue
            if self.queue and len(self.queue) > 0:
                # If the command is quitting the menu we want to return in here
                if self.queue[0] in ("q", "..", "quit"):
                    self.save_class()
                    # Go back to the root in order to go to the right directory because
                    # there was a jump between indirect menus
                    if custom_path_menu_above:
                        self.queue.insert(1, custom_path_menu_above)

                    if len(self.queue) > 1:
                        return self.queue[1:]

                    if current_user.preferences.ENABLE_EXIT_AUTO_HELP:
                        return ["help"]
                    return []

                # Consume 1 element from the queue
                an_input = self.queue[0]
                self.queue = self.queue[1:]

                # Print location because this was an instruction and we want user to know the action
                if (
                    an_input
                    and an_input != "home"
                    and an_input != "help"
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
                    if session and current_user.preferences.USE_PROMPT_TOOLKIT:
                        # Check if toolbar hint was enabled
                        if current_user.preferences.TOOLBAR_HINT:
                            an_input = session.prompt(
                                f"{get_flair()} {self.PATH} $ ",
                                completer=self.completer,
                                search_ignore_case=True,
                                bottom_toolbar=HTML(
                                    '<style bg="ansiblack" fg="ansiwhite">[h]</style> help menu    '
                                    '<style bg="ansiblack" fg="ansiwhite">[q]</style> return to previous menu    '
                                    '<style bg="ansiblack" fg="ansiwhite">[e]</style> exit terminal    '
                                    '<style bg="ansiblack" fg="ansiwhite">[cmd -h]</style> '
                                    "see usage and available options    "
                                    f'<style bg="ansiblack" fg="ansiwhite">[about (cmd/menu)]</style> '
                                    f"{self.path[-1].capitalize()} (cmd/menu) Documentation"
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

                except (KeyboardInterrupt, EOFError):
                    # Exit in case of keyboard interrupt
                    an_input = "exit"

            try:
                # Allow user to go back to root
                if an_input == "/":
                    an_input = "home"

                # Process the input command
                self.queue = self.switch(an_input)

                if get_show_prompt() and an_input in ("login", "logout"):
                    return [an_input]

            except SystemExit:
                if not self.contains_keys(an_input):
                    logger.exception(
                        "The command '%s' doesn't exist on the %s menu.",
                        an_input,
                        self.PATH,
                    )
                console.print(
                    f"[red]The command '{an_input}' doesn't exist on the {self.PATH} menu.[/red]\n",
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
                    if not self.contains_keys(an_input) and an_input not in [
                        "exit",
                        "quit",
                        "help",
                    ]:
                        logger.warning("Replacing by %s", an_input)
                    console.print(f"[green]Replacing by '{an_input}'.[/green]\n")
                    self.queue.insert(0, an_input)
                else:
                    if (
                        self.TRY_RELOAD
                        and get_current_user().preferences.RETRY_WITH_LOAD
                    ):
                        console.print(f"\nTrying `load {an_input}`\n")
                        self.queue.insert(0, "load " + an_input)


class StockBaseController(BaseController, metaclass=ABCMeta):
    """Base controller class for stocks related menus."""

    def __init__(self, queue):
        """Instantiate the base class for Stock Controllers that use a load function."""
        super().__init__(queue)
        self.stock = pd.DataFrame()
        self.interval = "1440min"
        self.ticker = ""
        self.start = ""
        self.suffix = ""  # To hold suffix for Yahoo Finance
        self.add_info = stocks_helper.additional_info_about_ticker("")
        self.TRY_RELOAD = True
        self.USER_IMPORT_FILES = {
            filepath.name: filepath
            for file_type in ["csv"]
            for filepath in (
                get_current_user().preferences.USER_CUSTOM_IMPORTS_DIRECTORY / "stocks"
            ).rglob(f"*.{file_type}")
        }

    def call_load(self, other_args: List[str]):
        """Process load command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load stock ticker to perform analysis on. When the data source"
            + " is yf, an Indian ticker can be"
            + " loaded by using '.NS' at the end, e.g. 'SBIN.NS'. See available market in"
            + " https://help.yahoo.com/kb/exchanges-data-providers-yahoo-finance-sln2310.html.",
        )
        parser.add_argument(
            "-t",
            "--ticker",
            action="store",
            dest="ticker",
            required="-h" not in other_args and "--help" not in other_args,
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
            "-p",
            "--prepost",
            action="store_true",
            default=False,
            dest="prepost",
            help="Pre/After market hours. Only reflected in 'YahooFinance' intraday data.",
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
            "--performance",
            dest="performance",
            action="store_true",
            default=False,
            help="Show performance information.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if ns_parser.weekly and ns_parser.monthly:
                console.print(
                    "[red]Only one of monthly or weekly can be selected.[/red]."
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
                # This block makes sure that we only look for the file if the -f flag is used
                # Adding files in the argparse choices, will fail for the .exe even without -f
                file_location = self.USER_IMPORT_FILES.get(
                    ns_parser.filepath, ns_parser.filepath
                )
                df_stock_candidate = stocks_helper.load_custom(str(file_location))
                if df_stock_candidate.empty:
                    return
            is_df = isinstance(df_stock_candidate, pd.DataFrame)
            if not (
                (is_df and df_stock_candidate.empty)
                or (not is_df and not df_stock_candidate)
            ):
                self.stock = df_stock_candidate
                if (
                    ns_parser.interval == 1440
                    and not ns_parser.weekly
                    and not ns_parser.monthly
                    and ns_parser.filepath is None
                    and self.PATH == "/stocks/"
                    and ns_parser.performance
                ):
                    console.print()
                    stocks_helper.show_quick_performance(self.stock, ns_parser.ticker)
                if "." in ns_parser.ticker:
                    self.ticker, self.suffix = ns_parser.ticker.upper().split(".")
                    if "." not in self.ticker:
                        self.ticker = ns_parser.ticker.upper()
                else:
                    self.ticker = ns_parser.ticker.upper()
                    self.suffix = ""

                if ns_parser.source == "EODHD":
                    self.start = self.stock.index[0].to_pydatetime()
                elif ns_parser.source == "eodhd":
                    self.start = self.stock.index[0].to_pydatetime()
                else:
                    self.start = ns_parser.start
                self.interval = f"{ns_parser.interval}min"

                if self.PATH in ["/stocks/qa/"]:
                    self.stock["Returns"] = self.stock["Adj Close"].pct_change()
                    self.stock["LogRet"] = np.log(self.stock["Adj Close"]) - np.log(
                        self.stock["Adj Close"].shift(1)
                    )
                    self.stock["LogPrice"] = np.log(self.stock["Adj Close"])
                    self.stock = self.stock.rename(columns={"Adj Close": "AdjClose"})
                    self.stock = self.stock.dropna()
                    self.stock.columns = [x.lower() for x in self.stock.columns]
                    # pylint: disable=attribute-defined-outside-init
                    self.target = "returns" if not self.stock.empty else ""

                export_data(
                    ns_parser.export,
                    os.path.dirname(os.path.abspath(__file__)),
                    f"load_{self.ticker}",
                    self.stock.copy(),
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )


class CryptoBaseController(BaseController, metaclass=ABCMeta):
    """Base controller class for crypto related menus."""

    def __init__(self, queue):
        """Instantiate the base class for Crypto Controllers that use a load function."""
        super().__init__(queue)

        self.symbol = ""
        self.vs = ""
        self.current_df = pd.DataFrame()
        self.current_currency = ""
        self.source = ""
        self.current_interval = ""
        self.exchange = ""
        self.price_str = ""
        self.interval = ""
        self.resolution = "1D"
        self.TRY_RELOAD = True
        self.exchanges = cryptocurrency_helpers.get_exchanges_ohlc()

    def call_load(self, other_args):
        """Process load command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="""Load crypto currency to perform analysis on.
            Yahoo Finance is used as default source.
            Other sources can be used such as 'ccxt' or 'cg' with --source.
            If you select 'ccxt', you can then select any exchange with --exchange.
            You can also select a specific interval with --interval.""",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="Coin to get. Must be coin symbol (e.g., btc, eth)",
            dest="coin",
            type=str,
            required="-h" not in other_args and "--help" not in other_args,
        )

        parser.add_argument(
            "-s",
            "--start",
            type=valid_date,
            default=(datetime.now() - timedelta(days=1100)).strftime("%Y-%m-%d"),
            dest="start",
            help="The starting date (format YYYY-MM-DD) of the crypto",
        )

        parser.add_argument(
            "--exchange",
            help="Exchange to search",
            dest="exchange",
            type=str,
            default="binance",
            choices=self.exchanges,
        )

        parser.add_argument(
            "-e",
            "--end",
            type=valid_date,
            default=datetime.now().strftime("%Y-%m-%d"),
            dest="end",
            help="The ending date (format YYYY-MM-DD) of the crypto",
        )
        parser.add_argument(
            "-i",
            "--interval",
            action="store",
            dest="interval",
            type=str,
            default="1440",
            choices=["1", "5", "15", "30", "60", "240", "1440", "10080", "43200"],
            help="The interval of the crypto",
        )

        parser.add_argument(
            "--vs",
            help="Quote currency (what to view coin vs). e.g., usdc, usdt, ... if source is ccxt, usd, eur, ... otherwise",  # noqa
            dest="vs",
            default="usdt",
            type=str,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if (
                ns_parser.source in ("YahooFinance", "CoinGecko")
                and ns_parser.vs == "usdt"
            ):
                ns_parser.vs = "usd"
            if ns_parser.source == "YahooFinance" and ns_parser.interval in [
                "240",
                "10080",
                "43200",
            ]:
                console.print(
                    f"[red]YahooFinance does not support {ns_parser.interval}min interval[/red]"
                )
                return
            (self.current_df) = cryptocurrency_helpers.load(
                symbol=ns_parser.coin.lower(),
                to_symbol=ns_parser.vs,
                end_date=ns_parser.end.strftime("%Y-%m-%d"),
                start_date=ns_parser.start.strftime("%Y-%m-%d"),
                interval=ns_parser.interval,
                source=ns_parser.source,
                exchange=ns_parser.exchange,
            )
            if not self.current_df.empty:
                self.vs = ns_parser.vs
                self.exchange = ns_parser.exchange
                self.source = ns_parser.source
                self.current_interval = ns_parser.interval
                self.current_currency = ns_parser.vs
                self.symbol = ns_parser.coin.lower()
                self.data = (  # pylint: disable=attribute-defined-outside-init
                    self.current_df.copy()
                )
                cryptocurrency_helpers.show_quick_performance(
                    self.current_df,
                    self.symbol,
                    self.current_currency,
                    ns_parser.source,
                    ns_parser.exchange,
                    self.current_interval,
                )
                export_data(
                    ns_parser.export,
                    os.path.dirname(os.path.abspath(__file__)),
                    "load",
                    self.current_df.copy(),
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
