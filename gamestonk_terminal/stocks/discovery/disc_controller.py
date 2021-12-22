""" Discovery Controller Module """
__docformat__ = "numpy"

import argparse
import difflib
from datetime import datetime
from typing import List, Union
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_non_negative,
    check_positive,
    check_int_range,
    try_except,
    system_clear,
    get_flair,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    valid_date,
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
    nasdaq_view,
)


# pylint:disable=C0302


class DiscoveryController:
    """Discovery Controller class"""

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
        "cnews",
        "rtat",
    ]
    CHOICES += CHOICES_COMMANDS

    arkord_sortby_choices = [
        "date",
        "volume",
        "open",
        "high",
        "close",
        "low",
        "total",
        "weight",
        "shares",
    ]
    arkord_fund_choices = ["ARKK", "ARKF", "ARKW", "ARKQ", "ARKG", "ARKX", ""]
    cnews_type_choices = [
        nt.lower()
        for nt in [
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
    ]

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        self.disc_parser = argparse.ArgumentParser(add_help=False, prog="disc")
        self.disc_parser.add_argument(
            "cmd",
            choices=self.CHOICES,
        )

        self.completer: Union[None, NestedCompleter] = None

        if session and gtff.USE_PROMPT_TOOLKIT:

            choices: dict = {c: {} for c in self.CHOICES}
            choices["arkord"]["-s"] = {c: None for c in self.arkord_sortby_choices}
            choices["arkord"]["--sortby"] = {
                c: None for c in self.arkord_sortby_choices
            }
            choices["arkord"]["-f"] = {c: None for c in self.arkord_fund_choices}
            choices["arkord"]["--fund"] = {c: None for c in self.arkord_fund_choices}
            choices["cnews"]["-t"] = {c: None for c in self.cnews_type_choices}
            choices["cnews"]["--type"] = {c: None for c in self.cnews_type_choices}

            self.completer = NestedCompleter.from_nested_dict(choices)

        if queue:
            self.queue = queue
        else:
            self.queue = list()

    def print_help(self):
        """Print help"""
        help_text = """
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
NASDAQ Data Link (Formerly Quandl):
    rtat           top 10 retail traded stocks per day
"""
        print(help_text)

    def switch(self, an_input: str):
        """Process and dispatch input

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

        (known_args, other_args) = self.disc_parser.parse_known_args(an_input.split())

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
        self.queue.insert(0, "disc")
        self.queue.insert(0, "stocks")
        self.queue.insert(0, "reset")
        self.queue.insert(0, "quit")
        self.queue.insert(0, "quit")

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_non_negative,
            default=5,
            help="Limit of past days to look for IPOs.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finnhub_view.past_ipo(
                num_days_behind=ns_parser.limit,
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_non_negative,
            default=5,
            help="Limit of future days to look for IPOs.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            finnhub_view.future_ipo(
                num_days_ahead=ns_parser.limit,
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=5,
            help="Limit of stocks to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_gainers(
                num_stocks=ns_parser.limit,
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=5,
            help="Limit of stocks to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_losers(
                num_stocks=ns_parser.limit,
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=5,
            help="Limit of stocks to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_ugs(
                num_stocks=ns_parser.limit,
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=5,
            help="Limit of stocks to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_gtech(
                num_stocks=ns_parser.limit,
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=5,
            help="Limit of stocks to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_active(
                num_stocks=ns_parser.limit,
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=5,
            help="Limit of stocks to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_ulc(
                num_stocks=ns_parser.limit,
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=5,
            help="Limit of stocks to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            yahoofinance_view.display_asc(
                num_stocks=ns_parser.limit,
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_int_range(1, 25),
            default=5,
            help="Limit of stocks to display.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            fidelity_view.orders_view(
                num=ns_parser.limit,
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=10,
            help="Limit of stocks to display.",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            dest="sort_col",
            choices=self.arkord_sortby_choices,
            nargs="+",
            help="Column to sort by",
            default="",
        )
        parser.add_argument(
            "-a",
            "--ascend",
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
            choices=self.arkord_fund_choices,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            ark_view.ark_orders_view(
                num=ns_parser.limit,
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=1,
            help="Limit of upcoming earnings release dates to display.",
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            seeking_alpha_view.upcoming_earning_release_dates(
                num_pages=ns_parser.n_pages,
                num_earnings=ns_parser.limit,
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="limit of articles being printed",
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
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-i")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            seeking_alpha_view.news(
                article_id=ns_parser.n_id,
                num=ns_parser.limit,
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="limit of stocks to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            shortinterest_view.low_float(
                num=ns_parser.limit,
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
        parser.add_argument(
            "-t",
            "--type",
            action="store",
            dest="s_type",
            choices=self.cnews_type_choices,
            default="Top-News",
            help="number of news to display",
        )
        parser.add_argument(
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="limit of news to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            seeking_alpha_view.display_news(
                news_type=ns_parser.s_type,
                num=ns_parser.limit,
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=5,
            help="limit of stocks to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")

        ns_parser = parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            shortinterest_view.hot_penny_stocks(
                num=ns_parser.limit,
                export=ns_parser.export,
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
            "-l",
            "--limit",
            action="store",
            dest="limit",
            type=check_positive,
            default=3,
            help="limit of days to display",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-l")
        ns_parser = parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED
        )
        if ns_parser:
            nasdaq_view.display_top_retail(
                n_days=ns_parser.limit, export=ns_parser.export
            )


def menu(queue: List[str] = None):
    """Discovery Menu"""
    disc_controller = DiscoveryController(queue)
    an_input = "HELP_ME"

    while True:
        # There is a command in the queue
        if disc_controller.queue and len(disc_controller.queue) > 0:
            # If the command is quitting the menu we want to return in here
            if disc_controller.queue[0] in ("q", "..", "quit"):
                print("")
                if len(disc_controller.queue) > 1:
                    return disc_controller.queue[1:]
                return []

            # Consume 1 element from the queue
            an_input = disc_controller.queue[0]
            disc_controller.queue = disc_controller.queue[1:]

            # Print the current location because this was an instruction and we want user to know what was the action
            if an_input and an_input.split(" ")[0] in disc_controller.CHOICES_COMMANDS:
                print(f"{get_flair()} /stocks/disc/ $ {an_input}")

        # Get input command from user
        else:
            # Display help menu when entering on this menu from a level above
            if an_input == "HELP_ME":
                disc_controller.print_help()

            # Get input from user using auto-completion
            if session and gtff.USE_PROMPT_TOOLKIT and disc_controller.completer:
                an_input = session.prompt(
                    f"{get_flair()} /stocks/disc/ $ ",
                    completer=disc_controller.completer,
                    search_ignore_case=True,
                )
            # Get input from user without auto-completion
            else:
                an_input = input(f"{get_flair()} /stocks/disc/ $ ")

        try:
            # Process the input command
            disc_controller.queue = disc_controller.switch(an_input)

        except SystemExit:
            print(
                f"\nThe command '{an_input}' doesn't exist on the /stocks/disc menu.",
                end="",
            )
            similar_cmd = difflib.get_close_matches(
                an_input.split(" ")[0] if " " in an_input else an_input,
                disc_controller.CHOICES,
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
                        disc_controller.queue = []
                        print("\n")
                        continue
                    an_input = candidate_input
                else:
                    an_input = similar_cmd[0]

                print(f" Replacing by '{an_input}'.")
                disc_controller.queue.insert(0, an_input)
            else:
                print("\n")
