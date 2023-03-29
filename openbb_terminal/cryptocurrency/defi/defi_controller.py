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
    cryptosaurio_view,
    graph_model,
    graph_view,
    llama_model,
    llama_view,
    smartstake_view,
    substack_view,
    terramoney_fcd_model,
    terramoney_fcd_view,
)
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
    check_terra_address_format,
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
        "tokens",
        "pairs",
        "pools",
        "swaps",
        "stats",
        "vaults",
        "sinfo",
        "validators",
        "gacc",
        "sreturn",
        "lcsc",
        "anchor",
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
        mt.add_cmd("tokens")
        mt.add_cmd("stats")
        mt.add_cmd("pairs")
        mt.add_cmd("pools")
        mt.add_cmd("swaps")
        mt.add_cmd("ldapps")
        mt.add_cmd("gdapps")
        mt.add_cmd("stvl")
        mt.add_cmd("dtvl")
        mt.add_cmd("sinfo")
        mt.add_cmd("validators")
        mt.add_cmd("gacc")
        mt.add_cmd("sreturn")
        mt.add_cmd("lcsc")
        mt.add_cmd("anchor")
        console.print(text=mt.menu_text, menu="Cryptocurrency - Decentralized Finance")

    @log_start_end(log=logger)
    def call_anchor(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="anchor",
            description="""
                Displays anchor protocol earnings data of a certain terra address
                --transactions flag can be passed to show history of previous transactions
                [Source: https://cryptosaurio.com/]
            """,
        )
        parser.add_argument(
            "--address",
            dest="address",
            type=check_terra_address_format,
            help="Terra address. Valid terra addresses start with 'terra'",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "--transactions",
            action="store_true",
            help="Flag to show transactions history in anchor earn",
            dest="transactions",
            default=False,
        )

        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "--address")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            cryptosaurio_view.display_anchor_data(
                show_transactions=ns_parser.transactions,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                address=ns_parser.address,
            )

    @log_start_end(log=logger)
    def call_sinfo(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sinfo",
            description="""
                Displays staking info of a certain terra address.
                [Source: https://fcd.terra.dev/swagger]
            """,
        )
        parser.add_argument(
            "-a",
            "--address",
            dest="address",
            type=check_terra_address_format,
            help="Terra address. Valid terra addresses start with 'terra'",
            required="-h" not in other_args,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of delegations",
            default=10,
        )

        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "-a")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            terramoney_fcd_view.display_account_staking_info(
                address=ns_parser.address,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_validators(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="validators",
            description="""
                Displays information about terra validators.
                [Source: https://fcd.terra.dev/swagger]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of validators to show",
            default=10,
        )
        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: votingPower",
            default="votingPower",
            choices=terramoney_fcd_model.VALIDATORS_COLUMNS,
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
            terramoney_fcd_view.display_validators(
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_gacc(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="gacc",
            description="""
                Displays terra blockchain account growth history.
                [Source: https://fcd.terra.dev/swagger]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of days to show",
            default=90,
        )
        parser.add_argument(
            "--cumulative",
            action="store_false",
            help="Show cumulative or discrete values. For active accounts only discrete value are available",
            dest="cumulative",
            default=True,
        )
        parser.add_argument(
            "-k",
            "--kind",
            dest="kind",
            type=str,
            help="Total account count or active account count. Default: total",
            default="total",
            choices=["active", "total"],
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            terramoney_fcd_view.display_account_growth(
                kind=ns_parser.kind,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                cumulative=ns_parser.cumulative,
                limit=ns_parser.limit,
            )

    @log_start_end(log=logger)
    def call_sratio(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sratio",
            description="""
                Displays terra blockchain staking ratio history.
                [Source: https://fcd.terra.dev/swagger]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of days to show",
            default=90,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            terramoney_fcd_view.display_staking_ratio_history(
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                limit=ns_parser.limit,
            )

    @log_start_end(log=logger)
    def call_sreturn(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sreturn",
            description="""
                Displays terra blockchain staking returns history.
                [Source: https://fcd.terra.dev/swagger]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of days to show",
            default=90,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            terramoney_fcd_view.display_staking_returns_history(
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                limit=ns_parser.limit,
            )

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
            type=str,
            required="-h" not in other_args,
            help="dApps to search historical TVL. Should be split by , e.g.: anchor,sushiswap,pancakeswap",
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "-d")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            llama_view.display_historical_tvl(dapps=ns_parser.dapps)

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
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
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
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
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
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            choices=range(1, 1000),
            metavar="SKIP",
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
            graph_view.display_uni_tokens(
                skip=ns_parser.skip,
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            graph_view.display_uni_stats(
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            choices=range(1, 1000),
            metavar="VOL",
        )
        parser.add_argument(
            "-tx",
            "--tx",
            dest="tx",
            type=check_positive,
            help="Minimum number of transactions",
            default=100,
            choices=range(1, 1000),
            metavar="TX",
        )
        parser.add_argument(
            "--days",
            dest="days",
            type=check_positive,
            help="Number of days the pair has been active,",
            default=10,
            choices=range(1, 1000),
            metavar="DAY",
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
            graph_view.display_recently_added(
                limit=ns_parser.limit,
                days=ns_parser.days,
                min_volume=ns_parser.vol,
                min_tx=ns_parser.tx,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            graph_view.display_uni_pools(
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
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
            default="Datetime",
            choices=graph_model.SWAPS_FILTERS,
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
            graph_view.display_last_uni_swaps(
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_vaults(self, other_args: List[str]):
        """Process swaps command"""
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
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    def call_lcsc(self, other_args: List[str]):
        """Process lcsc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lcsc",
            description="""
                Display Luna circulating supply changes stats.
                [Source: Smartstake.io]

                Follow these steps to get the key token:
                1. Head to https://terra.smartstake.io/
                2. Right click on your browser and choose Inspect
                3. Select Network tab (by clicking on the expand button next to Source tab)
                4. Go to Fetch/XHR tab, and refresh the page
                5. Get the option looks similar to the following: `listData?type=history&dayCount=30`
                6. Extract the key and token out of the URL

            """,
        )

        parser.add_argument(
            "-d",
            "--days",
            dest="days",
            type=check_positive,
            help="Number of days to display. Default: 30 days",
            default=30,
            choices=range(1, 1000),
            metavar="DAYS",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, limit=5
        )

        if ns_parser:
            smartstake_view.display_luna_circ_supply_change(
                days=ns_parser.days,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
