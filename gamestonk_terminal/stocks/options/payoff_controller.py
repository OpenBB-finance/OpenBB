""" Payoff Controller Module """
__docformat__ = "numpy"

import argparse
import difflib
from typing import List, Dict, Union
from prompt_toolkit.completion import NestedCompleter
from colorama import Style
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    check_non_negative,
    get_flair,
    parse_known_args_and_warn,
    try_except,
    system_clear,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.stocks.options.yfinance_model import get_option_chain, get_price
from gamestonk_terminal.stocks.options.yfinance_view import plot_payoff


# pylint: disable=R0902


class PayoffController:
    """Payoff Controller class"""

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
    CHOICES_COMMANDS = [
        "list",
        "add",
        "rmv",
        "pick",
        "plot",
        "sop",
    ]
    CHOICES += CHOICES_COMMANDS

    underlying_asset_choices = ["long", "short", "none"]

    def __init__(self, ticker: str, expiration: str, queue: List[str] = None):
        """Construct"""
        self.payoff_parser = argparse.ArgumentParser(add_help=False, prog="payoff")
        self.payoff_parser.add_argument("cmd", choices=self.CHOICES)

        self.chain = get_option_chain(ticker, expiration)
        self.calls = list(
            zip(
                self.chain.calls["strike"].tolist(),
                self.chain.calls["lastPrice"].tolist(),
            )
        )
        self.puts = list(
            zip(
                self.chain.puts["strike"].tolist(),
                self.chain.puts["lastPrice"].tolist(),
            )
        )
        self.ticker = ticker
        self.current_price = get_price(ticker)
        self.expiration = expiration
        self.options: List[Dict[str, str]] = []
        self.underlying = 0

        self.call_index_choices = range(len(self.calls))
        self.put_index_choices = range(len(self.puts))

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:

            self.choices: dict = {c: {} for c in self.CHOICES}
            self.choices["pick"] = {c: {} for c in self.underlying_asset_choices}
            self.choices["add"] = {
                str(c): {} for c in list(range(max(len(self.puts), len(self.calls))))
            }

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        if self.underlying == 1:
            text = "Long"
        elif self.underlying == 0:
            text = "None"
        elif self.underlying == -1:
            text = "Short"

        help_text = f"""
Ticker: {self.ticker or None}
Expiry: {self.expiration or None}

    pick          long, short, or none (default) underlying asset

Underlying Asset: {text}

    list          list available strike prices for calls and puts

    add           add option to the list of the options to be plotted{Style.DIM if not self.options else ""}
    rmv           remove option from the list of the options to be plotted{Style.RESET_ALL}

    sop           selected options
    plot          show the option payoff diagram
        """
        print(help_text)

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

        (known_args, other_args) = self.payoff_parser.parse_known_args(an_input.split())

        # Redirect commands to their correct functions
        if known_args.cmd:
            if known_args.cmd in ("..", "q"):
                known_args.cmd = "quit"
            elif known_args.cmd in ("?", "h"):
                known_args.cmd = "help"
            elif known_args.cmd == "r":
                known_args.cmd = "reset"

        return getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

    def call_cls(self, _):
        """Process cls command"""
        system_clear()
        return self.queue

    def call_home(self, _):
        """Process home command"""
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")
        return self.queue

    def call_help(self, _):
        """Process help command"""
        self.print_help()
        return self.queue

    def call_quit(self, _):
        """Process quit menu command"""
        print("")
        if len(self.queue) > 0:
            self.queue.insert(0, "quit")
            return self.queue
        return ["quit"]

    def call_exit(self, _):
        """Process exit terminal command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            return self.queue
        return ["quit", "quit", "quit", "quit"]

    def call_reset(self, _):
        """Process reset command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "payoff")
            if self.expiration:
                self.queue.insert(0, f"exp {self.expiration}")
            if self.ticker:
                self.queue.insert(0, f"load {self.ticker}")
            self.queue.insert(0, "options")
            self.queue.insert(0, "stocks")
            self.queue.insert(0, "reset")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            return self.queue

        reset_commands = ["quit", "quit", "quit", "reset", "stocks", "options"]
        if self.ticker:
            reset_commands.append(f"load {self.ticker}")
        if self.expiration:
            reset_commands.append(f"exp -d {self.expiration}")
        reset_commands.append("payoff")

        return reset_commands

    @try_except
    def call_list(self, other_args):
        """Lists available calls and puts"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="list",
            description="""Lists available calls and puts.""",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            length = max(len(self.calls), len(self.puts)) - 1
            print("#\tcall\tput")
            for i in range(length):
                call = self.calls[i][0] if i < len(self.calls) else ""
                put = self.puts[i][0] if i < len(self.puts) else ""
                print(f"{i}\t{call}\t{put}")
            print("")

        return self.queue

    @try_except
    def call_add(self, other_args: List[str]):
        """Process add command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="add",
            description="""Add options to the diagram.""",
        )
        parser.add_argument(
            "-p",
            "--put",
            dest="put",
            action="store_true",
            help="buy a put instead of a call",
            default=False,
        )
        parser.add_argument(
            "-s",
            "--short",
            dest="short",
            action="store_true",
            help="short the option instead of buying it",
            default=False,
        )
        parser.add_argument(
            "-i",
            "--index",
            dest="index",
            type=check_non_negative,
            help="list index of the option",
            required="-h" not in other_args and "-k" not in other_args,
            choices=self.put_index_choices
            if "-p" in other_args
            else self.call_index_choices,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            opt_type = "put" if ns_parser.put else "call"
            sign = -1 if ns_parser.short else 1
            options_list = self.puts if ns_parser.put else self.calls

            if ns_parser.index < len(options_list):
                strike = options_list[ns_parser.index][0]
                cost = options_list[ns_parser.index][1]

                option = {
                    "type": opt_type,
                    "sign": sign,
                    "strike": strike,
                    "cost": cost,
                }
                self.options.append(option)

                print("#\tType\tHold\tStrike\tCost")
                for i, o in enumerate(self.options):
                    asset: str = "Long" if o["sign"] == 1 else "Short"
                    print(f"{i}\t{o['type']}\t{asset}\t{o['strike']}\t{o['cost']}")
                print("")

            else:
                print("Please use a valid index\n")

        return self.queue

    @try_except
    def call_rmv(self, other_args: List[str]):
        """Process rmv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rmv",
            description="""Remove one of the options to be shown in the payoff.""",
        )
        parser.add_argument(
            "-i",
            "--index",
            dest="index",
            type=check_non_negative,
            help="index of the option to remove",
            required=bool("-h" not in other_args and len(self.options) > 0),
            choices=range(len(self.options)),
        )
        parser.add_argument(
            "-a",
            "--all",
            dest="all",
            action="store_true",
            help="remove all of the options",
            default=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if self.options:
                if ns_parser.all:
                    self.options = []
                else:
                    if ns_parser.index < len(self.options):
                        del self.options[ns_parser.index]
                    else:
                        print("Please use a valid index.\n")

                print("#\tType\tHold\tStrike\tCost")
                for i, o in enumerate(self.options):
                    sign = "Long" if o["sign"] == 1 else "Short"
                    print(f"{i}\t{o['type']}\t{sign}\t{o['strike']}\t{o['cost']}")
                print("")
        else:
            print("No options have been selected, removing them is not possible\n")

        return self.queue

    def call_pick(self, other_args: List[str]):
        """Process pick command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="long",
            description="This function plots option payoff diagrams",
        )
        parser.add_argument(
            "-t",
            "--type",
            dest="underlyingtype",
            type=str,
            help="Choose what you would like to do with the underlying asset",
            required="-h" not in other_args,
            choices=self.underlying_asset_choices,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.underlyingtype == "long":
                self.underlying = 1
            elif ns_parser.underlyingtype == "none":
                self.underlying = 0
            elif ns_parser.underlyingtype == "short":
                self.underlying = -1

        print("")
        return self.queue

    @try_except
    def call_sop(self, other_args):
        """Process sop command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sop",
            description="Displays selected option",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            print("#\tType\tHold\tStrike\tCost")
            for i, o in enumerate(self.options):
                sign = "Long" if o["sign"] == 1 else "Short"
                print(f"{i}\t{o['type']}\t{sign}\t{o['strike']}\t{o['cost']}")
            print("")

        return self.queue

    @try_except
    def call_plot(self, other_args):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="This function plots option payoff diagrams",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            plot_payoff(
                self.current_price,
                self.options,
                self.underlying,
                self.ticker,
                self.expiration,
            )

        return self.queue


def menu(ticker: str, expiration: str, queue: List[str] = None):
    """Payoff Menu"""
    payoff_controller = PayoffController(ticker, expiration, queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if payoff_controller.queue and len(payoff_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if payoff_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(payoff_controller.queue) > 1:
                    return payoff_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = payoff_controller.queue[0]
            payoff_controller.queue = payoff_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if (
                an_input
                and an_input.split(" ")[0] in payoff_controller.CHOICES_COMMANDS
            ):
                print(f"{get_flair()} /stocks/options/payoff/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                payoff_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and payoff_controller.choices:
                if payoff_controller.options:
                    payoff_controller.choices["rmv"] = {
                        str(c): {} for c in range(len(payoff_controller.options))
                    }
                completer = NestedCompleter.from_nested_dict(payoff_controller.choices)
                an_input = session.prompt(
                    f"{get_flair()} /stocks/options/payoff/ $ ",
                    completer=completer,
                    search_ignore_case=True,
                )
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /stocks/options/payoff/ $ ")

        try:
            # Process the input command
            payoff_controller.queue = payoff_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/options/payoff menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                payoff_controller.CHOICES,
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
                        payoff_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                payoff_controller.queue.insert(0, an_input)
            else:
                print("\n")
