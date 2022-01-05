"""Onchain Controller Module"""
__docformat__ = "numpy"

# pylint: disable=C0302

import argparse
from datetime import datetime, timedelta
import difflib
from typing import List, Union

from colorama.ansi import Style
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal.cryptocurrency.due_diligence.glassnode_model import (
    GLASSNODE_SUPPORTED_HASHRATE_ASSETS,
    INTERVALS,
)
from gamestonk_terminal.cryptocurrency.due_diligence.glassnode_view import (
    display_hashrate,
)

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    get_flair,
    parse_known_args_and_warn,
    check_positive,
    check_int_range,
    try_except,
    system_clear,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    valid_date,
)

from gamestonk_terminal.cryptocurrency.onchain import (
    ethgasstation_view,
    ethplorer_model,
    whale_alert_model,
    whale_alert_view,
    ethplorer_view,
    bitquery_view,
    bitquery_model,
)


class OnchainController:
    """Onchain Controller class"""

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

    SPECIFIC_CHOICES = {
        "account": [
            "balance",
            "hist",
        ],
        "token": [
            "info",
            "th",
            "prices",
            "holders",
        ],
        "tx": ["tx"],
    }

    CHOICES_COMMANDS = [
        "hr",
        "gwei",
        "whales",
        "balance",
        "top",
        "holders",
        "tx",
        "hist",
        "info",
        "th",
        "prices",
        "address",
        "lt",
        "dvcp",
        "tv",
        "ueat",
        "ttcp",
        "baas",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        self.onchain_parser = argparse.ArgumentParser(add_help=False, prog="onchain")
        self.onchain_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.address = ""
        self.address_type = ""

        self.completer: Union[None, NestedCompleter] = None
        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.CHOICES}
            choices["whales"]["-s"] = {c: None for c in whale_alert_model.FILTERS}
            choices["hr"] = {c: None for c in GLASSNODE_SUPPORTED_HASHRATE_ASSETS}
            choices["hr"]["-c"] = {c: None for c in GLASSNODE_SUPPORTED_HASHRATE_ASSETS}
            choices["hr"]["--coin"] = {
                c: None for c in GLASSNODE_SUPPORTED_HASHRATE_ASSETS
            }
            choices["hr"]["-i"] = {c: None for c in INTERVALS}
            choices["ttcp"] = {c: None for c in bitquery_model.DECENTRALIZED_EXCHANGES}
            choices["baas"]["-c"] = {c: None for c in bitquery_model.POSSIBLE_CRYPTOS}
            choices["baas"]["--coin"] = {
                c: None for c in bitquery_model.POSSIBLE_CRYPTOS
            }
            choices["balance"]["-s"] = {
                c: None for c in ethplorer_model.BALANCE_FILTERS
            }
            choices["holders"]["-s"] = {
                c: None for c in ethplorer_model.HOLDERS_FILTERS
            }
            choices["hist"]["-s"] = {c: None for c in ethplorer_model.HIST_FILTERS}
            choices["top"]["-s"] = {c: None for c in ethplorer_model.TOP_FILTERS}
            choices["th"]["-s"] = {c: None for c in ethplorer_model.TH_FILTERS}
            choices["prices"]["-s"] = {c: None for c in ethplorer_model.PRICES_FILTERS}
            choices["lt"]["-s"] = {c: None for c in bitquery_model.LT_FILTERS}
            choices["tv"]["-s"] = {c: None for c in bitquery_model.LT_FILTERS}
            choices["ueat"]["-s"] = {c: None for c in bitquery_model.UEAT_FILTERS}
            choices["ueat"]["-i"] = {c: None for c in bitquery_model.INTERVALS}
            choices["dvcp"]["-s"] = {c: None for c in bitquery_model.DVCP_FILTERS}
            choices["lt"]["-k"] = {c: None for c in bitquery_model.LT_KIND}
            choices["lt"]["-vs"] = {c: None for c in bitquery_model.CURRENCIES}
            choices["ttcp"] = {c: None for c in bitquery_model.DECENTRALIZED_EXCHANGES}
            choices["ttcp"]["-s"] = {c: None for c in bitquery_model.TTCP_FILTERS}
            choices["baas"]["-s"] = {c: None for c in bitquery_model.BAAS_FILTERS}
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

        (known_args, other_args) = self.onchain_parser.parse_known_args(
            an_input.split()
        )

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
        self.queue.insert(0, "onchain")
        self.queue.insert(0, "crypto")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

    @try_except
    def call_hr(self, other_args: List[str]):
        """Process hr command"""

        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="hr",
            description="""
                Display mean hashrate for a certain blockchain (ETH or BTC)
                [Source: https://glassnode.org]
            """,
        )

        parser.add_argument(
            "-c",
            "--coin",
            dest="coin",
            type=str,
            help="Coin to check hashrate (BTC or ETH)",
            default="BTC",
            choices=GLASSNODE_SUPPORTED_HASHRATE_ASSETS,
        )

        parser.add_argument(
            "-i",
            "--interval",
            dest="interval",
            type=str,
            help="Frequency interval. Default: 24h",
            default="24h",
            choices=INTERVALS,
        )

        parser.add_argument(
            "-s",
            "--since",
            dest="since",
            type=valid_date,
            help="Initial date. Default: 2020-01-01",
            default=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        )

        parser.add_argument(
            "-u",
            "--until",
            dest="until",
            type=valid_date,
            help="Final date. Default: 2021-01-01",
            default=(datetime.now()).strftime("%Y-%m-%d"),
        )

        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            display_hashrate(
                asset=ns_parser.coin,
                interval=ns_parser.interval,
                since=int(datetime.timestamp(ns_parser.since)),
                until=int(datetime.timestamp(ns_parser.until)),
                export=ns_parser.export,
            )

    @try_except
    def call_gwei(self, other_args: List[str]):
        """Process gwei command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="onchain",
            description="""
                Display ETH gas fees
                [Source: https://ethgasstation.info]
            """,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            ethgasstation_view.display_gwei_fees(export=ns_parser.export)

    @try_except
    def call_whales(self, other_args: List[str]):
        """Process whales command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="whales",
            description="""
                Display crypto whales transactions.
                [Source: https://docs.whale-alert.io/]
            """,
        )

        parser.add_argument(
            "-m",
            "--min",
            dest="min",
            type=check_int_range(500000, 100 ** 7),
            help="Minimum value of transactions.",
            default=1000000,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: date",
            default="date",
            choices=whale_alert_model.FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "-a",
            "--address",
            dest="address",
            action="store_true",
            help="Flag to show addresses of transaction",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            whale_alert_view.display_whales_transactions(
                min_value=ns_parser.min,
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                show_address=ns_parser.address,
                export=ns_parser.export,
            )

    @try_except
    def call_address(self, other_args: List[str]):
        """Process address command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="address",
            description="""
                Load address for further analysis. You can analyze account address, token address or transaction hash.
                [Source: Ethplorer]
            """,
        )

        parser.add_argument(
            "-a",
            action="store_true",
            help="Account address",
            dest="account",
            default=False,
        )

        parser.add_argument(
            "-t",
            action="store_true",
            help="ERC20 token address",
            dest="token",
            default=False,
        )

        parser.add_argument(
            "-tx",
            action="store_true",
            help="Transaction hash",
            dest="transaction",
            default=False,
        )

        parser.add_argument(
            "--address",
            dest="address",
            help="Ethereum address",
            default=False,
            type=str,
            required="-h" not in other_args,
        )

        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "--address")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if len(ns_parser.address) not in [42, 66]:
                print(
                    f"Couldn't load address {ns_parser.address}. "
                    f"Token or account address should be 42 characters long. "
                    f"Transaction hash should be 66 characters long\n"
                )

            if ns_parser.account:
                address_type = "account"
            elif ns_parser.token:
                address_type = "token"
            elif ns_parser.transaction:
                address_type = "tx"
            else:
                address_type = "account"

            if len(ns_parser.address) == 66:
                address_type = "tx"

            self.address = ns_parser.address
            self.address_type = address_type

    @try_except
    def call_balance(self, other_args: List[str]):
        """Process balance command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="balance",
            description="""
                Display info about tokens on given ethereum blockchain balance.
                [Source: Ethplorer]
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: index",
            default="index",
            choices=ethplorer_model.BALANCE_FILTERS,
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

        if ns_parser and self.address:
            ethplorer_view.display_address_info(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                address=self.address,
                export=ns_parser.export,
            )
        else:
            print("You need to set an ethereum address\n")

    @try_except
    def call_hist(self, other_args: List[str]):
        """Process hist command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="hist",
            description="""
                   Display history for given ethereum blockchain balance.
                    e.g. 0x3cD751E6b0078Be393132286c442345e5DC49699
                   [Source: Ethplorer]
               """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: timestamp",
            default="timestamp",
            choices=ethplorer_model.HIST_FILTERS,
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

        if ns_parser and self.address:
            ethplorer_view.display_address_history(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                address=self.address,
                export=ns_parser.export,
            )
        else:
            print("You need to set an ethereum address\n")

    @try_except
    def call_holders(self, other_args: List[str]):
        """Process holders command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="holders",
            description="""
                Display top ERC20 token holders: e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
                [Source: Ethplorer]
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: share",
            default="share",
            choices=ethplorer_model.HOLDERS_FILTERS,
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

        if ns_parser and self.address:
            ethplorer_view.display_top_token_holders(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                address=self.address,
                export=ns_parser.export,
            )
        else:
            print("You need to set an ethereum address\n")

    @try_except
    def call_top(self, other_args: List[str]):
        """Process top command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="top",
            description="""
                Display top ERC20 tokens.
                [Source: Ethplorer]
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: rank",
            default="rank",
            choices=ethplorer_model.TOP_FILTERS,
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
            ethplorer_view.display_top_tokens(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

    @try_except
    def call_info(self, other_args: List[str]):
        """Process info command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="info",
            description="""
                Display info about ERC20 token. e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
                [Source: Ethplorer]
            """,
        )

        parser.add_argument(
            "--social",
            action="store_false",
            help="Flag to show social media links",
            dest="social",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser and self.address:
            ethplorer_view.display_token_info(
                social=ns_parser.social,
                address=self.address,
                export=ns_parser.export,
            )
        else:
            print("You need to set an ethereum address\n")

    @try_except
    def call_th(self, other_args: List[str]):
        """Process th command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="th",
            description="""
                     Displays info about token history.
                     e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
                     [Source: Ethplorer]
                 """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: value",
            default="value",
            choices=ethplorer_model.TH_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "--hash",
            action="store_false",
            help="Flag to show transaction hash",
            dest="hash",
            default=True,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser and self.address:
            ethplorer_view.display_token_history(
                top=ns_parser.limit,
                hash_=ns_parser.hash,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                address=self.address,
                export=ns_parser.export,
            )
        else:
            print("You need to set an ethereum address\n")

    @try_except
    def call_tx(self, other_args: List[str]):
        """Process tx command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tx",
            description="""
                  Display info ERC20 token transaction on ethereum blockchain.
                  e.g. 0x9dc7b43ad4288c624fdd236b2ecb9f2b81c93e706b2ffd1d19b112c1df7849e6
                  [Source: Ethplorer]
              """,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser and self.address:
            ethplorer_view.display_tx_info(
                tx_hash=self.address,
                export=ns_parser.export,
            )
        else:
            print("You need to set an ethereum address\n")

    @try_except
    def call_prices(self, other_args: List[str]):
        """Process prices command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="prices",
            description="""
                  "Display token historical prices. e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
                  [Source: Ethplorer]
              """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: date",
            default="date",
            choices=ethplorer_model.PRICES_FILTERS,
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

        if ns_parser and self.address:
            ethplorer_view.display_token_historical_prices(
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                address=self.address,
                export=ns_parser.export,
            )
        else:
            print("You need to set an ethereum address\n")

    @try_except
    def call_lt(self, other_args: List[str]):
        """Process lt command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lt",
            description="""
                      Display Trades on Decentralized Exchanges aggregated by DEX or Month
                      [Source: https://graphql.bitquery.io/]
                  """,
        )

        parser.add_argument(
            "-k",
            "--kind",
            dest="kind",
            type=str,
            help="Aggregate trades by dex or time Default: dex",
            default="dex",
            choices=bitquery_model.LT_KIND,
        )

        parser.add_argument(
            "-vs",
            "--vs",
            dest="vs",
            type=str,
            help="Currency of displayed trade amount.",
            default="USD",
            choices=bitquery_model.CURRENCIES,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=10,
        )

        parser.add_argument(
            "-d",
            "--days",
            dest="days",
            type=check_positive,
            help="Number of days to display data for.",
            default=90,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: tradeAmount. For monthly trades date.",
            default="tradeAmount",
            choices=bitquery_model.LT_FILTERS,
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
            bitquery_view.display_dex_trades(
                kind=ns_parser.kind,
                trade_amount_currency=ns_parser.vs,
                top=ns_parser.limit,
                days=ns_parser.days,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

    @try_except
    def call_dvcp(self, other_args: List[str]):
        """Process dvcp command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dvcp",
            description="""
                      Display daily volume for given crypto pair
                      [Source: https://graphql.bitquery.io/]
                  """,
        )

        parser.add_argument(
            "-c",
            "--coin",
            dest="coin",
            type=str,
            help="ERC20 token symbol or address.",
            required="-h" not in other_args,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=10,
        )

        parser.add_argument(
            "-vs", "--vs", dest="vs", type=str, help="Quote currency", default="USDT"
        )

        parser.add_argument(
            "-d",
            "--days",
            dest="days",
            type=check_positive,
            help="Number of days to display data for.",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column.",
            default="date",
            choices=bitquery_model.DVCP_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            bitquery_view.display_daily_volume_for_given_pair(
                token=ns_parser.coin,
                vs=ns_parser.vs,
                top=ns_parser.days,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

    @try_except
    def call_tv(self, other_args: List[str]):
        """Process tv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tv",
            description="""
                      Display token volume on different Decentralized Exchanges.
                      [Source: https://graphql.bitquery.io/]
                  """,
        )

        parser.add_argument(
            "-c",
            "--coin",
            dest="coin",
            type=str,
            help="ERC20 token symbol or address.",
            required="-h" not in other_args,
        )

        parser.add_argument(
            "-vs",
            "--vs",
            dest="vs",
            type=str,
            help="Currency of displayed trade amount.",
            default="USD",
            choices=bitquery_model.CURRENCIES,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column.",
            default="trades",
            choices=bitquery_model.LT_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )
        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            bitquery_view.display_dex_volume_for_token(
                token=ns_parser.coin,
                trade_amount_currency=ns_parser.vs,
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

    @try_except
    def call_ueat(self, other_args: List[str]):
        """Process ueat command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ueat",
            description="""
                      Display number of unique ethereum addresses which made a transaction in given time interval,
                      [Source: https://graphql.bitquery.io/]
                  """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records. (Maximum available time period is 90 days."
            "Depending on chosen time period, display N records will be recalculated. E.g."
            "For interval: month, and number: 10, period of calculation equals to 300, "
            "but because of max days limit: 90, it will only return last 3 months (3 records). ",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column.",
            default="date",
            choices=bitquery_model.UEAT_FILTERS,
        )

        parser.add_argument(
            "-i",
            "--interval",
            dest="interval",
            type=str,
            help="Time interval in which ethereum address made transaction. month, week or day. "
            "Maximum time period is 90 days (3 months, 14 weeks)",
            default="day",
            choices=bitquery_model.INTERVALS,
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
            bitquery_view.display_ethereum_unique_senders(
                interval=ns_parser.interval,
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

    @try_except
    def call_ttcp(self, other_args: List[str]):
        """Process ttcp command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ttcp",
            description="""
                      Display most traded crypto pairs on given decentralized exchange in chosen time period.
                      [Source: https://graphql.bitquery.io/]
                  """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=10,
        )

        parser.add_argument(
            "-e",
            "--exchange",
            dest="exchange",
            type=str,
            help="Decentralized exchange name.",
            choices=bitquery_model.DECENTRALIZED_EXCHANGES,
        )

        parser.add_argument(
            "-d",
            "--days",
            dest="days",
            type=check_positive,
            help="Number of days to display data for.",
            default=30,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column.",
            default="tradeAmount",
            choices=bitquery_model.TTCP_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-e")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            exchange = "Uniswap"
            if ns_parser.exchange:
                if ns_parser.exchange in bitquery_model.DECENTRALIZED_EXCHANGES:
                    exchange = ns_parser.exchange
                else:
                    similar_cmd = difflib.get_close_matches(
                        ns_parser.exchange,
                        bitquery_model.DECENTRALIZED_EXCHANGES,
                        n=1,
                        cutoff=0.75,
                    )

                    if similar_cmd:
                        print(f"Replacing by '{similar_cmd[0]}'")
                        exchange = similar_cmd[0]

                    else:
                        similar_cmd = difflib.get_close_matches(
                            ns_parser.exchange,
                            bitquery_model.DECENTRALIZED_EXCHANGES,
                            n=1,
                            cutoff=0.5,
                        )
                        if similar_cmd:
                            print(f"Did you mean '{similar_cmd[0]}'?")

                        print(
                            f"Couldn't find any exchange with provided name: {ns_parser.exchange}. "
                            f"Please choose one from list: {bitquery_model.DECENTRALIZED_EXCHANGES}\n"
                        )

            else:
                print("Exchange not provided setting default to Uniswap.\n")

            bitquery_view.display_most_traded_pairs(
                days=ns_parser.days,
                top=ns_parser.limit,
                exchange=exchange,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

    @try_except
    def call_baas(self, other_args: List[str]):
        """Process baas command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="baas",
            description="""
                      Display average bid, ask prices, spread for given crypto pair for chosen time period
                      [Source: https://graphql.bitquery.io/]
                  """,
        )

        parser.add_argument(
            "-c",
            "--coin",
            dest="coin",
            type=str,
            help="ERC20 token symbol or address.",
        )

        parser.add_argument(
            "-vs", "--vs", dest="vs", type=str, help="Quote currency", default="USDT"
        )

        parser.add_argument(
            "-d",
            "--days",
            dest="days",
            type=check_positive,
            help="Number of days to display data for.",
            default=10,
        )

        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column.",
            default="date",
            choices=bitquery_model.BAAS_FILTERS,
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "-c")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if ns_parser.coin:
                if ns_parser.coin in bitquery_model.POSSIBLE_CRYPTOS:
                    bitquery_view.display_spread_for_crypto_pair(
                        token=ns_parser.coin,
                        vs=ns_parser.vs,
                        days=ns_parser.days,
                        sortby=ns_parser.sortby,
                        descend=ns_parser.descend,
                        export=ns_parser.export,
                    )

                else:
                    print(f"Coin '{ns_parser.coin}' does not exist.")
                    if ns_parser.coin.upper() == "BTC":
                        token = "WBTC"
                    else:
                        similar_cmd = difflib.get_close_matches(
                            ns_parser.coin,
                            bitquery_model.POSSIBLE_CRYPTOS,
                            n=1,
                            cutoff=0.75,
                        )
                        token = similar_cmd[0]
                    if similar_cmd[0]:
                        print(f"Replacing with '{token}'")
                        bitquery_view.display_spread_for_crypto_pair(
                            token=token,
                            vs=ns_parser.vs,
                            days=ns_parser.days,
                            sortby=ns_parser.sortby,
                            descend=ns_parser.descend,
                            export=ns_parser.export,
                        )
                    else:
                        similar_cmd = difflib.get_close_matches(
                            ns_parser.coin,
                            bitquery_model.POSSIBLE_CRYPTOS,
                            n=1,
                            cutoff=0.5,
                        )
                        if similar_cmd:
                            print(f"Did you mean '{similar_cmd[0]}'?")

            else:
                print("You didn't provide coin symbol.\n")

    def print_help(self):
        """Print help"""
        help_text = """
Onchain Menu:

Glassnode:
    hr              check blockchain hashrate over time (BTC or ETH)
Eth Gas Station:
    gwei             check current eth gas fees
Whale Alert:
    whales           check crypto wales transactions
BitQuery:
    lt               last trades by dex or month
    dvcp             daily volume for crypto pair
    tv               token volume on DEXes
    ueat             unique ethereum addresses which made a transaction
    ttcp             top traded crypto pairs on given decentralized exchange
    baas             bid, ask prices, average spread for given crypto pair
"""
        help_text += f"\nEthereum address: {self.address if self.address else '?'}"
        help_text += (
            f"\nAddress type: {self.address_type if self.address_type else '?'}\n"
        )

        help_text += """
Ethereum [Ethplorer]:
    address         load ethereum address of token, account or transaction
    top             top ERC20 tokens"""

        help_text += f"""{Style.DIM if self.address_type != "account" else ""}
    balance         check ethereum balance
    hist            ethereum balance history (transactions){Style.RESET_ALL if self.address_type != "account" else ""}"""

        help_text += f"""{Style.DIM if self.address_type != "token" else ""}
    info            ERC20 token info
    holders         top ERC20 token holders
    th              ERC20 token history
    prices          ERC20 token historical prices{Style.RESET_ALL if self.address_type != "token" else ""}"""

        help_text += f"""{Style.DIM if self.address_type != "tx" else ""}
    tx              ethereum blockchain transaction info{Style.RESET_ALL if self.address_type != "tx" else ""}
    """

        print(help_text)


def menu(queue: List[str] = None):
    """Onchain Menu"""
    onchain_controller = OnchainController(queue=queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if onchain_controller.queue and len(onchain_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if onchain_controller.queue[0] in ("q", "..", "quit"):
                if len(onchain_controller.queue) > 1:
                    return onchain_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = onchain_controller.queue[0]
            onchain_controller.queue = onchain_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if (
                an_input
                and an_input.split(" ")[0] in onchain_controller.CHOICES_COMMANDS
            ):
                print(f"{get_flair()} /crypto/onchain/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                onchain_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and onchain_controller.completer:
                try:
                    an_input = session.prompt(
                        f"{get_flair()} /crypto/onchain/ $ ",
                        completer=onchain_controller.completer,
                        search_ignore_case=True,
                    )
                except KeyboardInterrupt:
                    # Exit in case of keyboard interrupt
                    an_input = "exit"
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /crypto/onchain/ $ ")

        try:
            # Process the input command
            onchain_controller.queue = onchain_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /crypto/onchain menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                onchain_controller.CHOICES,
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
                        onchain_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                onchain_controller.queue.insert(0, an_input)
            else:
                print("\n")
