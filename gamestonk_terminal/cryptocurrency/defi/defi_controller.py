"""Defi Controller Module"""
__docformat__ = "numpy"

# pylint: disable=C0302

import argparse
import logging
from typing import List

from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.cryptocurrency.defi import (
    coindix_model,
    coindix_view,
    defipulse_view,
    defirate_view,
    graph_model,
    graph_view,
    llama_model,
    llama_view,
    substack_view,
    terraengineer_model,
    terraengineer_view,
    terramoney_fcd_model,
    terramoney_fcd_view,
    smartstake_view,
)
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
    check_terra_address_format,
    parse_known_args_and_warn,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.rich_config import console

logger = logging.getLogger(__name__)


class DefiController(BaseController):
    """Defi Controller class"""

    CHOICES_COMMANDS = [
        "dpi",
        "funding",
        "lending",
        "borrow",
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
        "ayr",
        "aterra",
        "sinfo",
        "validators",
        "govp",
        "gacc",
        "sratio",
        "sreturn",
        "lcsc",
    ]

    PATH = "/crypto/defi/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["ldapps"]["-s"] = {c: {} for c in llama_model.LLAMA_FILTERS}
            choices["aterra"]["--asset"] = {c: {} for c in terraengineer_model.ASSETS}
            choices["aterra"] = {c: {} for c in terraengineer_model.ASSETS}
            choices["tokens"]["-s"] = {c: {} for c in graph_model.TOKENS_FILTERS}
            choices["pairs"]["-s"] = {c: {} for c in graph_model.PAIRS_FILTERS}
            choices["pools"]["-s"] = {c: {} for c in graph_model.POOLS_FILTERS}
            choices["swaps"]["-s"] = {c: {} for c in graph_model.SWAPS_FILTERS}
            choices["vaults"]["-s"] = {c: {} for c in coindix_model.VAULTS_FILTERS}
            choices["vaults"]["-k"] = {c: {} for c in coindix_model.VAULT_KINDS}
            choices["vaults"]["-c"] = {c: {} for c in coindix_model.CHAINS}
            choices["vaults"]["-p"] = {c: {} for c in coindix_model.PROTOCOLS}
            choices["govp"]["-s"] = {c: {} for c in terramoney_fcd_model.GOV_COLUMNS}
            choices["govp"]["--status"] = {
                c: {} for c in terramoney_fcd_model.GOV_STATUSES
            }
            choices["validators"]["-s"] = {
                c: {} for c in terramoney_fcd_model.VALIDATORS_COLUMNS
            }

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = """[cmds]
    newsletter    Recent DeFi related newsletters [src][Substack][/src]
    dpi           DeFi protocols listed on DefiPulse [src][Defipulse][/src]
    funding       Funding rates - current or last 30 days average [src][Defirate][/src]
    borrow        DeFi borrow rates - current or last 30 days average [src][Defirate][/src]
    lending       DeFi ending rates - current or last 30 days average [src][Defirate][/src]
    vaults        Top DeFi Vaults on different blockchains [src][Coindix][/src]
[src][The Graph][/src] [info]Uniswap[/info]
    tokens        Tokens trade-able on Uniswap
    stats         Base statistics about Uniswap
    pairs         Recently added pairs on Uniswap
    pools         Pools by volume on Uniswap
    swaps         Recent swaps done on Uniswap
[src][Defi Llama][/src]
    ldapps        Lists dApps
    gdapps        Displays top DeFi dApps grouped by chain
    stvl          Displays historical values of the total sum of TVLs from all dApps
    dtvl          Displays historical total value locked (TVL) by dApp
[src][Terra Engineer][/src]
    aterra        Displays 30-day history of specified asset in terra address
    ayr           Displays 30-day history of anchor yield reserve
[src][Terra FCD][/src]
    sinfo         Displays staking info for provided terra account address
    validators    Displays information about terra blockchain validators
    govp          Displays terra blockchain governance proposals list
    gacc          Displays terra blockchain account growth history
    sratio        Displays terra blockchain staking ratio history
    sreturn       Displays terra blockchain staking returns history
[src][Smartstake][/src]
    lcsc         Displays Luna circulating supply changes[/cmds]
"""
        console.print(text=help_text, menu="Cryptocurrency - Decentralized Finance")

    @log_start_end(log=logger)
    def call_aterra(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="aterra",
            description="""
                Displays the 30-day history of an asset in a certain terra address.
                [Source: https://terra.engineer/]
            """,
        )
        parser.add_argument(
            "--asset",
            dest="asset",
            type=str,
            help="Terra asset {ust,luna,sdt} Default: ust",
            default=terraengineer_model.ASSETS[0],
            choices=terraengineer_model.ASSETS,
        )
        parser.add_argument(
            "--address",
            dest="address",
            type=check_terra_address_format,
            help="Terra address. Valid terra addresses start with 'terra'",
            required="-h" not in other_args,
        )

        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "--asset")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            terraengineer_view.display_terra_asset_history(
                export=ns_parser.export,
                address=ns_parser.address,
                asset=ns_parser.asset,
            )

    @log_start_end(log=logger)
    def call_ayr(self, other_args: List[str]):
        """Process ayr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ayr",
            description="""
                Displays the 30-day history of the Anchor Yield Reserve.
                An increasing yield reserve indicates that the return on collateral staked by borrowers in Anchor
                is greater than the yield paid to depositors. A decreasing yield reserve means yield paid
                to depositors is outpacing the staking returns of borrower's collateral.
                TLDR: Shows the address that contains UST that is paid on anchor interest earn.
                [Source: https://terra.engineer/]
            """,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            terraengineer_view.display_anchor_yield_reserve(export=ns_parser.export)

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

        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "-a")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            terramoney_fcd_view.display_account_staking_info(
                export=ns_parser.export, address=ns_parser.address, top=ns_parser.limit
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
            choices=[
                "validatorName",
                "tokensAmount",
                "votingPower",
                "commissionRate",
                "status",
                "uptime",
            ],
        )
        parser.add_argument(
            "--descend",
            action="store_true",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            terramoney_fcd_view.display_validators(
                export=ns_parser.export,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                top=ns_parser.limit,
            )

    @log_start_end(log=logger)
    def call_govp(self, other_args: List[str]):
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="govp",
            description="""
                Displays terra blockchain governance proposals list.
                [Source: https://fcd.terra.dev/swagger]
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="Number of proposals to show",
            default=10,
        )
        parser.add_argument(
            "-s",
            "--sort",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: id",
            default="id",
            choices=terramoney_fcd_model.GOV_COLUMNS,
        )
        parser.add_argument(
            "--status",
            dest="status",
            type=str,
            help="Status of proposal. Default: all",
            default="all",
            choices=terramoney_fcd_model.GOV_STATUSES,
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
            terramoney_fcd_view.display_gov_proposals(
                status=ns_parser.status,
                export=ns_parser.export,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                top=ns_parser.limit,
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
        parser.add_argument(
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            terramoney_fcd_view.display_account_growth(
                kind=ns_parser.kind,
                export=ns_parser.export,
                cumulative=ns_parser.cumulative,
                top=ns_parser.limit,
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

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            terramoney_fcd_view.display_staking_ratio_history(
                export=ns_parser.export, top=ns_parser.limit
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

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            terramoney_fcd_view.display_staking_returns_history(
                export=ns_parser.export, top=ns_parser.limit
            )

    @log_start_end(log=logger)
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

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            llama_view.display_grouped_defi_protocols(num=ns_parser.limit)

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
        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "-d")

        ns_parser = parse_known_args_and_warn(
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

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            llama_view.display_defi_tvl(top=ns_parser.limit, export=ns_parser.export)

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
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

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            substack_view.display_newsletters(
                top=ns_parser.limit, export=ns_parser.export
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

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            graph_view.display_uni_stats(export=ns_parser.export)

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
            "--descend",
            action="store_false",
            help="Flag to sort in descending order (lowest first)",
            dest="descend",
            default=False,
        )

        parser.add_argument(
            "-l",
            "--links",
            action="store_false",
            help="Flag to show vault link",
            dest="link",
            default=True,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            coindix_view.display_defi_vaults(
                chain=ns_parser.chain,
                kind=ns_parser.kind,
                protocol=ns_parser.protocol,
                top=ns_parser.limit,
                sortby=ns_parser.sortby,
                descend=ns_parser.descend,
                link=ns_parser.link,
                export=ns_parser.export,
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
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES, limit=5
        )

        if ns_parser:
            smartstake_view.display_luna_circ_supply_change(
                days=ns_parser.days,
                limit=ns_parser.limit,
                export=ns_parser.export,
            )
