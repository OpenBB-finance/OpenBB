"""Parent Classes"""
__docformat__ = "numpy"

from abc import ABCMeta, abstractmethod
import argparse
import difflib
from typing import Union, List, Callable

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.menu import session
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.decorators import try_except
from gamestonk_terminal.helper_funcs import system_clear, get_flair

# Do before merging
# add try_except to all switches


class BaseController:
    __metaclass__ = ABCMeta

    CHOICES = [
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

    def __init__(
        self,
        path: str,
        queue: List[str] = None,
        dynamic_completer: Callable[..., NestedCompleter] = None,
    ) -> None:
        """
        This is the base class for any controller in the codebase. Use it to
        quickly create a working context and menu.

        path: str
            Where the current context is located in the terminal
        queue: List[str]
            The current queue
        dynamic_completer:
            Allows a function for dynamic completing
        """
        self.choices = self.CHOICES
        self.path = path
        self.dynamic_completer = dynamic_completer
        self.PATH = [x for x in path.split("/") if x != ""]

        name = self.PATH[-1] if path != "/" else "terminal"
        self.parser = argparse.ArgumentParser(add_help=False, prog=name)
        self.parser.add_argument("cmd", choices=self.CHOICES)

        self.completer: Union[None, NestedCompleter] = None

        if path != "/":
            self.queue = queue if queue else list()

    def check_path(self, path: str) -> bool:
        pass

    def custom_reset(self) -> None:
        """
        This will be replace by any children with custom_reset functions

        When you replace this function be careful where insert the function.
        Making the insert parameter 0 makes it the first command executed, to
        make the command the last one executed set it to the number of levels
        it is deep multiplied by two plus one. For example, If your new context
        was /stocks/network/ it would be 2 X 2 + 1 or 5.
        """

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
            print("")
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

    def call_cls(self, _):
        """Process cls command"""
        system_clear()

    def call_home(self, _) -> None:
        """Process home command"""
        for _ in range(self.path.count("/") - 1):
            self.queue.insert(0, "quit")

    def call_help(self, _) -> None:
        """Process help command"""
        self.print_help()

    def call_quit(self, _) -> None:
        """Process quit menu command"""
        print("")
        self.queue.insert(0, "quit")

    def call_exit(self, _) -> None:
        """Process exit terminal command"""
        for _ in range(self.path.count("/")):
            self.queue.insert(0, "quit")

    def call_reset(self, _) -> None:
        """Process reset command. If you would like to have customization in the
        reset process define a methom `custom_reset` in the child class.
        """
        if self.path != "/":
            for val in self.PATH[::-1]:
                self.queue.insert(0, val)
            self.queue.insert(0, "reset")
            for _ in range(len(self.PATH)):
                self.queue.insert(0, "quit")
            self.custom_reset()

    def menu(self) -> List[str]:
        an_input = "HELP_ME"

        while True:
            # There is a command in the queue
            if self.queue and len(self.queue) > 0:
                # If the command is quitting the menu we want to return in here
                if self.queue[0] in ("q", "..", "quit"):
                    print("")
                    if len(self.queue) > 1:
                        return self.queue[1:]
                    return []

                # Consume 1 element from the queue
                an_input = self.queue[0]
                self.queue = self.queue[1:]

                # Print location because this was an instruction and we want user to know the action
                if an_input and an_input.split(" ")[0] in self.choices:
                    print(f"{get_flair()} {self.path} $ {an_input}")

            # Get input command from user
            else:
                # Display help menu when entering on this menu from a level above
                if an_input == "HELP_ME":
                    self.print_help()

                # Get input from user using auto-completion
                if session and gtff.USE_PROMPT_TOOLKIT:
                    # Possible arguments is not yet finalized
                    if not self.completer and self.dynamic_completer:
                        # Complete dynamic arguments that change at each iteration
                        self.completer = self.dynamic_completer(self)
                    try:
                        an_input = session.prompt(
                            f"{get_flair()} {self.path} $ ",
                            completer=self.completer,
                            search_ignore_case=True,
                        )
                    except KeyboardInterrupt:
                        # Exit in case of keyboard interrupt
                        an_input = "exit"
                # Get input from user without auto-completion
                else:
                    an_input = input(f"{get_flair()} {self.path} $ ")

            try:
                # Process the input command
                self.queue = self.switch(an_input)

            except SystemExit:
                print(
                    f"\nThe command '{an_input}' doesn't exist on the {self.PATH[:-1]} menu.",
                    end="",
                )
                similar_cmd = difflib.get_close_matches(
                    an_input.split(" ")[0] if " " in an_input else an_input,
                    self.CHOICES,
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
                            print("\n")
                            continue
                        an_input = candidate_input
                    else:
                        an_input = similar_cmd[0]

                    print(f" Replacing by '{an_input}'.")
                    self.queue.insert(0, an_input)
                else:
                    print("\n")
