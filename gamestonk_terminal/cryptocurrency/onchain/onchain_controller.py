"""Onchain Controller Module"""
__docformat__ = "numpy"

# pylint: disable=C0302

import argparse
import difflib
from typing import List

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import (
    get_flair,
    parse_known_args_and_warn,
    check_positive,
    check_int_range,
    try_except,
    system_clear,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
)

from gamestonk_terminal.cryptocurrency.onchain import (
    ethgasstation_view,
    whale_alert_view,
    ethplorer_view,
    bitquery_view,
    bitquery_model,
)


class OnchainController:
    """Onchain Controller class"""

    CHOICES = [
        "cls",
        "?",
        "help",
        "q",
        "quit",
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
        "active",
        "lt",
        "dvcp",
        "tv",
        "ueat",
        "ttcp",
        "baas",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(self):
        """Constructor"""
        self.onchain_parser = argparse.ArgumentParser(add_help=False, prog="onchain")
        self.onchain_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )
        self.address = None
        self.address_type = None

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

        (known_args, other_args) = self.onchain_parser.parse_known_args(
            an_input.split()
        )

        # Help menu again
        if known_args.cmd == "?":
            self.print_help()
            return None

        # Clear screen
        if known_args.cmd == "cls":
            system_clear()
            return None

        return getattr(
            self, "call_" + known_args.cmd, lambda: "Command not recognized!"
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

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        ethgasstation_view.display_gwei_fees(export=ns_parser.export)

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
            help="Sort by given column. Default: date",
            default="date",
            choices=[
                "date",
                "symbol",
                "blockchain",
                "amount",
                "amount_usd",
                "from",
                "to",
            ],
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
            "--balance",
            dest="balance",
            action="store_true",
            help="Flag to show addresses of transaction",
            default=False,
        )

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser:
                return

            whale_alert_view.display_whales_transactions(
                min_value=ns_parser.min,
                top=ns_parser.top,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                show_address=ns_parser.address,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e)

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

        try:
            if other_args:
                if not other_args[0][0] == "-":
                    other_args.insert(0, "--address")

            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser:
                return

            if len(ns_parser.address) not in [42, 66]:
                print(
                    f"Couldn't load address {ns_parser.address}. "
                    f"Token or account address should be 42 characters long. "
                    f"Transaction hash should be 66 characters long\n"
                )
                return

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

            print(f"Address loaded {self.address}\n")
        except Exception as e:
            print(e)

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
            help="Sort by given column. Default: index",
            default="index",
            choices=[
                "index",
                "balance",
                "tokenName",
                "tokenSymbol",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser or not self.address:
                return

            ethplorer_view.display_address_info(
                top=ns_parser.top,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                address=self.address,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e)

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
            help="Sort by given column. Default: timestamp",
            default="timestamp",
            choices=["timestamp", "transactionHash", "token", "value"],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser or not self.address:
                return

            ethplorer_view.display_address_history(
                top=ns_parser.top,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                address=self.address,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e)

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
            help="Sort by given column. Default: share",
            default="share",
            choices=[
                "balance",
                "balance",
                "share",
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
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser or not self.address:
                return

            ethplorer_view.display_top_token_holders(
                top=ns_parser.top,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                address=self.address,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e)

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
            help="Sort by given column. Default: rank",
            default="rank",
            choices=[
                "rank",
                "name",
                "symbol",
                "price",
                "txsCount",
                "transfersCount",
                "holdersCount",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=True,
        )

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser:
                return

            ethplorer_view.display_top_tokens(
                top=ns_parser.top,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e)

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

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser or not self.address:
                return

            ethplorer_view.display_token_info(
                social=ns_parser.social,
                address=self.address,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e)

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
            help="Sort by given column. Default: value",
            default="value",
            choices=[
                "value",
            ],
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

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:

            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser or not self.address:
                return

            ethplorer_view.display_token_history(
                top=ns_parser.top,
                hash_=ns_parser.hash,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                address=self.address,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e)

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

        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:

            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser or not self.address:
                return

            ethplorer_view.display_tx_info(
                tx_hash=self.address,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e)

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
            help="Sort by given column. Default: date",
            default="date",
            choices=[
                "date",
                "cap",
                "volumeConverted",
                "open",
                "high",
                "close",
                "low",
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
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )

        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)

            if not ns_parser or not self.address:
                return

            ethplorer_view.display_token_historical_prices(
                top=ns_parser.top,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                address=self.address,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e)

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
            choices=["dex", "time"],
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
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
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
            choices=["trades", "tradeAmount", "exchange"],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        try:
            ns_parser = parse_known_args_and_warn(
                parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
            )

            if not ns_parser:
                return

            bitquery_view.display_dex_trades(
                kind=ns_parser.kind,
                trade_amount_currency=ns_parser.vs,
                top=ns_parser.top,
                days=ns_parser.days,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e)

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
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
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
            choices=[
                "date",
                "exchange",
                "base",
                "quote",
                "open",
                "high",
                "low",
                "close",
                "tradeAmount",
                "trades",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        try:
            if other_args:
                if not other_args[0][0] == "-":
                    other_args.insert(0, "-c")

            ns_parser = parse_known_args_and_warn(
                parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
            )

            if not ns_parser:
                return

            bitquery_view.display_daily_volume_for_given_pair(
                token=ns_parser.coin,
                vs=ns_parser.vs,
                top=ns_parser.days,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e)

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
            help="Sort by given column.",
            default="trades",
            choices=["exchange", "tradeAmount", "trades"],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        try:
            if other_args:
                if not other_args[0][0] == "-":
                    other_args.insert(0, "-c")

            ns_parser = parse_known_args_and_warn(
                parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
            )

            if not ns_parser:
                return

            bitquery_view.display_dex_volume_for_token(
                token=ns_parser.coin,
                trade_amount_currency=ns_parser.vs,
                top=ns_parser.top,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e)

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
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records. (Maximum available time period is 90 days."
            "Depending on chosen time period, top N records will be recalculated. E.g."
            "For interval: month, and top: 10, period of calculation equals to 300, "
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
            choices=[
                "date",
                "uniqueSenders",
                "transactions",
                "averageGasPrice",
                "mediumGasPrice",
                "maximumGasPrice",
            ],
        )

        parser.add_argument(
            "-i",
            "--interval",
            dest="interval",
            type=str,
            help="Time interval in which ethereum address made transaction. month, week or day. "
            "Maximum time period is 90 days (3 months, 14 weeks)",
            default="day",
            choices=["day", "month", "week"],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        try:
            ns_parser = parse_known_args_and_warn(
                parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
            )

            if not ns_parser:
                return

            bitquery_view.display_ethereum_unique_senders(
                interval=ns_parser.interval,
                limit=ns_parser.top,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e)

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
            "-t",
            "--top",
            dest="top",
            type=check_positive,
            help="top N number records",
            default=10,
        )

        parser.add_argument(
            "-e",
            "--exchange",
            dest="exchange",
            type=str,
            help="Decentralized exchange name.",
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
            choices=["base", "quoted", "trades", "tradeAmount"],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-e")

        try:
            ns_parser = parse_known_args_and_warn(
                parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
            )

            if not ns_parser:
                return

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
                            return
                        print(
                            f"Couldn't find any exchange with provided name: {ns_parser.exchange}. "
                            f"Please choose one from list: {bitquery_model.DECENTRALIZED_EXCHANGES}\n"
                        )
                        return
            else:
                print("Exchange not provided setting default to Uniswap.\n")

            bitquery_view.display_most_traded_pairs(
                days=ns_parser.days,
                top=ns_parser.top,
                exchange=exchange,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e)

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
            choices=[
                "date",
                "baseCurrency",
                "quoteCurrency",
                "dailySpread",
                "averageBidPrice",
                "averageAskPrice",
            ],
        )

        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        try:
            if other_args:
                if not other_args[0][0] == "-":
                    other_args.insert(0, "-c")

            ns_parser = parse_known_args_and_warn(
                parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
            )

            if not ns_parser:
                return

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
                        print(f"Replacing by '{token}'")
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
                return
        except Exception as e:
            print(e)

    def print_help(self):
        """Print help"""
        help_text = """
Onchain:
    cls         clear screen
    ?/help      show this menu again
    q           quit this menu, and shows back to main menu
    quit        quit to abandon the program

Eth Gas Station:
    gwei              check current eth gas fees

Whale Alert:
    whales            check crypto wales transactions

BitQuery:
    lt                last trades by dex or month
    dvcp              daily volume for crypto pair
    tv                token volume on DEXes
    ueat              unique ethereum addresses which made a transaction
    ttcp              top traded crypto pairs on given decentralized exchange
    baas              bid, ask prices, average spread for given crypto pair
"""
        help_text += f"\nEthereum address: {self.address if self.address else '?'}"
        help_text += (
            f"\nAddress type: {self.address_type if self.address_type else '?'}\n"
        )

        help_text += """
Ethereum [Ethplorer]:
    address           load ethereum address of token, account or transaction
    top               top ERC20 tokens"""

        if self.address_type == "account":
            help_text += """
    balance           check ethereum balance balance
    hist              ethereum balance history (transactions)"""

        if self.address_type == "token":
            help_text += """
    info              ERC20 token info
    holders           top ERC20 token holders
    th                ERC20 token history
    prices            ERC20 token historical prices"""

        if self.address_type == "tx":
            help_text += """
    tx                ethereum blockchain transaction info"""

        print(help_text, "\n")


def menu():
    """Onchain Menu"""
    onchain_controller = OnchainController()
    onchain_controller.call_help(None)

    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in onchain_controller.CHOICES}
            choices["ttcp"] = {c: None for c in bitquery_model.DECENTRALIZED_EXCHANGES}

            choices["baas"]["-c"] = {c: None for c in bitquery_model.POSSIBLE_CRYPTOS}
            choices["baas"]["--coin"] = {
                c: None for c in bitquery_model.POSSIBLE_CRYPTOS
            }

            completer = NestedCompleter.from_nested_dict(choices)
            an_input = session.prompt(
                f"{get_flair()} (crypto)>(onchain)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (crypto)>(onchain)> ")

        try:
            process_input = onchain_controller.switch(an_input)
        except SystemExit:
            print("The command selected doesn't exist\n")
            continue

        if process_input is False:
            return False

        if process_input is True:
            return True
