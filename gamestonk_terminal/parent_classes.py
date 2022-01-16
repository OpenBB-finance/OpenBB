"""Parent Classes"""
__docformat__ = "numpy"

from abc import ABCMeta, abstractmethod
import argparse
import re
import difflib
from typing import Union, List, Dict, Any

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.menu import session
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.decorators import try_except
from gamestonk_terminal.helper_funcs import system_clear, get_flair
from gamestonk_terminal.rich_config import console


controllers: Dict[str, Any] = {}


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
    ]

    CHOICES_COMMANDS: List[str] = []
    CHOICES_MENUS: List[str] = []

    PATH: str = ""

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
        if class_ins.PATH in controllers and arguments == 1 and gtff.REMEMBER_CONTEXTS:
            old_class = controllers[class_ins.PATH]
            old_class.queue = self.queue
            return old_class.menu()
        return class_ins(*args, **kwargs).menu()

    def save_class(self):
        """Saves the current instance of the class to be loaded later"""
        if gtff.REMEMBER_CONTEXTS:
            controllers[self.PATH] = self

    def custom_reset(self) -> List[str]:
        """This will be replaced by any children with custom_reset functions"""
        return []

    @abstractmethod
    def print_help(self) -> None:
        raise NotImplementedError("Must override print_help")

    @try_except
    def switch(self, an_input: str) -> List[str]:
        """Process and dispatch input

        Returns
        -------
        List[str]
            List of commands in the queue to execute
        """
        # Empty command
        if not an_input:
            console.print("")
            return self.queue

        # Navigation slash is being used
        if "/" in an_input:
            actions = an_input.split("/")

            # Absolute path is specified
            if not actions[0]:
                an_input = "home"
            # Relative path so execute first instruction
            else:
                an_input = actions[0]

            # Add all instructions to the queue
            for cmd in actions[1:][::-1]:
                if cmd:
                    self.queue.insert(0, cmd)

        (known_args, other_args) = self.parser.parse_known_args(an_input.split())

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

        return self.queue

    def call_cls(self, _) -> None:
        """Process cls command"""
        system_clear()

    def call_home(self, _) -> None:
        """Process home command"""
        self.save_class()
        for _ in range(self.PATH.count("/") - 1):
            self.queue.insert(0, "quit")

    def call_help(self, _) -> None:
        """Process help command"""
        self.print_help()

    def call_quit(self, _) -> None:
        """Process quit menu command"""
        self.save_class()
        console.print("")
        self.queue.insert(0, "quit")

    def call_exit(self, _) -> None:
        # Not sure how to handle controller loading here
        """Process exit terminal command"""
        for _ in range(self.PATH.count("/")):
            self.queue.insert(0, "quit")

    def call_reset(self, _) -> None:
        """Process reset command. If you would like to have customization in the
        reset process define a methom `custom_reset` in the child class.
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

    def menu(self, custom_path_menu_above: str = ""):
        an_input = "HELP_ME"

        while True:
            # There is a command in the queue
            if self.queue and len(self.queue) > 0:
                # If the command is quitting the menu we want to return in here
                if self.queue[0] in ("q", "..", "quit"):
                    console.print("")
                    # Go back to the root in order to go to the right directory because
                    # there was a jump between indirect menus
                    if custom_path_menu_above:
                        self.queue.insert(1, custom_path_menu_above)

                    if len(self.queue) > 1:
                        return self.queue[1:]

                    if gtff.ENABLE_EXIT_AUTO_HELP:
                        return ["help"]
                    return []

                # Consume 1 element from the queue
                an_input = self.queue[0]
                self.queue = self.queue[1:]

                # Print location because this was an instruction and we want user to know the action
                if an_input and an_input.split(" ")[0] in self.controller_choices:
                    console.print(f"{get_flair()} {self.path} $ {an_input}")

            # Get input command from user
            else:
                # Display help menu when entering on this menu from a level above
                if an_input == "HELP_ME":
                    self.print_help()

                try:
                    # Get input from user using auto-completion
                    if session and gtff.USE_PROMPT_TOOLKIT:
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
                console.print(
                    f"\nThe command '{an_input}' doesn't exist on the {self.path} menu.",
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

                    console.print(f" Replacing by '{an_input}'.")
                    self.queue.insert(0, an_input)
                else:
                    console.print("\n")
