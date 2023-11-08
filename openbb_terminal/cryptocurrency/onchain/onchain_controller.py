"""Onchain Controller Module"""
__docformat__ = "numpy"

# pylint: disable=C0302

import argparse
import difflib
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.cryptocurrency.due_diligence.glassnode_model import (
    GLASSNODE_SUPPORTED_HASHRATE_ASSETS,
    INTERVALS_HASHRATE,
)
from openbb_terminal.cryptocurrency.due_diligence.glassnode_view import display_hashrate
from openbb_terminal.cryptocurrency.onchain import (
    bitquery_model,
    bitquery_view,
    blockchain_view,
    ethgasstation_view,
    ethplorer_model,
    ethplorer_view,
    topledger_model,
    topledger_view,
    whale_alert_model,
    whale_alert_view,
)
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_int_range,
    check_positive,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class OnchainController(BaseController):
    """Onchain Controller class"""

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
        "btccp",
        "btcct",
        "btcblockdata",
        "topledger",
    ]

    PATH = "/crypto/onchain/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        self.address = ""
        self.address_type = ""

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            choices["hr"].update({c: {} for c in GLASSNODE_SUPPORTED_HASHRATE_ASSETS})

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("crypto/onchain/")
        mt.add_cmd("hr")
        mt.add_cmd("btccp")
        mt.add_cmd("btcct")
        mt.add_cmd("btcblockdata")
        mt.add_cmd("gwei")
        mt.add_cmd("whales")
        mt.add_cmd("topledger")
        mt.add_cmd("lt")
        mt.add_cmd("dvcp")
        mt.add_cmd("tv")
        mt.add_cmd("ueat")
        mt.add_cmd("ttcp")
        mt.add_cmd("baas")
        mt.add_raw("\n")
        mt.add_param("_address", self.address or "")
        mt.add_param("_type", self.address_type or "")
        mt.add_raw("\n")
        mt.add_info("_ethereum_")
        mt.add_cmd("address")
        mt.add_cmd("top")
        mt.add_cmd("balance", self.address_type == "account")
        mt.add_cmd("hist", self.address_type == "account")
        mt.add_cmd("info", self.address_type == "token")
        mt.add_cmd("holders", self.address_type == "token")
        mt.add_cmd("th", self.address_type == "token")
        mt.add_cmd("prices", self.address_type == "token")
        mt.add_cmd("tx", self.address_type == "tx")
        console.print(text=mt.menu_text, menu="Cryptocurrency - Onchain")

    @log_start_end(log=logger)
    def call_btcct(self, other_args: List[str]):
        """Process btcct command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="btcct",
            description="""
                Display BTC confirmed transactions [Source: https://api.blockchain.info/]
            """,
        )

        parser.add_argument(
            "-s",
            "--since",
            dest="since",
            type=valid_date,
            help="Initial date. Default: 2010-01-01",
            default=datetime(2010, 1, 1).strftime("%Y-%m-%d"),
        )

        parser.add_argument(
            "-u",
            "--until",
            dest="until",
            type=valid_date,
            help=f"Final date. Default: {(datetime.now()).strftime('%Y-%m-%d')}",
            default=(datetime.now()).strftime("%Y-%m-%d"),
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            blockchain_view.display_btc_confirmed_transactions(
                start_date=ns_parser.since.strftime("%Y-%m-%d"),
                end_date=ns_parser.until.strftime("%Y-%m-%d"),
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_btccp(self, other_args: List[str]):
        """Process btccp command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="btccp",
            description="""
                Display BTC circulating supply [Source: https://api.blockchain.info/]
            """,
        )

        parser.add_argument(
            "-s",
            "--since",
            dest="since",
            type=valid_date,
            help="Initial date. Default: 2010-01-01",
            default=datetime(2010, 1, 1).strftime("%Y-%m-%d"),
        )

        parser.add_argument(
            "-u",
            "--until",
            dest="until",
            type=valid_date,
            help="Final date. Default: 2021-01-01",
            default=(datetime.now()).strftime("%Y-%m-%d"),
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            blockchain_view.display_btc_circulating_supply(
                start_date=ns_parser.since.strftime("%Y-%m-%d"),
                end_date=ns_parser.until.strftime("%Y-%m-%d"),
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            choices=INTERVALS_HASHRATE,
        )

        parser.add_argument(
            "-s",
            "--since",
            dest="since",
            type=valid_date,
            help=f"Initial date. Default: {(datetime.now() - timedelta(days=365)).strftime('%Y-%m-%d')}",
            default=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        )

        parser.add_argument(
            "-u",
            "--until",
            dest="until",
            type=valid_date,
            help=f"Final date. Default: {(datetime.now()).strftime('%Y-%m-%d')}",
            default=(datetime.now()).strftime("%Y-%m-%d"),
        )

        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "-c")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            display_hashrate(
                symbol=ns_parser.coin,
                interval=ns_parser.interval,
                start_date=ns_parser.since.strftime("%Y-%m-%d"),
                end_date=ns_parser.until.strftime("%Y-%m-%d"),
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            ethgasstation_view.display_gwei_fees(
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            type=check_int_range(500000, 100**7),
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
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        parser.add_argument(
            "-a",
            "--address",
            dest="address",
            action="store_true",
            help="Flag to show addresses of transaction",
            default=False,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            whale_alert_view.display_whales_transactions(
                min_value=ns_parser.min,
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                show_address=ns_parser.address,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_topledger(self, other_args: List[str]):
        """Process topledger command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="topledger",
            description="""
                    Display on-chain data from topledger.
                    [Source: Topledger]
                """,
        )

        parser.add_argument(
            "-o",
            "--org",
            dest="org_slug",
            type=str,
            help="Organization Slug",
            choices=list(topledger_model.MAPPING.keys()),
            default=None,
        )
        parser.add_argument(
            "-q",
            "--query",
            dest="query_slug",
            type=str,
            help="Query Slug",
            choices=[
                query.get("slug")
                for section in topledger_model.MAPPING.values()
                for query in section.get("queries", [])
                if query.get("slug")
            ],
            default=None,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            topledger_view.display_topledger_data(
                org_slug=ns_parser.org_slug,
                query_slug=ns_parser.query_slug,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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

        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "--address")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if len(ns_parser.address) not in [42, 66]:
                console.print(
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

    @log_start_end(log=logger)
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
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.address:
                ethplorer_view.display_address_info(
                    limit=ns_parser.limit,
                    sortby=ns_parser.sortby,
                    ascend=ns_parser.reverse,
                    address=self.address,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("You need to set an ethereum address\n")

    @log_start_end(log=logger)
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
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.address:
                ethplorer_view.display_address_history(
                    limit=ns_parser.limit,
                    sortby=ns_parser.sortby,
                    ascend=ns_parser.reverse,
                    address=self.address,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("You need to set an ethereum address\n")

    @log_start_end(log=logger)
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
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.address:
                ethplorer_view.display_top_token_holders(
                    limit=ns_parser.limit,
                    sortby=ns_parser.sortby,
                    ascend=ns_parser.reverse,
                    address=self.address,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("You need to set an ethereum address\n")

    @log_start_end(log=logger)
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
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            ethplorer_view.display_top_tokens(
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if self.address:
                ethplorer_view.display_token_info(
                    social=ns_parser.social,
                    address=self.address,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("You need to set an ethereum address\n")

    @log_start_end(log=logger)
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
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        parser.add_argument(
            "--hash",
            action="store_false",
            help="Flag to show transaction hash",
            dest="hash",
            default=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if self.address:
                ethplorer_view.display_token_history(
                    limit=ns_parser.limit,
                    hash_=ns_parser.hash,
                    sortby=ns_parser.sortby,
                    ascend=ns_parser.reverse,
                    address=self.address,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("You need to set an ethereum address\n")

    @log_start_end(log=logger)
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

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if self.address:
                ethplorer_view.display_tx_info(
                    tx_hash=self.address,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("You need to set an ethereum address\n")

    @log_start_end(log=logger)
    def call_prices(self, other_args: List[str]):
        """Process prices command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="prices",
            description="""
                Display token historical prices. e.g. 0x1f9840a85d5aF5bf1D1762F925BDADdC4201F984
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
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if self.address:
                ethplorer_view.display_token_historical_prices(
                    limit=ns_parser.limit,
                    sortby=ns_parser.sortby,
                    ascend=ns_parser.reverse,
                    address=self.address,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )
            else:
                console.print("You need to set an ethereum address\n")

    @log_start_end(log=logger)
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
            choices=range(1, 360),
            metavar="DAYS",
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
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            bitquery_view.display_dex_trades(
                kind=ns_parser.kind,
                trade_amount_currency=ns_parser.vs,
                limit=ns_parser.limit,
                days=ns_parser.days,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            "-vs",
            "--vs",
            dest="vs",
            type=str,
            help="Quote currency",
            default="USDT",
            choices=bitquery_model.CURRENCIES,
        )
        parser.add_argument(
            "-d",
            "--days",
            dest="days",
            type=check_positive,
            help="Number of days to display data for.",
            default=10,
            choices=range(1, 100),
            metavar="DAYS",
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
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "-c")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            bitquery_view.display_daily_volume_for_given_pair(
                symbol=ns_parser.coin,
                to_symbol=ns_parser.vs,
                limit=ns_parser.days,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "-c")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            bitquery_view.display_dex_volume_for_token(
                symbol=ns_parser.coin,
                trade_amount_currency=ns_parser.vs,
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            choices=range(1, 90),
            metavar="LIMIT",
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
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_RAW_DATA_ALLOWED,
        )

        if ns_parser:
            bitquery_view.display_ethereum_unique_senders(
                interval=ns_parser.interval,
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            choices=range(1, 100),
            metavar="DAYS",
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
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-e")

        ns_parser = self.parse_known_args_and_warn(
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
                        console.print(f"Replacing by '{similar_cmd[0]}'")
                        exchange = similar_cmd[0]

                    else:
                        similar_cmd = difflib.get_close_matches(
                            ns_parser.exchange,
                            bitquery_model.DECENTRALIZED_EXCHANGES,
                            n=1,
                            cutoff=0.5,
                        )
                        if similar_cmd:
                            console.print(f"Did you mean '{similar_cmd[0]}'?")

                        console.print(
                            f"Couldn't find any exchange with provided name: {ns_parser.exchange}. "
                            f"Please choose one from list: {bitquery_model.DECENTRALIZED_EXCHANGES}\n"
                        )

            else:
                console.print("Exchange not provided setting default to Uniswap.\n")

            bitquery_view.display_most_traded_pairs(
                days=ns_parser.days,
                limit=ns_parser.limit,
                exchange=exchange,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            choices=bitquery_model.get_possible_crypto_symbols(),
            metavar="COIN",
        )
        parser.add_argument(
            "-vs",
            "--vs",
            dest="vs",
            type=str,
            help="Quote currency",
            default="USDT",
            choices=bitquery_model.CURRENCIES,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
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
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in descending order by default. "
                "Reverse flag will sort it in an ascending way. "
                "Only works when raw data is displayed."
            ),
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "-c")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.coin:
                possible_cryptos = bitquery_model.get_possible_crypto_symbols()
                if ns_parser.coin in possible_cryptos:
                    bitquery_view.display_spread_for_crypto_pair(
                        symbol=ns_parser.coin,
                        to_symbol=ns_parser.vs,
                        limit=ns_parser.limit,
                        sortby=ns_parser.sortby,
                        ascend=ns_parser.reverse,
                        export=ns_parser.export,
                        sheet_name=" ".join(ns_parser.sheet_name)
                        if ns_parser.sheet_name
                        else None,
                    )

                else:
                    console.print(f"Coin '{ns_parser.coin}' does not exist.")
                    if ns_parser.coin.upper() == "BTC":
                        token = "WBTC"  # noqa: S105
                    else:
                        similar_cmd = difflib.get_close_matches(
                            ns_parser.coin,
                            possible_cryptos,
                            n=1,
                            cutoff=0.75,
                        )
                        try:
                            token = similar_cmd[0]
                            if similar_cmd[0]:
                                console.print(f"Replacing with '{token}'")
                                bitquery_view.display_spread_for_crypto_pair(
                                    token=token,
                                    to_symbol=ns_parser.vs,
                                    limit=ns_parser.limit,
                                    sortby=ns_parser.sortby,
                                    ascend=ns_parser.reverse,
                                    export=ns_parser.export,
                                    sheet_name=" ".join(ns_parser.sheet_name)
                                    if ns_parser.sheet_name
                                    else None,
                                )
                        except Exception:
                            similar_cmd = difflib.get_close_matches(
                                ns_parser.coin,
                                possible_cryptos,
                                n=1,
                                cutoff=0.5,
                            )
                            if similar_cmd:
                                console.print(f"Did you mean '{similar_cmd[0]}'?")

            else:
                console.print("You didn't provide coin symbol.\n")

    @log_start_end(log=logger)
    def call_btcblockdata(self, other_args: List[str]):
        """Process btcblockdata command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="btcblockdata",
            description="""
                Display block data from Blockchain.com,
                [Source: https://api.blockchain.info/]
            """,
        )

        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "--blockhash")

        parser.add_argument(
            "--blockhash",
            action="store",
            help="Flag for block hash of block.",
            dest="blockhash",
            default=False,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            blockchain_view.display_btc_single_block(
                blockhash=ns_parser.blockhash,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
