"""Cryptocurrency Overview Controller"""
__docformat__ = "numpy"

# pylint: disable=R0904, C0302, W0622
import argparse
import difflib
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.cryptocurrency.discovery.pycoingecko_model import (
    get_categories_keys,
)
from openbb_terminal.cryptocurrency.overview import (
    blockchaincenter_view,
    coinbase_model,
    coinbase_view,
    coinpaprika_model,
    coinpaprika_view,
    cryptopanic_model,
    cryptopanic_view,
    loanscan_model,
    loanscan_view,
    pycoingecko_model,
    pycoingecko_view,
    rekt_model,
    rekt_view,
    tokenterminal_model,
    tokenterminal_view,
    withdrawalfees_model,
    withdrawalfees_view,
)
from openbb_terminal.cryptocurrency.overview.blockchaincenter_model import DAYS
from openbb_terminal.cryptocurrency.overview.coinpaprika_model import (
    get_all_contract_platforms,
)
from openbb_terminal.cryptocurrency.overview.coinpaprika_view import CURRENCIES
from openbb_terminal.cryptocurrency.overview.glassnode_view import display_btc_rainbow
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_FIGURES_ALLOWED,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_positive,
    valid_date,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class OverviewController(BaseController):
    """Overview Controller class"""

    CHOICES_COMMANDS = [
        "hm",
        "global",
        "defi",
        "stables",
        "exchanges",
        "exrates",
        "indexes",
        "derivatives",
        "categories",
        "hold",
        "markets",
        "exmarkets",
        "info",
        "platforms",
        "contracts",
        "pairs",
        "news",
        "wf",
        "ewf",
        "wfpe",
        "btcrb",
        "altindex",
        "ch",
        "cr",
        "fun",
    ]

    PATH = "/crypto/ov/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            choices["wfpe"].update(
                {c: {} for c in withdrawalfees_model.POSSIBLE_CRYPTOS}
            )

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("crypto/ov/", 105)
        mt.add_cmd("global")
        mt.add_cmd("defi")
        mt.add_cmd("stables")
        mt.add_cmd("exchanges")
        mt.add_cmd("exrates")
        mt.add_cmd("indexes")
        mt.add_cmd("derivatives")
        mt.add_cmd("categories")
        mt.add_cmd("hold")
        mt.add_cmd("hm")
        mt.add_cmd("info")
        mt.add_cmd("markets")
        mt.add_cmd("exmarkets")
        mt.add_cmd("platforms")
        mt.add_cmd("contracts")
        mt.add_cmd("pairs")
        mt.add_cmd("news")
        mt.add_cmd("wf")
        mt.add_cmd("ewf")
        mt.add_cmd("wfpe")
        mt.add_cmd("altindex")
        mt.add_cmd("btcrb")
        mt.add_cmd("ch")
        mt.add_cmd("cr")
        mt.add_cmd("fun")
        console.print(text=mt.menu_text, menu="Cryptocurrency - Overview")

    @log_start_end(log=logger)
    def call_hm(self, other_args):
        """Process hm command"""
        parser = argparse.ArgumentParser(
            prog="hm",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Display cryptocurrencies heatmap with daily percentage change [Source: https://coingecko.com]
            Accepts --category or -c to display only coins of a certain category
            (default no category to display all coins ranked by market cap).
            You can look on only top N number of records with --limit.
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=int,
            help="Display N items",
            default=10,
        )
        parser.add_argument(
            "-c",
            "--category",
            default="",
            dest="category",
            help="Category (e.g., stablecoins). Empty for no category",
            choices=get_categories_keys(),
            metavar="CATEGORY",
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "-c")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_crypto_heatmap(
                category=ns_parser.category,
                limit=ns_parser.limit,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_fun(self, other_args):
        """Process fun command"""
        parser = argparse.ArgumentParser(
            prog="fun",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Display fundamental metrics overview [Source: Token Terminal]""",
        )
        parser.add_argument(
            "-m",
            "--metric",
            required=True,
            choices=tokenterminal_model.METRICS,
            dest="metric",
            help="Choose metric of interest",
        )
        parser.add_argument(
            "-c",
            "--category",
            default="",
            choices=tokenterminal_model.CATEGORIES,
            dest="category",
            help="Choose category of interest",
        )
        parser.add_argument(
            "-t",
            "--timeline",
            default="24h",
            choices=tokenterminal_model.TIMELINES,
            dest="timeline",
            help="Choose timeline of interest",
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
            "--limit",
            dest="limit",
            type=int,
            help="Display N items",
            default=10,
        )
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "-m")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_FIGURES_ALLOWED
        )
        if ns_parser:
            tokenterminal_view.display_fundamental_metrics(
                metric=ns_parser.metric,
                category=ns_parser.category,
                timeline=ns_parser.timeline,
                ascend=ns_parser.reverse,
                limit=ns_parser.limit,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_ch(self, other_args):
        """Process ch command"""
        parser = argparse.ArgumentParser(
            prog="ch",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Display list of major crypto-related hacks [Source: https://rekt.news]
            Can be sorted by {Platform,Date,Amount [$],Audit,Slug,URL} with --sortby
            and reverse the display order with --reverse
            Show only N elements with --limit
            Accepts --slug or -s to check individual crypto hack (e.g., -s polynetwork-rekt)
            """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=int,
            help="Display N items",
            default=15,
        )
        parser.add_argument(
            "--sortby",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Amount [$]",
            default="Amount [$]",
            nargs="+",
            choices=rekt_model.HACKS_COLUMNS,
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
            "-s",
            "--slug",
            dest="slug",
            type=str,
            help="Slug to check crypto hack (e.g., polynetwork-rekt)",
            default="",
            choices=rekt_model.get_crypto_hack_slugs(),
            metavar="SORTBY",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-s")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            rekt_view.display_crypto_hacks(
                slug=ns_parser.slug,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                sortby=" ".join(ns_parser.sortby),
                ascend=not ns_parser.reverse,
            )

    @log_start_end(log=logger)
    def call_btcrb(self, other_args: List[str]):
        """Process btcrb command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="btcrb",
            description="""Display bitcoin rainbow chart overtime including halvings.
            [Price data from source: https://glassnode.com]
            [Inspired by: https://blockchaincenter.net]""",
        )
        parser.add_argument(
            "-s",
            "--since",
            dest="since",
            type=valid_date,
            help="Initial date. Default is initial BTC date: 2010-01-01",
            default=datetime(2010, 1, 1).strftime("%Y-%m-%d"),
        )

        parser.add_argument(
            "-u",
            "--until",
            dest="until",
            type=valid_date,
            help="Final date. Default is current date",
            default=datetime.now().strftime("%Y-%m-%d"),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )
        if ns_parser:
            display_btc_rainbow(
                start_date=ns_parser.since.strftime("%Y-%m-%d"),
                end_date=ns_parser.until.strftime("%Y-%m-%d"),
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_altindex(self, other_args: List[str]):
        """Process altindex command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="altindex",
            description="""Display altcoin index overtime.
                    If 75% of the Top 50 coins performed better than Bitcoin over periods of time
                    (30, 90 or 365 days) it is Altcoin Season. Excluded from the Top 50 are
                    Stablecoins (Tether, DAI…) and asset backed tokens (WBTC, stETH, cLINK,…)
                    [Source: https://blockchaincenter.net]
                """,
        )

        parser.add_argument(
            "-p",
            "--period",
            type=int,
            help="Period of time to check if how altcoins have performed against btc (30, 90, 365)",
            dest="period",
            default=365,
            choices=DAYS,
        )

        parser.add_argument(
            "-s",
            "--since",
            dest="since",
            type=valid_date,
            help="Start date (default: 1 year before, e.g., 2021-01-01)",
            default=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        )

        parser.add_argument(
            "-u",
            "--until",
            dest="until",
            type=valid_date,
            help="Final date. Default is current date",
            default=datetime.now().strftime("%Y-%m-%d"),
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_BOTH_RAW_DATA_AND_FIGURES
        )

        if ns_parser:
            blockchaincenter_view.display_altcoin_index(
                start_date=ns_parser.since.strftime("%Y-%m-%d"),
                end_date=ns_parser.until.strftime("%Y-%m-%d"),
                period=ns_parser.period,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_wf(self, other_args: List[str]):
        """Process wf command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="wf",
            description="""
                Display top coins withdrawal fees
                [Source: https://withdrawalfees.com/]
            """,
        )

        parser.add_argument(
            "-l",
            "--limit",
            type=int,
            help="Limit number of coins to display withdrawal fees. Default 10",
            dest="limit",
            default=10,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            withdrawalfees_view.display_overall_withdrawal_fees(
                limit=ns_parser.limit, export=ns_parser.export
            )

    @log_start_end(log=logger)
    def call_ewf(self, other_args: List[str]):
        """Process ewf command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ewf",
            description="""
                Display exchange withdrawal fees
                [Source: https://withdrawalfees.com/]
            """,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            withdrawalfees_view.display_overall_exchange_withdrawal_fees(
                export=ns_parser.export
            )

    @log_start_end(log=logger)
    def call_wfpe(self, other_args: List[str]):
        """Process wfpe command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="wfpe",
            description="""
                Coin withdrawal fees per exchange
                [Source: https://withdrawalfees.com/]
            """,
        )

        parser.add_argument(
            "-c",
            "--coin",
            default="bitcoin",
            type=str,
            dest="coin",
            help="Coin to check withdrawal fees in long format (e.g., bitcoin, ethereum)",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if ns_parser.coin:
                if ns_parser.coin in withdrawalfees_model.POSSIBLE_CRYPTOS:
                    withdrawalfees_view.display_crypto_withdrawal_fees(
                        symbol=ns_parser.coin, export=ns_parser.export
                    )
                else:
                    console.print(f"Coin '{ns_parser.coin}' does not exist.")

                    similar_cmd = difflib.get_close_matches(
                        ns_parser.coin,
                        withdrawalfees_model.POSSIBLE_CRYPTOS,
                        n=1,
                        cutoff=0.75,
                    )
                    if similar_cmd:
                        console.print(f"Replacing by '{similar_cmd[0]}'")
                        withdrawalfees_view.display_crypto_withdrawal_fees(
                            symbol=similar_cmd[0], export=ns_parser.export
                        )
                    else:
                        similar_cmd = difflib.get_close_matches(
                            ns_parser.coin,
                            withdrawalfees_model.POSSIBLE_CRYPTOS,
                            n=1,
                            cutoff=0.5,
                        )
                        if similar_cmd:
                            console.print(f"Did you mean '{similar_cmd[0]}'?")
            else:
                console.print(
                    f"Couldn't find any coin with provided name: {ns_parser.coin}. "
                    f"Please choose one from list: {withdrawalfees_model.POSSIBLE_CRYPTOS}\n"
                )

    @log_start_end(log=logger)
    def call_hold(self, other_args):
        """Process hold command"""
        parser = argparse.ArgumentParser(
            prog="hold",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
                Shows overview of public companies that holds ethereum or bitcoin.
                You can find there most important metrics like:
                Total Bitcoin Holdings, Total Value (USD), Public Companies Bitcoin Dominance, Companies
                """,
        )

        parser.add_argument(
            "-c",
            "--coin",
            dest="coin",
            type=str,
            help="companies with ethereum or bitcoin",
            default="bitcoin",
            choices=pycoingecko_model.HOLD_COINS,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number of records",
            default=5,
        )
        parser.add_argument(
            "--bar",
            action="store_true",
            help="Flag to show bar chart",
            dest="bar",
            default=False,
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_holdings_overview(
                symbol=ns_parser.coin,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                show_bar=ns_parser.bar,
                limit=ns_parser.limit,
            )

    @log_start_end(log=logger)
    def call_categories(self, other_args):
        """Process top_categories command"""
        parser = argparse.ArgumentParser(
            prog="categories",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows top cryptocurrency categories by market capitalization. It includes categories like:
            stablecoins, defi, solana ecosystem, polkadot ecosystem and many others.
            You can sort by {}, using --sortby parameter""",
        )

        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number of records",
            default=15,
        )

        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: market_cap_desc",
            default="Market_Cap",
            choices=[
                "Name",
                "Market_Cap",
                "Market_Cap_Change_24H",
                "Top_3_Coins",
                "Volume_24H",
            ],
        )

        parser.add_argument(
            "--pie",
            action="store_true",
            help="Flag to show pie chart",
            dest="pie",
            default=False,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_categories(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                sortby=ns_parser.sortby,
                pie=ns_parser.pie,
            )

    # TODO: solve sort (similar to losers from discovery)
    @log_start_end(log=logger)
    def call_stables(self, other_args):
        """Process stables command"""
        parser = argparse.ArgumentParser(
            prog="stables",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows stablecoins by market capitalization.
                Stablecoins are cryptocurrencies that attempt to peg their market value to some external reference
                like the U.S. dollar or to a commodity's price such as gold.
                You can display only N number of coins with --limit parameter.
                You can sort data by {} with --sortby""",
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: market_cap",
            default="Market_Cap_[$]",
            choices=[
                "Symbol",
                "Name",
                "Price_[$]",
                "Market_Cap_[$]",
                "Market_Cap_Rank",
                "Change_7d_[%]",
                "Change_24h_[%]",
                "Volume_[$]",
            ],
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
            "--pie",
            action="store_true",
            help="Flag to show pie chart",
            dest="pie",
            default=False,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_stablecoins(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                pie=ns_parser.pie,
            )

    @log_start_end(log=logger)
    def call_cr(self, other_args):
        """Process cr command"""
        parser = argparse.ArgumentParser(
            prog="cr",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Displays crypto {borrow,supply} interest rates for cryptocurrencies across several platforms.
                You can select rate type with --type {borrow,supply}
                You can display only N number of platforms with --limit parameter.""",
        )

        parser.add_argument(
            "-t",
            "--type",
            dest="type",
            type=str,
            help="Select interest rate type",
            default="supply",
            choices=["borrow", "supply"],
        )
        parser.add_argument(
            "-c",
            "--cryptocurrrencies",
            dest="cryptos",
            type=loanscan_model.check_valid_coin,
            help=f"""Cryptocurrencies to search interest rates for separated by comma.
            Default: BTC,ETH,USDT,USDC. Options: {",".join(loanscan_model.CRYPTOS)}""",
            default="BTC,ETH,USDT,USDC",
            choices=loanscan_model.CRYPTOS,
            metavar="CRYPTOS",
        )

        parser.add_argument(
            "-p",
            "--platforms",
            dest="platforms",
            type=loanscan_model.check_valid_platform,
            help=f"""Platforms to search interest rates in separated by comma.
            Default: BlockFi,Ledn,SwissBorg,Youhodler. Options: {",".join(loanscan_model.PLATFORMS)}""",
            default="BlockFi,Ledn,SwissBorg,Youhodler",
            choices=loanscan_model.PLATFORMS,
            metavar="PLATFORMS",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED, limit=10
        )
        if ns_parser:
            loanscan_view.display_crypto_rates(
                rate_type=ns_parser.type,
                symbols=ns_parser.cryptos,
                platforms=ns_parser.platforms,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_exchanges(self, other_args):
        """Process exchanges command"""
        filters = (
            pycoingecko_model.EXCHANGES_FILTERS + coinpaprika_model.EXCHANGES_FILTERS
        )
        parser = argparse.ArgumentParser(
            prog="exchanges",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows Top Crypto Exchanges
                You can display only N number exchanges with --limit parameter.
                You can sort data by Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC with --sortby
                Or you can sort data by 'name', 'currencies', 'markets', 'fiats', 'confidence',
                'volume_24h', 'volume_7d', 'volume_30d', 'sessions_per_month'
                if you are using the alternative source CoinPaprika
                and also with --reverse flag to sort ascending.
                Flag --urls will display urls.
                Displays: Trust_Score, Id, Name, Country, Year_Established, Trade_Volume_24h_BTC""",
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=filters,
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
            "-u",
            "--urls",
            dest="urls",
            action="store_true",
            help="Flag to add a url column. Works only with CoinGecko source",
            default=False,
        )
        parser.add_argument(
            "--vs",
            help="Quoted currency. Default: USD. Works only with CoinPaprika source",
            dest="vs",
            default="USD",
            type=str,
            choices=CURRENCIES,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.source == "CoinGecko":
                pycoingecko_view.display_exchanges(
                    limit=ns_parser.limit,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                    sortby=ns_parser.sortby,
                    ascend=ns_parser.reverse,
                    links=ns_parser.urls,
                )
            elif ns_parser.source == "CoinPaprika":
                coinpaprika_view.display_all_exchanges(
                    symbol=ns_parser.vs,
                    limit=ns_parser.limit,
                    ascend=ns_parser.reverse,
                    sortby=ns_parser.sortby,
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_exrates(self, other_args):
        """Process exchange_rates command"""
        parser = argparse.ArgumentParser(
            prog="exrates",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
                Shows list of crypto, fiats, commodity exchange rates from CoinGecko
                You can look on only N number of records with --limit,
                You can sort by Index, Name, Unit, Value, Type, and also use --reverse flag to sort descending.""",
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Index",
            default="Index",
            choices=pycoingecko_model.EXRATES_FILTERS,
        )
        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in ascending order by default. "
                "Reverse flag will sort it in an descending way. "
                "Only works when raw data is displayed."
            ),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_exchange_rates(
                sortby=ns_parser.sortby,
                limit=ns_parser.limit,
                ascend=not ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_indexes(self, other_args):
        """Process indexes command"""
        parser = argparse.ArgumentParser(
            prog="indexes",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows list of crypto indexes from CoinGecko.
            Each crypto index is made up of a selection of cryptocurrencies,
            grouped together and weighted by market cap.
            You can display only N number of indexes with --limit parameter.
            You can sort data by Rank, Name, Id, Market, Last, MultiAsset with --sortby
            and also with --reverse flag to sort descending.
            Displays: Rank, Name, Id, Market, Last, MultiAsset
                """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=pycoingecko_model.INDEXES_FILTERS,
        )
        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in ascending order by default. "
                "Reverse flag will sort it in an descending way. "
                "Only works when raw data is displayed."
            ),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_indexes(
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=not ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_derivatives(self, other_args):
        """Process derivatives command"""
        parser = argparse.ArgumentParser(
            prog="derivatives",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows list of crypto derivatives from CoinGecko
               Crypto derivatives are secondary contracts or financial tools that derive their value from a primary
               underlying asset. In this case, the primary asset would be a cryptocurrency such as Bitcoin.
               The most popular crypto derivatives are crypto futures, crypto options, and perpetual contracts.
               You can look on only N number of records with --limit,
               You can sort by Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread, Funding_Rate,
               Volume_24h with by and also with --reverse flag to set it to sort descending.
               Displays:
                   Rank, Market, Symbol, Price, Pct_Change_24h, Contract_Type, Basis, Spread, Funding_Rate, Volume_24h
                   """,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: Rank",
            default="Rank",
            choices=pycoingecko_model.DERIVATIVES_FILTERS,
        )
        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in ascending order by default. "
                "Reverse flag will sort it in an descending way. "
                "Only works when raw data is displayed."
            ),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_derivatives(
                limit=ns_parser.limit,
                sortby=ns_parser.sortby,
                ascend=not ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_global(self, other_args):
        """Process global command"""
        parser = argparse.ArgumentParser(
            prog="global",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows global statistics about Crypto Market""",
        )

        parser.add_argument(
            "--pie",
            action="store_true",
            help="Flag to show pie chart with market cap distribution. Works only with CoinGecko source",
            dest="pie",
            default=False,
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            if ns_parser.source == "CoinGecko":
                pycoingecko_view.display_global_market_info(
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                    pie=ns_parser.pie,
                )
            elif ns_parser.source == "CoinPaprika":
                coinpaprika_view.display_global_market(
                    export=ns_parser.export,
                    sheet_name=" ".join(ns_parser.sheet_name)
                    if ns_parser.sheet_name
                    else None,
                )

    @log_start_end(log=logger)
    def call_defi(self, other_args):
        """Process defi command"""
        parser = argparse.ArgumentParser(
            prog="defi",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Shows global DeFi statistics
               DeFi or Decentralized Finance refers to financial services that are built
               on top of distributed networks with no central intermediaries.
               Displays metrics like:
                   Market Cap, Trading Volume, Defi Dominance, Top Coins...""",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            pycoingecko_view.display_global_defi_info(
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_markets(self, other_args):
        """Process markets command"""
        parser = argparse.ArgumentParser(
            prog="markets",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Show market related (price, supply, volume) coin information for all coins on CoinPaprika.
            You can display only N number of coins with --limit parameter.
            You can sort data by rank, name, symbol, price, volume_24h, mcap_change_24h, pct_change_1h, pct_change_24h,
            ath_price, pct_from_ath, --sortby parameter and also with --reverse flag to sort ascending.
            Displays:
               rank, name, symbol, price, volume_24h, mcap_change_24h,
               pct_change_1h, pct_change_24h, ath_price, pct_from_ath,
                """,
        )
        parser.add_argument(
            "--vs",
            help="Quoted currency. Default USD",
            dest="vs",
            default="USD",
            type=str,
            choices=CURRENCIES,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: rank",
            default="rank",
            choices=coinpaprika_model.MARKETS_FILTERS,
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
            coinpaprika_view.display_all_coins_market_info(
                symbol=ns_parser.vs,
                limit=ns_parser.limit,
                ascend=ns_parser.reverse,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                sortby=ns_parser.sortby,
            )

    @log_start_end(log=logger)
    def call_exmarkets(self, other_args):
        """Process exmarkets command"""
        parser = argparse.ArgumentParser(
            prog="exmarkets",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Get all exchange markets found for given exchange
                You can display only N number of records with --limit parameter.
                You can sort data by pair, base_currency_name, quote_currency_name, market_url, category,
                reported_volume_24h_share, trust_score --sortby parameter and also with --reverse flag to sort ascending.
                You can use additional flag --urls to see urls for each market
                Displays:
                    exchange_id, pair, base_currency_name, quote_currency_name, market_url,
                    category, reported_volume_24h_share, trust_score,""",
        )
        parser.add_argument(
            "-e",
            "--exchange",
            help="Identifier of exchange e.g for Binance Exchange -> binance",
            dest="exchange",
            default="binance",
            type=str,
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
            "--sortby",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: reported_volume_24h_share",
            default="reported_volume_24h_share",
            choices=coinpaprika_model.EXMARKETS_FILTERS,
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
            "-u",
            "--urls",
            dest="urls",
            action="store_true",
            help="""Flag to show urls. If you will use that flag you will see only:
                exchange, pair, trust_score, market_url columns""",
            default=False,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-e")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_exchange_markets(
                exchange=ns_parser.exchange,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                links=ns_parser.urls,
            )

    @log_start_end(log=logger)
    def call_info(self, other_args):
        """Process info command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="info",
            description="""Show basic coin information for all coins from CoinPaprika API
                You can display only N number of coins with --limit parameter.
                You can sort data by rank, name, symbol, price, volume_24h, circulating_supply,
                total_supply, max_supply, market_cap, beta_value, ath_price --sortby parameter
                and also with --reverse flag to sort descending.

                Displays:
                    rank, name, symbol, price, volume_24h, circulating_supply,
                    total_supply, max_supply, market_cap, beta_value, ath_price
                """,
        )
        parser.add_argument(
            "--vs",
            help="Quoted currency. Default USD",
            dest="vs",
            default="USD",
            type=str,
            choices=CURRENCIES,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=20,
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: rank",
            default="rank",
            choices=coinpaprika_model.INFO_FILTERS,
        )
        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in ascending order by default. "
                "Reverse flag will sort it in an descending way. "
                "Only works when raw data is displayed."
            ),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_all_coins_info(
                symbol=ns_parser.vs,
                limit=ns_parser.limit,
                ascend=not ns_parser.reverse,
                sortby=ns_parser.sortby,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_platforms(self, other_args):
        """Process platforms command"""
        parser = argparse.ArgumentParser(
            prog="platforms",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""List all smart contract platforms like ethereum, solana, cosmos, polkadot, kusama""",
        )

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_all_platforms(
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_contracts(self, other_args):
        """Process contracts command"""
        platforms = get_all_contract_platforms()["platform_id"].tolist()

        parser = argparse.ArgumentParser(
            prog="contracts",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""Gets all contract addresses for given platform.
               Provide platform id with -p/--platform parameter
               You can display only N number of smart contracts with --limit parameter.
               You can sort data by id, type, active, balance  --sortby parameter
               and also with --reverse flag to sort descending.

               Displays:
                   id, type, active, balance
               """,
        )
        parser.add_argument(
            "-p",
            "--platform",
            help="Blockchain platform like eth-ethereum",
            dest="platform",
            default="eth-ethereum",
            type=str,
            choices=platforms,
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=15,
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            type=str,
            help="Sort by given column",
            default="id",
            choices=coinpaprika_model.CONTRACTS_FILTERS,
        )
        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in ascending order by default. "
                "Reverse flag will sort it in an descending way. "
                "Only works when raw data is displayed."
            ),
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-p")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinpaprika_view.display_contracts(
                symbol=ns_parser.platform,
                limit=ns_parser.limit,
                ascend=not ns_parser.reverse,
                sortby=ns_parser.sortby,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_pairs(self, other_args):
        """Process pairs command"""
        parser = argparse.ArgumentParser(
            prog="pairs",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Shows available trading pairs on Coinbase ",
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=int,
            help="display N number of pairs >=10",
            default=15,
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: id",
            default="id",
            choices=coinbase_model.PAIRS_FILTERS,
        )
        parser.add_argument(
            "-r",
            "--reverse",
            action="store_true",
            dest="reverse",
            default=False,
            help=(
                "Data is sorted in ascending order by default. "
                "Reverse flag will sort it in an descending way. "
                "Only works when raw data is displayed."
            ),
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            coinbase_view.display_trading_pairs(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                sortby=ns_parser.sortby,
                ascend=not ns_parser.reverse,
            )

    @log_start_end(log=logger)
    def call_news(self, other_args):
        """Process news command"""
        parser = argparse.ArgumentParser(
            prog="news",
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="Display recent news from CryptoPanic aggregator platform. [Source: https://cryptopanic.com/]",
        )
        parser.add_argument(
            "-l",
            "--limit",
            dest="limit",
            type=check_positive,
            help="display N number records",
            default=20,
        )
        parser.add_argument(
            "-k",
            "--kind",
            dest="kind",
            type=str,
            help="Filter by category of news. Available values: news or media.",
            default="news",
            choices=cryptopanic_model.CATEGORIES,
        )
        parser.add_argument(
            "--filter",
            dest="filter",
            type=str,
            help="Filter by kind of news. One from list: rising|hot|bullish|bearish|important|saved|lol",
            default=None,
            required=False,
            choices=cryptopanic_model.FILTERS,
        )
        parser.add_argument(
            "-r",
            "--region",
            dest="region",
            type=str,
            help="Filter news by regions. Available regions are: en (English), de (Deutsch), nl (Dutch), es (Español), "
            "fr (Français), it (Italiano), pt (Português), ru (Русский)",
            default="en",
            choices=cryptopanic_model.REGIONS,
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sortby",
            type=str,
            help="Sort by given column. Default: published_at",
            default="published_at",
            choices=cryptopanic_model.SORT_FILTERS,
        )
        parser.add_argument(
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
            "-u",
            "--urls",
            dest="urls",
            action="store_true",
            help="Flag to show urls column.",
            default=False,
        )
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            cryptopanic_view.display_news(
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
                sortby=ns_parser.sortby,
                ascend=ns_parser.reverse,
                links=ns_parser.urls,
                post_kind=ns_parser.kind,
                filter_=ns_parser.filter,
                region=ns_parser.region,
            )
