""" Disc Controller """
__docformat__ = "numpy"

import argparse
import os
from typing import List
from datetime import datetime
from matplotlib import pyplot as plt
from prompt_toolkit.completion import NestedCompleter
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.helper_funcs import get_flair
from gamestonk_terminal.menu import session
from gamestonk_terminal.helper_funcs import (
    parse_known_args_and_warn,
    check_non_negative,
    check_positive,
    valid_date,
    check_int_range,
)
from gamestonk_terminal.stocks.discovery import (
    ark_view,
    fidelity_view,
    seeking_alpha_view,
    shortinterest_view,
    yahoofinance_view,
    finnhub_view,
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
        "ford",
        "arkord",
        "upcoming",
        "latest",
        "trending",
        "lowfloat",
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
        help_text = """https://github.com/GamestonkTerminal/GamestonkTerminal/tree/main/gamestonk_terminal/stocks/discovery

Discovery:
    cls            clear screen")
    ?/help         show this menu again")
    q              quit this menu, and shows back to main menu")
    quit           quit to abandon program")
Finnhub:
    pipo           past IPOs dates
    fipo           future IPOs dates
Yahoo Finance:
    gainers        show latest top gainers
    losers         show latest top losers
Fidelity:
    ford           orders by Fidelity Customers
cathiesark.com:
    arkord         orders by ARK Investment Management LLC
Seeking Alpha:
    upcoming       upcoming earnings release dates
    latest         latest news
    trending       trending news
shortinterest.com
    lowfloat       show low float stocks under 10M shares float
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
            os.system("cls||clear")
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
        try:
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

        except Exception as e:
            print(e, "\n")

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
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-n")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            finnhub_view.future_ipo(
                num_days_ahead=ns_parser.num,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

    def call_gainers(self, other_args: List[str]):
        """Process gainers command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="gainers",
            description="Print up to 25 top ticker gainers. [Source: Yahoo Finance]",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_int_range(1, 25),
            default=5,
            help="Number of the top gainers stocks to retrieve.",
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

        except Exception as e:
            print(e, "\n")

    def call_losers(self, other_args: List[str]):
        """Process losers command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="losers",
            description="Print up to 25 top ticker losers. [Source: Yahoo Finance]",
        )
        parser.add_argument(
            "-n",
            "--num",
            action="store",
            dest="num",
            type=check_int_range(1, 25),
            default=5,
            help="Number of the top losers stocks to retrieve.",
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

        except Exception as e:
            print(e, "\n")

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
        try:
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

        except Exception as e:
            print(e, "\n")

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
            "--export",
            choices=["csv", "json", "xlsx"],
            default="",
            type=str,
            dest="export",
            help="Export dataframe data to csv,json,xlsx file",
        )
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-n")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            ark_view.ark_orders_view(
                num=ns_parser.n_num,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

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
        try:
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

        except Exception as e:
            print(e, "\n")

    def call_latest(self, other_args: List[str]):
        """Process latest command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="latest",
            description="""Latest news articles. [Source: Seeking Alpha]""",
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
        try:
            if other_args:
                if "-" not in other_args[0]:
                    other_args.insert(0, "-i")

            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            seeking_alpha_view.news(
                news_type="latest",
                article_id=ns_parser.n_id,
                num=ns_parser.n_num,
                start_date=ns_parser.s_date,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")

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
        try:
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

        except Exception as e:
            print(e, "\n")

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
        try:
            ns_parser = parse_known_args_and_warn(parser, other_args)
            if not ns_parser:
                return

            shortinterest_view.low_float(
                num=ns_parser.n_num,
                export=ns_parser.export,
            )

        except Exception as e:
            print(e, "\n")


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
            continue
