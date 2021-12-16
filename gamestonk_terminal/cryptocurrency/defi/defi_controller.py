"""Defi Controller Module"""
__docformat__ = "numpy"

import argparse
from typing import List
from prompt_toolkit.completion import NestedCompleter

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
    llama_view,
    substack_view,
    graph_view,
)


class DefiController:
    """Defi Controller class"""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
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

    def __init__(self):
        """Constructor"""
        self.defi_parser = argparse.ArgumentParser(add_help=False, prog="defi")
        self.defi_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    def switch(self, an_input: str):
        """Process and dispatch input

        Parameters
        -------
        an_input : str
            string with input arguments

        Returns
        -------
        True, False or None
            False - quit the menu
            True - quit the program
            None - continue in the menu
        """

        # Empty command
        if not an_input:
            print("")
            return None

        (known_args, other_args) = self.defi_parser.parse_known_args(an_input.split())

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            system_clear()
            return None

        return getattr(
            self,
            "call_" + known_args.cmd,
            lambda _: "Command not recognized!",
        )(other_args)

    def call_help(self, *_):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

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
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
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

        if not ns_parser:
            return

        defipulse_view.display_defipulse(
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            export=ns_parser.export,
        )

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
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: tvl",
            default="tvl",
            choices=[
                "tvl",
                "symbol",
                "category",
                "chains",
                "change_1h",
                "change_1d",
                "change_7d",
                "tvl",
            ],
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

        if not ns_parser:
            return

        llama_view.display_defi_protocols(
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            description=ns_parser.description,
            export=ns_parser.export,
        )

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
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
            default=10,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if not ns_parser:
            return

        llama_view.display_defi_tvl(top=ns_parser.top, export=ns_parser.export)

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
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
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

        if not ns_parser:
            return

        defirate_view.display_funding_rates(
            top=ns_parser.top, current=ns_parser.current, export=ns_parser.export
        )

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
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
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

        if not ns_parser:
            return

        defirate_view.display_borrow_rates(
            top=ns_parser.top, current=ns_parser.current, export=ns_parser.export
        )

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
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
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

        if not ns_parser:
            return

        defirate_view.display_lending_rates(
            top=ns_parser.top, current=ns_parser.current, export=ns_parser.export
        )

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
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
            default=10,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if not ns_parser:
            return

        substack_view.display_newsletters(top=ns_parser.top, export=ns_parser.export)

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
            choices=[
                "index",
                "symbol",
                "name",
                "tradeVolumeUSD",
                "totalLiquidity",
                "txCount",
            ],
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

        if not ns_parser:
            return

        graph_view.display_uni_tokens(
            skip=ns_parser.skip,
            limit=ns_parser.limit,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            export=ns_parser.export,
        )

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

        if not ns_parser:
            return

        graph_view.display_uni_stats(export=ns_parser.export)

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
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="Number of records",
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
            choices=[
                "created",
                "pair",
                "token0",
                "token1",
                "volumeUSD",
                "txCount",
                "totalSupply",
            ],
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

        if not ns_parser:
            return

        graph_view.display_recently_added(
            top=ns_parser.top,
            days=ns_parser.days,
            min_volume=ns_parser.vol,
            min_tx=ns_parser.tx,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            export=ns_parser.export,
        )

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
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="Number of records",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: volumeUSD",
            default="volumeUSD",
            choices=[
                "volumeUSD",
                "token0.name",
                "token0.symbol",
                "token1.name",
                "token1.symbol",
                "volumeUSD",
                "txCount",
            ],
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

        if not ns_parser:
            return

        graph_view.display_uni_pools(
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            export=ns_parser.export,
        )

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
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="Number of records",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: timestamp",
            default="timestamp",
            choices=["timestamp", "token0", "token1", "amountUSD"],
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

        if not ns_parser:
            return

        graph_view.display_last_uni_swaps(
            top=ns_parser.top,
            sortby=ns_parser.sortby,
            descend=ns_parser.descend,
            export=ns_parser.export,
        )

    def print_help(self):
        """Print help"""
        help_text = """
Decentralized Finance:
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program

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
    swaps         Recent swaps done on Uniswap"""
        print(help_text, "\n")


def menu():
    """Defi Menu"""
    defi_controller = DefiController()
    defi_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in defi_controller.CHOICES}
            )
            an_input = session.prompt(
                f"{get_flair()} (crypto)>(defi)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(defi)> ")

        try:
            process_input = defi_controller.switch(an_input)
        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if process_input is False:
            return False

        if process_input is True:
            return True
