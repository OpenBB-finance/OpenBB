"""Defi Controller Module"""
__docformat__ = "numpy"

import argparse
import difflib

from typing import List, Union
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.cryptocurrency.defi import graph_model
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    check_positive,
    try_except,
    system_clear,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
)

from gamestonk_terminal.cryptocurrency.defi import (
    defirate_view,
    defipulse_view,
    llama_model,
    llama_view,
    substack_view,
    graph_view,
)


class DefiController:
    """Defi Controller class"""

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
        "dpi",
        "funding",
        "lending",
        "tvl",
        "borrow",
        "llama",
        "newsletter",
        "tokens",
        "pairs",
        "pools",
        "swaps",
        "stats",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        self.defi_parser = argparse.ArgumentParser(add_help=False, prog="defi")
        self.defi_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.completer: Union[None, NestedCompleter] = None
        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["llama"]["-s"] = {c: {} for c in llama_model.LLAMA_FILTERS}
            choices["tokens"]["-s"] = {c: {} for c in graph_model.TOKENS_FILTERS}
            choices["pairs"]["-s"] = {c: {} for c in graph_model.PAIRS_FILTERS}
            choices["pools"]["-s"] = {c: {} for c in graph_model.POOLS_FILTERS}
            choices["swaps"]["-s"] = {c: {} for c in graph_model.SWAPS_FILTERS}
            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def switch(self, an_input: str):
        """Process and dispatch input

        Parameters
        -------
        an_input : str
            string with input arguments

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

        (known_args, other_args) = self.defi_parser.parse_known_args(an_input.split())

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
            return self.queue
        return ["quit", "quit", "quit"]

    def call_reset(self, _):
        """Process reset command"""
        if len(self.queue) > 0:
            self.queue.insert(0, "defi")
            self.queue.insert(0, "crypto")
            self.queue.insert(0, "reset")
            self.queue.insert(0, "quit")
            self.queue.insert(0, "quit")
            return self.queue
        return ["quit", "quit", "reset", "crypto", "defi"]

    @try_except
    def call_dpi(self, other_args: List[str]):
        """Process dpi command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dpi",
            description="""
                Displays DeFi Pulse crypto protocols.
                [Source: https://defipulse.com/]
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=["Rank", "Name", "Chain", "Category", "TVL", "Change_1D"],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            defipulse_view.display_defipulse(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )
        return self.queue

    @try_except
    def call_llama(self, other_args: List[str]):
        """Process llama command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="llama",
            description="""
                Display information about listed DeFi Protocols on DeFi Llama.
                [Source: https://docs.llama.fi/api]
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: tvl",
            default="tvl",
            choices=llama_model.LLAMA_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        parser.add_argument(
            "--desc",
            action="store_false",
            help="Flag to display description of protocol",
            dest="description",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            llama_view.display_defi_protocols(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                description=ns_parser.description,
                export=ns_parser.export,
            )
        return self.queue

    @try_except
    def call_tvl(self, other_args: List[str]):
        """Process tvl command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tvl",
            description="""
                Displays historical values of the total sum of TVLs from all listed protocols.
                [Source: https://docs.llama.fi/api]
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=10,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            llama_view.display_defi_tvl(top=ns_parser.limit, export=ns_parser.export)
        return self.queue

    @try_except
    def call_funding(self, other_args: List[str]):
        """Process funding command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="funding",
            description="""
                Display Funding rates.
                [Source: https://defirate.com/]
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=10,
        )

        parser.add_argument(
            "--current",
            action="store_false",
            default=True,
            dest="current",
            help="Show Current Funding Rates or Last 30 Days Average",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            defirate_view.display_funding_rates(
                top=ns_parser.limit, current=ns_parser.current, export=ns_parser.export
            )
        return self.queue

    @try_except
    def call_borrow(self, other_args: List[str]):
        """Process borrow command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="borrow",
            description="""
                 Display DeFi borrow rates.
                 [Source: https://defirate.com/]
             """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=10,
        )

        parser.add_argument(
            "--current",
            action="store_false",
            default=True,
            dest="current",
            help="Show Current Borrow Rates or Last 30 Days Average",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            defirate_view.display_borrow_rates(
                top=ns_parser.limit, current=ns_parser.current, export=ns_parser.export
            )
        return self.queue

    @try_except
    def call_lending(self, other_args: List[str]):
        """Process lending command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lending",
            description="""
                 Display DeFi lending rates.
                 [Source: https://defirate.com/]
             """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=15,
        )

        parser.add_argument(
            "--current",
            action="store_false",
            default=True,
            dest="current",
            help="Show Current Lending Rates or Last 30 Days Average",
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            defirate_view.display_lending_rates(
                top=ns_parser.limit, current=ns_parser.current, export=ns_parser.export
            )
        return self.queue

    @try_except
    def call_newsletter(self, other_args: List[str]):
        """Process newsletter command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="newsletter",
            description="""
                Display DeFi related substack newsletters.
                [Source: substack.com]
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=10,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            substack_view.display_newsletters(
                top=ns_parser.limit, export=ns_parser.export
            )
        return self.queue

    @try_except
    def call_tokens(self, other_args: List[str]):
        """Process tokens command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tokens",
            description="""
                Display tokens trade-able on Uniswap DEX
                [Source: https://thegraph.com/en/]
            """,
        )

        parser.add_argument(
            "--skip",
            dest="skip",
            type=check_positive,
            help="Number of records to skip",
            default=0,
        )

        parser.add_argument(
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=20,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: index",
            default="index",
            choices=graph_model.TOKENS_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            graph_view.display_uni_tokens(
                skip=ns_parser.skip,
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )
        return self.queue

    @try_except
    def call_stats(self, other_args: List[str]):
        """Process stats command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="stats",
            description="""
                 Display base statistics about Uniswap DEX.
                 [Source: https://thegraph.com/en/]
             """,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            graph_view.display_uni_stats(export=ns_parser.export)
        return self.queue

    @try_except
    def call_pairs(self, other_args: List[str]):
        """Process pairs command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pairs",
            description="""
                Displays Lastly added pairs on Uniswap DEX.
                [Source: https://thegraph.com/en/]
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=10,
        )

        parser.add_argument(
            "-v",
            "--vol",
            dest="vol",
            type=check_positive,
            help="Minimum trading volume",
            default=100,
        )

        parser.add_argument(
            "-tx",
            "--tx",
            dest="tx",
            type=check_positive,
            help="Minimum number of transactions",
            default=100,
        )

        parser.add_argument(
            "--days",
            dest="days",
            type=check_positive,
            help="Number of days the pair has been active,",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: created",
            default="created",
            choices=graph_model.PAIRS_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            graph_view.display_recently_added(
                top=ns_parser.limit,
                days=ns_parser.days,
                min_volume=ns_parser.vol,
                min_tx=ns_parser.tx,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )
        return self.queue

    @try_except
    def call_pools(self, other_args: List[str]):
        """Process pools command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pairs",
            description="""
                Display uniswap pools by volume.
                [Source: https://thegraph.com/en/]
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: volumeUSD",
            default="volumeUSD",
            choices=graph_model.POOLS_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            graph_view.display_uni_pools(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )
        return self.queue

    @try_except
    def call_swaps(self, other_args: List[str]):
        """Process swaps command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pairs",
            description="""
                Display last swaps done on Uniswap DEX.
                [Source: https://thegraph.com/en/]
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: timestamp",
            default="timestamp",
            choices=graph_model.SWAPS_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            graph_view.display_last_uni_swaps(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )
        return self.queue

    def print_help(self):
        """Print help"""
        help_text = """
Decentralized Finance Menu:

Overview:
    llama         DeFi protocols listed on DeFi Llama
    tvl           Total value locked of DeFi protocols
    newsletter    Recent DeFi related newsletters
    dpi           DeFi protocols listed on DefiPulse
    funding       Funding reates - current or last 30 days average
    borrow        DeFi borrow rates - current or last 30 days average
    lending       DeFi ending rates - current or last 30 days average
Uniswap:
    tokens        Tokens trade-able on Uniswap
    stats         Base statistics about Uniswap
    pairs         Recently added pairs on Uniswap
    pools         Pools by volume on Uniswap
    swaps         Recent swaps done on Uniswap
"""
        print(help_text)


def menu(queue: List[str] = None):
    """Defi Menu"""
    defi_controller = DefiController(queue=queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if defi_controller.queue and len(defi_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if defi_controller.queue[0] in ("q", "..", "quit"):
                if len(defi_controller.queue) > 1:
                    return defi_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = defi_controller.queue[0]
            defi_controller.queue = defi_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in defi_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /crypto/defi/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                defi_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and defi_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /crypto/defi/ $ ",
                    completer=defi_controller.completer,
                    search_ignore_case=True,
                )
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /crypto/defi/ $ ")

        try:
            # Process the input command
            defi_controller.queue = defi_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/options menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                defi_controller.CHOICES,
                n=1,
                cutoff=0.7,
            )
            if similar_cmd:
                if " " in an_input:
                    candidate_input = (
                        f"{similar_cmd[0]} {' '.join(an_input.split(' ')[1:])}"
                    )
                else:
                    candidate_input = similar_cmd[0]

                if candidate_input == an_input:
                    an_input = ""
                    defi_controller.queue = []
                    print("\n")
                    continue

                print(f" Replacing by '{an_input}'.")
                defi_controller.queue.insert(0, an_input)
            else:
                print("\n")
                an_input = ""
                defi_controller.queue = []
