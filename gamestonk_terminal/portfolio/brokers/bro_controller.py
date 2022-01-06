__docformat__ = "numpy"

# pylint: disable=R1710

import argparse
from typing import List, Union, Set
import difflib
from prompt_toolkit.completion import NestedCompleter


from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair, system_clear
from gamestonk_terminal.menu import session

from gamestonk_terminal.portfolio.brokers.ally import ally_controller
from gamestonk_terminal.portfolio.brokers.degiro import degiro_controller
from gamestonk_terminal.portfolio.brokers.robinhood import robinhood_controller
from gamestonk_terminal.portfolio.brokers.coinbase import coinbase_controller


class BrokersController:
    """Brokers Controller"""

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
    CHOICES_COMMANDS: List = []
    BROKERS = ["cb", "ally", "rh", "degiro"]

    CHOICES += BROKERS + CHOICES_COMMANDS

    def __init__(self, queue: List[str] = None):
        self.bro_parser = argparse.ArgumentParser(add_help=False, prog="bro")
        self.bro_parser.add_argument("cmd", choices=self.CHOICES)
        self.broker_list: Set = set()
        self.merged_holdings = None
        if queue:
            self.queue = queue
        else:
            self.queue = list()

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_string = """

Brokers:
>   ally         Ally Invest Menu
>   degiro       Degiro Menu
>   rh           Robinhood Menu

Crypto Brokers:
>   cb           Coinbase Pro Menu
    """
        print(help_string)

    def switch(self, an_input: str):
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

        (known_args, other_args) = self.bro_parser.parse_known_args(an_input.split())

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

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_help(self, _):
        """Process help command"""
        self.print_help()

    def call_quit(self, _):
        """Process quit menu command"""
        print("")
        self.queue.insert(0, "quit")

    def call_exit(self, _):
        """Process exit terminal command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_reset(self, _):
        """Process reset command"""
        self.queue.insert(0, "bro")
        self.queue.insert(0, "portfolio")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    def call_degiro(self, _):
        """Process degiro command."""
        self.queue = degiro_controller.menu(self.queue)

    def call_ally(self, _):
        """Process ally command."""
        self.queue = ally_controller.menu(self.queue)

    def call_rh(self, _):
        """Process rh command."""
        self.queue = robinhood_controller.menu(self.queue)

    def call_cb(self, _):
        """Process degiro command."""
        self.queue = coinbase_controller.menu(self.queue)

    # TODO: Consistent way of merging across brokers including crypto
    # def call_login(self, other_args):
    #    """Process login command"""
    #    logged_in = False
    #    if not other_args:
    #        print("Please enter brokers you wish to login to")
    #        print("")
    #        return
    #    for broker in other_args:
    #        if broker in self.BROKERS:
    #            api = broker + "_api"
    #            try:
    #                # pylint: disable=eval-used
    #                eval(api + ".login()")
    #                self.broker_list.add(broker)
    #                logged_in = True
    #            except Exception as e:
    #                print("")
    #                print(f"Error at broker : {broker}")
    #                print(e)
    #                print("Make sure credentials are defined in config_terminal.py ")
    #                print("")
    #        else:
    #            print(f"{broker} not supported")


def menu(queue: List[str] = None):
    """Brokers Menu"""
    print(
        "\nUSE THIS MENU AT YOUR OWN DISCRETION\n"
        "   - This menu is the only one in the entire repository that has access to your broker accounts. "
        "If you have provided your login details on the config_terminal.py file"
        "   - We review the code thoroughly from each contributor, hence, we can ensure that our codebase "
        "does not take advantage of your data.\n"
        "   - HOWEVER, our project imports almost 200 different open source python modules. Therefore, it "
        "is impossible for us to check the coding standards and security of each of these modules. "
        "Hence why adding this disclaimer here."
    )

    bro_controller = BrokersController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if bro_controller.queue and len(bro_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if bro_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(bro_controller.queue) > 1:
                    return bro_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = bro_controller.queue[0]
            bro_controller.queue = bro_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in bro_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /portfolio/bro/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                bro_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and bro_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /portfolio/bro/ $ ",
                        completer=bro_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /portfolio/bro/ $ ")

        try:
            # Process the input command
            bro_controller.queue = bro_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /portfolio/bro menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                bro_controller.CHOICES,
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
                        bro_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                bro_controller.queue.insert(0, an_input)
            else:
                print("\n")
