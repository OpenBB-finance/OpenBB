""" Disc Controller """
__docformat__ = "numpy"
# pylint:disable=too-many-lines

import argparse
import difflib
from datetime import datetime
from typing import List

from matplotlib import pyplot as plt
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import EXPORT_ONLY_RAW_DATA_ALLOWED, get_flair
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_non_negative,
    check_positive,
    valid_date,
    check_int_range,
    try_except,
    system_clear,
)
from gamestonk_terminal.menu import session
from gamestonk_terminal.stocks.discovery import (
    ark_view,
    fidelity_view,
    seeking_alpha_view,
    shortinterest_view,
    yahoofinance_view,
    finnhub_view,
    geekofwallstreet_view,
    financedatabase_view,
    nasdaq_view,
)


class DiscoveryController:
    """Discovery Controller"""

    # Command choices
    CHOICES = [
        "?",
        "cls",
        "help",
        "q",
        "quit",
    ]

    CHOICES_COMMANDS = [
        "pipo",
        "fipo",
        "gainers",
        "losers",
        "ugs",
        "gtech",
        "active",
        "ulc",
        "asc",
        "ford",
        "arkord",
        "upcoming",
        "trending",
        "lowfloat",
        "hotpenny",
        "rtearn",
        "fds",
        "cnews",
        "rtat",
    ]

    CHOICES += CHOICES_COMMANDS

    def __init__(self):
        """Constructor"""
        self.disc_parser = argparse.ArgumentParser(add_help=False, prog="disc")
        self.disc_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

    @staticmethod
    def print_help():
        """Print help"""
        help_text = """
Discovery:
    cls            clear screen
    ?/help         show this menu again
    q              quit this menu, and shows back to main menu
    quit           quit to abandon program

Geek of Wall St:
    rtearn         realtime earnings from and expected moves
Finnhub:
    pipo           past IPOs dates
    fipo           future IPOs dates
Yahoo Finance:
    gainers        show latest top gainers
    losers         show latest top losers
    ugs            undervalued stocks with revenue and earnings growth in excess of 25%
    gtech          tech stocks with revenue and earnings growth more than 25%
    active         most active stocks by intraday trade volume
    ulc            potentially undervalued large cap stocks
    asc            small cap stocks with earnings growth rates better than 25%
Fidelity:
    ford           orders by Fidelity Customers
cathiesark.com:
    arkord         orders by ARK Investment Management LLC
Seeking Alpha:
    upcoming       upcoming earnings release dates
    trending       trending news
    cnews          customized news (buybacks, ipos, spacs, healthcare, politics)
shortinterest.com
    lowfloat       low float stocks under 10M shares float
pennystockflow.com
    hotpenny       today's hot penny stocks
Finance Database:
    fds            advanced Equities search based on country, sector, industry, name and/or description
NASDAQ Data Link (Formerly Quandl):
    rtat           top 10 retail traded stocks per day
"""
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

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

        (known_args, other_args) = self.disc_parser.parse_known_args(an_input.split())

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

    def call_help(self, _):
        """Process Help command"""
        self.print_help()

    def call_q(self, _):
        """Process Q command - quit the menu"""
        return False

    def call_quit(self, _):
        """Process Quit command - quit the program"""
        return True

    @try_except
    def call_rtearn(self, other_args: List[str]):
        """Process rtearn command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rtearn",
            description="""
                Realtime earnings data and expected moves. [Source: https://thegeekofwallstreet.com]
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

        geekofwallstreet_view.display_realtime_earnings(ns_parser.export)

    @try_except
    def call_pipo(self, other_args: List[str]):
        """Process pipo command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pipo",
            description="""
                Past IPOs dates. [Source: https://finnhub.io]
            """,
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_non_negative,
            default=5,
            help="Number of past days to look for IPOs.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        finnhub_view.past_ipo(
            num_days_behind=ns_parser.num,
            export=ns_parser.export,
        )

    @try_except
    def call_fipo(self, other_args: List[str]):
        """Process fipo command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="fipo",
            description="""
                Future IPOs dates. [Source: https://finnhub.io]
            """,
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_non_negative,
            default=5,
            help="Number of future days to look for IPOs.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        finnhub_view.future_ipo(
            num_days_ahead=ns_parser.num,
            export=ns_parser.export,
        )

    @try_except
    def call_gainers(self, other_args: List[str]):
        """Process gainers command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="gainers",
            description="Print up to 25 top gainers. [Source: Yahoo Finance]",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_int_range(1, 25),
            default=5,
            help="Number of stocks to display.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        yahoofinance_view.display_gainers(
            num_stocks=ns_parser.num,
            export=ns_parser.export,
        )

    @try_except
    def call_losers(self, other_args: List[str]):
        """Process losers command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="losers",
            description="Print up to 25 top losers. [Source: Yahoo Finance]",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_int_range(1, 25),
            default=5,
            help="Number of stocks to display.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        yahoofinance_view.display_losers(
            num_stocks=ns_parser.num,
            export=ns_parser.export,
        )

    @try_except
    def call_ugs(self, other_args: List[str]):
        """Process ugs command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ugs",
            description="""
                Print up to 25 undervalued stocks with revenue and earnings growth in excess of 25%.
                [Source: Yahoo Finance]
            """,
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_int_range(1, 25),
            default=5,
            help="Number of stocks to display.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        yahoofinance_view.display_ugs(
            num_stocks=ns_parser.num,
            export=ns_parser.export,
        )

    @try_except
    def call_gtech(self, other_args: List[str]):
        """Process gtech command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="gtech",
            description="""
                Print up to 25 top tech stocks with revenue and earnings growth in excess of 25%. [Source: Yahoo Finance]
            """,
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_int_range(1, 25),
            default=5,
            help="Number of stocks to display.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        yahoofinance_view.display_gtech(
            num_stocks=ns_parser.num,
            export=ns_parser.export,
        )

    @try_except
    def call_active(self, other_args: List[str]):
        """Process active command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="active",
            description="""
                Print up to 25 top most actively traded intraday tickers. [Source: Yahoo Finance]
            """,
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_int_range(1, 25),
            default=5,
            help="Number of stocks to display.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        yahoofinance_view.display_active(
            num_stocks=ns_parser.num,
            export=ns_parser.export,
        )

    @try_except
    def call_ulc(self, other_args: List[str]):
        """Process ulc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ulc",
            description="""
                Print up to 25 potentially undervalued large cap stocks. [Source: Yahoo Finance]
            """,
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_int_range(1, 25),
            default=5,
            help="Number of the stocks to display.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        yahoofinance_view.display_ulc(
            num_stocks=ns_parser.num,
            export=ns_parser.export,
        )

    @try_except
    def call_asc(self, other_args: List[str]):
        """Process asc command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="asc",
            description="""
                Print up to 25 small cap stocks with earnings growth rates better than 25%. [Source: Yahoo Finance]
            """,
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_int_range(1, 25),
            default=5,
            help="Number of the stocks to display.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        yahoofinance_view.display_asc(
            num_stocks=ns_parser.num,
            export=ns_parser.export,
        )

    @try_except
    def call_ford(self, other_args: List[str]):
        """Process ford command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ford",
            description="""
                Orders by Fidelity customers. Information shown in the table below
                is based on the volume of orders entered on the "as of" date shown. Securities
                identified are not recommended or endorsed by Fidelity and are displayed for
                informational purposes only. [Source: Fidelity]
            """,
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="n_num",
            type=check_positive,
            default=10,
            help="Number of top ordered stocks to be printed.",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        fidelity_view.orders_view(
            num=ns_parser.n_num,
            export=ns_parser.export,
        )

    @try_except
    def call_arkord(self, other_args: List[str]):
        """Process arkord command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="arkord",
            description="""
                Orders by ARK Investment Management LLC - https://ark-funds.com/. [Source: https://cathiesark.com]
            """,
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="n_num",
            type=check_positive,
            default=10,
            help="Last N ARK orders.",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sort_col",
            choices=[
                "date",
                "volume",
                "open",
                "high",
                "close",
                "low",
                "total",
                "weight",
                "shares",
            ],
            nargs="+",
            help="Colume to sort by",
            default="",
        )
        parser.add_argument(
            "-a",
            "-ascend",
            dest="ascend",
            help="Flag to sort in ascending order",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-b",
            "--buy_only",
            dest="buys_only",
            help="Flag to look at buys only",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-c",
            "--sell_only",
            dest="sells_only",
            help="Flag to look at sells only",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "-f",
            "--fund",
            type=str,
            default="",
            help="Filter by fund",
            dest="fund",
            choices=["ARKK", "ARKF", "ARKW", "ARKQ", "ARKG", "ARKX", ""],
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args and "-" not in other_args[0]:
            other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        ark_view.ark_orders_view(
            num=ns_parser.n_num,
            sort_col=ns_parser.sort_col,
            ascending=ns_parser.ascend,
            buys_only=ns_parser.buys_only,
            sells_only=ns_parser.sells_only,
            fund=ns_parser.fund,
            export=ns_parser.export,
        )

    @try_except
    def call_upcoming(self, other_args: List[str]):
        # TODO: switch to nasdaq
        """Process upcoming command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="upcoming",
            description="""Upcoming earnings release dates. [Source: Seeking Alpha]""",
        )
        parser.add_argument(
            "-p",
            "--pages",
            action="store",
            dest="n_pages",
            type=check_positive,
            default=10,
            help="Number of pages to read upcoming earnings from in Seeking Alpha website.",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="n_num",
            type=check_positive,
            default=1,
            help="Number of upcoming earnings release dates to display",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-n")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        seeking_alpha_view.upcoming_earning_release_dates(
            num_pages=ns_parser.n_pages,
            num_earnings=ns_parser.n_num,
            export=ns_parser.export,
        )

    @try_except
    def call_trending(self, other_args: List[str]):
        """Process trending command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="trending",
            description="""Trending news articles. [Source: Seeking Alpha]""",
        )
        parser.add_argument(
            "-i",
            "--id",
            action="store",
            dest="n_id",
            type=check_positive,
            default=-1,
            help="article ID",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="n_num",
            type=check_positive,
            default=5,
            help="number of articles being printed",
        )
        parser.add_argument(
            "-d",
            "--date",
            action="store",
            dest="s_date",
            type=valid_date,
            default=datetime.now().strftime("%Y-%m-%d"),
            help="starting date of articles",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-i")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        seeking_alpha_view.news(
            news_type="trending",
            article_id=ns_parser.n_id,
            num=ns_parser.n_num,
            start_date=ns_parser.s_date,
            export=ns_parser.export,
        )

    @try_except
    def call_lowfloat(self, other_args: List[str]):
        """Process lowfloat command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lowfloat",
            description="""
                Print top stocks with lowest float. LowFloat.com provides a convenient
                sorted database of stocks which have a float of under 10 million shares. Additional key
                data such as the number of outstanding shares, short interest, and company industry is
                displayed. Data is presented for the Nasdaq Stock Market, the New York Stock Exchange,
                the American Stock Exchange, and the Over the Counter Bulletin Board. [Source: www.lowfloat.com]
            """,
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="n_num",
            type=check_positive,
            default=10,
            help="Number of top stocks to print.",
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

        shortinterest_view.low_float(
            num=ns_parser.n_num,
            export=ns_parser.export,
        )

    @try_except
    def call_cnews(self, other_args: List[str]):
        """Process cnews command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="cnews",
            description="""Customized news. [Source: Seeking Alpha]""",
        )
        l_news_type = [
            "Top-News",
            "On-The-Move",
            "Market-Pulse",
            "Notable-Calls",
            "Buybacks",
            "Commodities",
            "Crypto",
            "Issuance",
            "Global",
            "Guidance",
            "IPOs",
            "SPACs",
            "Politics",
            "M-A",
            "Consumer",
            "Energy",
            "Financials",
            "Healthcare",
            "MLPs",
            "REITs",
            "Technology",
        ]
        parser.add_argument(
            "-t",
            "--type",
            action="store",
            dest="s_type",
            choices=[tnews.lower() for tnews in l_news_type],
            default="Top-News",
            help="number of news to display",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="n_num",
            type=check_positive,
            default=5,
            help="number of news to display",
        )
        parser.add_argument(
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if not ns_parser:
            return

        seeking_alpha_view.display_news(
            news_type=ns_parser.s_type,
            num=ns_parser.n_num,
            export=ns_parser.export,
        )

    @try_except
    def call_hotpenny(self, other_args: List[str]):
        """Process hotpenny command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="hotpenny",
            description="""
                This site provides a list of todays most active and hottest penny stocks. While not for everyone, penny
                stocks can be exciting and rewarding investments in many ways. With penny stocks, you can get more bang
                for the buck. You can turn a few hundred dollars into thousands, just by getting in on the right penny
                stock at the right time. Penny stocks are increasing in popularity. More and more investors of all age
                groups and skill levels are getting involved, and the dollar amounts they are putting into these
                speculative investments are representing a bigger portion of their portfolios.
                [Source: www.pennystockflow.com]
            """,
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="n_num",
            type=check_positive,
            default=10,
            help="Number of top stocks to print.",
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

        shortinterest_view.hot_penny_stocks(
            num=ns_parser.n_num,
            export=ns_parser.export,
        )

    @try_except
    def call_fds(self, other_args: List[str]):
        """Process fds command"""
        parser = argparse.ArgumentParser(
            description="Display a selection of Equities based on country, sector, industry, name and/or description "
            "filtered by market cap. If no arguments are given, return the equities with the highest "
            "market cap. [Source: Finance Database]",
            add_help=False,
        )

        parser.add_argument(
            "-c",
            "--country",
            default=None,
            nargs="+",
            dest="country",
            help="Specify the Equities selection based on a country",
        )

        parser.add_argument(
            "-s",
            "--sector",
            default=None,
            nargs="+",
            dest="sector",
            help="Specify the Equities selection based on a sector",
        )

        parser.add_argument(
            "-i",
            "--industry",
            default=None,
            nargs="+",
            dest="industry",
            help="Specify the Equities selection based on an industry",
        )

        parser.add_argument(
            "-n",
            "--name",
            default=None,
            nargs="+",
            dest="name",
            help="Specify the Equities selection based on the name",
        )

        parser.add_argument(
            "-d",
            "--description",
            default=None,
            nargs="+",
            dest="description",
            help="Specify the Equities selection based on the description (not shown in table)",
        )

        parser.add_argument(
            "-m",
            "--marketcap",
            default=["Large"],
            choices=["Small", "Mid", "Large"],
            nargs="+",
            dest="marketcap",
            type=str.title,
            help="Specify the Equities selection based on Market Cap",
        )

        parser.add_argument(
            "-ie",
            "--include_exchanges",
            action="store_false",
            help="When used, data from different exchanges is also included. This leads to a much larger "
            "pool of data due to the same company being listed on multiple exchanges",
        )

        parser.add_argument(
            "-a",
            "--amount",
            default=10,
            type=int,
            dest="amount",
            help="Enter the number of Equities you wish to see in the Tabulate window",
        )

        parser.add_argument(
            "-o",
            "--options ",
            choices=["countries", "sectors", "industries"],
            default=None,
            dest="options",
            help="Obtain the available options for country, sector and industry",
        )

        ns_parser = parse_known_args_and_warn(parser, other_args)

        if not ns_parser:
            return

        financedatabase_view.show_equities(
            country=ns_parser.country,
            sector=ns_parser.sector,
            industry=ns_parser.industry,
            name=ns_parser.name,
            description=ns_parser.description,
            marketcap=ns_parser.marketcap,
            include_exchanges=ns_parser.include_exchanges,
            amount=ns_parser.amount,
            options=ns_parser.options,
        )

    @try_except
    def call_rtat(self, other_args: List[str]):
        """Process fds command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rtat",
            description="""
                Tracking over $30B USD/day of individual investors trades,
                RTAT gives a daily view into retail activity and sentiment for over 9,500 US traded stocks,
                ADRs, and ETPs
            """,
        )
        parser.add_argument(
            "-n",
            "--num",
            dest="n_days",
            help="Number of days to show",
            default=3,
            type=check_positive,
        )

        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if not ns_parser:
            return
        nasdaq_view.display_top_retail(n_days=ns_parser.n_days, export=ns_parser.export)


def menu():
    """Discovery Menu"""

    disc_controller = DiscoveryController()
    disc_controller.call_help(None)

    # Loop forever and ever
    while True:
        # Get input command from user
        if session and gtff.USE_PROMPT_TOOLKIT:
            completer = NestedCompleter.from_nested_dict(
                {c: None for c in disc_controller.CHOICES}
            )

            an_input = session.prompt(
                f"{get_flair()} (stocks)>(disc)> ",
                completer=completer,
            )
        else:
            an_input = input(f"{get_flair()} (stocks)>(disc)> ")

        try:
            plt.close("all")

            process_input = disc_controller.switch(an_input)

            if process_input is not None:
                return process_input

        except SystemExit:
            print("The command selected doesn't exist\n")
            similar_cmd = difflib.get_close_matches(
                an_input, disc_controller.CHOICES, n=1, cutoff=0.7
            )

            if similar_cmd:
                print(f"Did you mean '{similar_cmd[0]}'?\n")
            continue
