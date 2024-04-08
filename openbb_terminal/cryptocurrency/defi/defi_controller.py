"""Defi Controller Module"""

__docformat__ = "numpy"

# pylint: disable=C0302

import argparse
import logging
from typing import List, Optional

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.cryptocurrency.defi import (
    coindix_model,
    coindix_view,
    llama_model,
    llama_view,
    substack_view,
)
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class DefiController(BaseController):
    """Defi Controller class"""

    CHOICES_COMMANDS = [
        "ldapps",
        "gdapps",
        "stvl",
        "dtvl",
        "newsletter",
        "vaults",
    ]

    PATH = "/crypto/defi/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("crypto/defi/")
        mt.add_cmd("newsletter")
        mt.add_cmd("vaults")
        mt.add_cmd("ldapps")
        mt.add_cmd("gdapps")
        mt.add_cmd("stvl")
        mt.add_cmd("dtvl")
        console.print(text=mt.menu_text, menu="Cryptocurrency - Decentralized Finance")

    @log_start_end(log=logger)
    def call_gdapps(self, other_args: List[str]):
        """Process gdapps command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="gdapps",
            description="""
                Display top dApps (in terms of TVL) grouped by chain.
                [Source: https://docs.llama.fi/api]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of top dApps to display",
            default=40,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            llama_view.display_grouped_defi_protocols(limit=ns_parser.limit)

    @log_start_end(log=logger)
    def call_dtvl(self, other_args: List[str]):
        """Process dtvl command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dtvl",
            description="""
                Displays historical TVL of different dApps.
                [Source: https://docs.llama.fi/api]
            """,
        )
        parser.add_argument(
            "-d",
            "--dapps",
            dest="dapps",
            choices=["anchor", "sushiswap", "pancakeswap"],
            required="-h" not in other_args,
            help="dApps to search historical TVL. Should be split by , e.g.: anchor,sushiswap,pancakeswap",
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "-d")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            llama_view.display_historical_tvl(
                dapps=ns_parser.dapps,
                export=ns_parser.export,
                sheet_name=(
                    " ".join(ns_parser.sheet_name) if ns_parser.sheet_name else None
                ),
            )

    @log_start_end(log=logger)
    def call_ldapps(self, other_args: List[str]):
        """Process ldapps command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ldapps",
            description="""
                Display information about listed dApps on DeFi Llama.
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
            "--desc",
            action="store_true",
            help="Flag to display description of protocol",
            dest="description",
            default=False,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            llama_view.display_defi_protocols(
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                description=ns_parser.description,
                export=ns_parser.export,
                sheet_name=(
                    " ".join(ns_parser.sheet_name) if ns_parser.sheet_name else None
                ),
            )

    @log_start_end(log=logger)
    def call_stvl(self, other_args: List[str]):
        """Process stvl command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="stvl",
            description="""
                Displays historical values of the total sum of TVLs from all listed dApps.
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

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            llama_view.display_defi_tvl(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=(
                    " ".join(ns_parser.sheet_name) if ns_parser.sheet_name else None
                ),
            )

    @log_start_end(log=logger)
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

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            substack_view.display_newsletters(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=(
                    " ".join(ns_parser.sheet_name) if ns_parser.sheet_name else None
                ),
            )

    @log_start_end(log=logger)
    def call_vaults(self, other_args: List[str]):
        """Process vaults command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="vaults",
            description="""
                Display Top DeFi Vaults.
                [Source: https://coindix.com/]
            """,
        )
        parser.add_argument(
            "-c",
            "--chain",
            dest="chain",
            type=str,
            help="Blockchain name e.g. ethereum, terra",
            default=None,
            choices=coindix_model.CHAINS,
            required=False,
        )
        parser.add_argument(
            "-p",
            "--protocol",
            dest="protocol",
            type=str,
            help="DeFi protocol name e.g. aave, uniswap",
            default=None,
            choices=coindix_model.PROTOCOLS,
            required=False,
        )
        parser.add_argument(
            "-k",
            "--kind",
            dest="kind",
            type=str,
            help="Kind/type of vault e.g. lp, single, noimploss, stable",
            default=None,
            choices=coindix_model.VAULT_KINDS,
            required=False,
        )
        parser.add_argument(
            "-t",
            "--top",
            dest="limit",
            type=check_positive,
            help="Number of records to display",
            default=10,
            choices=range(1, 1000),
            metavar="TOP",
        )
        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: timestamp",
            default="apy",
            choices=coindix_model.VAULTS_FILTERS,
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
            "-l",
            "--links",
            action="store_false",
            help="Flag to show vault link",
            dest="link",
            default=True,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            coindix_view.display_defi_vaults(
                chain=ns_parser.chain,
                kind=ns_parser.kind,
                protocol=ns_parser.protocol,
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                link=ns_parser.link,
                export=ns_parser.export,
                sheet_name=(
                    " ".join(ns_parser.sheet_name) if ns_parser.sheet_name else None
                ),
            )
