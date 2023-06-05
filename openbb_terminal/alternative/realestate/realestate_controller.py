"""Trading Hours Controller."""
__docformat__ = "numpy"

import argparse
import logging
from datetime import datetime, timedelta
from typing import List, Optional

from openbb_terminal.alternative.realestate import landRegistry_view
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import EXPORT_ONLY_RAW_DATA_ALLOWED, check_positive
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


def get_relative_date(months: int):
    date = datetime.now() - timedelta(days=365 / 12 * months)
    return date.strftime("%Y-%m-%d")


def start_date():
    return get_relative_date(13)


def end_date():
    return get_relative_date(1)


class RealEstateController(BaseController):

    """Real Estate Controller class."""

    CHOICES_COMMANDS = ["sales", "townsales", "regionstats"]
    PATH = "/alternative/realestate/"
    CHOICES_GENERATION = True
    # FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")

    def __init__(self, queue: Optional[List[str]] = None):
        """Construct Data."""
        super().__init__(queue)

        self.enddate = None
        self.startdate = None
        self.town = None
        self.postcode = None
        self.region = None
        self.limit = 25

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        mt = MenuText("alternative/realestate/")
        mt.add_cmd("sales")
        mt.add_cmd("townsales")
        mt.add_cmd("regionstats")

        console.print(text=mt.menu_text, menu="UK Real Estate Sales Data")

    @log_start_end(log=logger)
    def call_sales(self, other_args: List[str]):
        """Process 'postcode' command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sales",
            description="Select the postcode you want to see sold house price data for. [Source: UK Land Registry]",
        )
        parser.add_argument(
            "-p",
            "--postcode",
            help="Postcode",
            type=str.upper,
            required="-h" not in other_args,
            dest="postcode",
            metavar="postcode",
        )

        parser.add_argument(
            "-l",
            "--limit",
            help="Number of entries to return",
            type=check_positive,
            required=False,
            dest="limit",
            metavar="limit",
            default=25,
        )

        if (
            other_args
            and "-p" not in other_args[0]
            and "--postcode" not in other_args[0]
            and "-h" not in other_args
        ):
            other_args.insert(0, "-p")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if ns_parser.postcode:
                landRegistry_view.display_estate_sales(
                    ns_parser.postcode, ns_parser.limit, export=ns_parser.export
                )
            else:
                console.print("[red]Select valid postcode[/red]\n")

    @log_start_end(log=logger)
    def call_townsales(self, other_args: List[str]):
        """Process 'townsales' command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="townsales",
            description="""Select the town and date range you want to see sold house price data for.
            [Source: UK Land Registry]""",
        )

        parser.add_argument(
            "-t",
            "--town",
            help="Town that we want sales information for",
            type=str.upper,
            required="-h" not in other_args,
            dest="town",
            metavar="town",
        )

        parser.add_argument(
            "-s",
            "--startdate",
            help="Start date that we want sales information for",
            type=str,
            required=False,
            dest="startdate",
            metavar="startdate",
            default=start_date(),
        )

        parser.add_argument(
            "-e",
            "--enddate",
            help="End date that we want sales information for",
            type=str,
            required=False,
            dest="enddate",
            metavar="enddate",
            default=end_date(),
        )

        parser.add_argument(
            "-l",
            "--limit",
            help="Number of entries to return",
            type=check_positive,
            required=False,
            dest="limit",
            metavar="limit",
            default=25,
        )

        if (
            other_args
            and "-t" not in other_args[0]
            and "--town" not in other_args[0]
            and "-h" not in other_args
        ):
            other_args.insert(0, "-t")

        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            EXPORT_ONLY_RAW_DATA_ALLOWED,
        )

        if ns_parser:
            if ns_parser.town and ns_parser.startdate and ns_parser.enddate:
                landRegistry_view.display_towns_sold_prices(
                    ns_parser.town,
                    ns_parser.startdate,
                    ns_parser.enddate,
                    ns_parser.limit,
                    ns_parser.export,
                )
            else:
                console.print(
                    "[red]Select the town you want to know about and a valid date range.[/red]\n"
                )

    @log_start_end(log=logger)
    def call_regionstats(self, other_args: List[str]):
        """Process 'regionstats' command."""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="regionstats",
            description="Select the region and date range you want see stats for. [Source: UK Land Registry]",
        )

        parser.add_argument(
            "-r",
            "--region",
            help="Region that we want stats for",
            type=str.lower,
            required="-h" not in other_args,
            dest="region",
            metavar="region",
        )

        parser.add_argument(
            "-s",
            "--startdate",
            help="Start date that we want sales information for",
            type=str,
            required=False,
            dest="startdate",
            metavar="startdate",
            default=start_date(),
        )

        parser.add_argument(
            "-e",
            "--enddate",
            help="End date that we want sales information for",
            type=str,
            required=False,
            dest="enddate",
            metavar="enddate",
            default=end_date(),
        )

        if (
            other_args
            and "-r" not in other_args[0]
            and "--region" not in other_args[0]
            and "-h" not in other_args
        ):
            other_args.insert(0, "-r")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if ns_parser.region and ns_parser.startdate and ns_parser.enddate:
                landRegistry_view.display_region_stats(
                    ns_parser.region,
                    ns_parser.startdate,
                    ns_parser.enddate,
                    ns_parser.export,
                )
            else:
                console.print(
                    "[red]Select the region you want to know about and a valid date range.[/red]\n"
                )
