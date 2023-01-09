"""Trading Hours Controller."""
__docformat__ = "numpy"

import argparse
import logging

from typing import List

from openbb_terminal.custom_prompt_toolkit import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
)
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.alternative.realestate import landRegistry_view

logger = logging.getLogger(__name__)


class RealEstateController(BaseController):

    """Real Estate Controller class."""

    CHOICES_COMMANDS = ["sales", "townsales", "regionstats"]
    PATH = "/alternative/realestate/"
    CHOICES_GENERATION = True
    # FILE_PATH = os.path.join(os.path.dirname(__file__), "README.md")

    def __init__(self, queue: List[str] = None):
        """Construct Data."""
        super().__init__(queue)

        self.enddate = None
        self.startdate = None
        self.town = None
        self.postcode = None
        self.region = None

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):

        mt = MenuText("alternative/realestate/")
        mt.add_cmd("sales")
        mt.add_raw("\n")
        mt.add_param("_postcode", self.postcode or "")
        mt.add_raw("\n")
        mt.add_cmd("townsales")
        mt.add_raw("\n")
        mt.add_param("_town", self.town or "")
        mt.add_param("_startdate <YYYY-MM-DD>", self.startdate or "")
        mt.add_param("_enddate <YYYY-MM-DD>", self.enddate or "")
        mt.add_raw("\n")
        mt.add_cmd("regionstats")
        mt.add_raw("\n")
        mt.add_param("_region", self.region or "")
        mt.add_param("_startdate <YYYY-MM-DD>", self.startdate or "")
        mt.add_param("_enddate <YYYY-MM-DD>", self.enddate or "")

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
                    ns_parser.postcode, export=ns_parser.export
                )
            else:
                console.print("[red]Select valid postcode[/red]\n")
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
            required=True,
            dest="startdate",
            metavar="startdate",
        )

        parser.add_argument(
            "-e",
            "--enddate",
            help="End date that we want sales information for",
            type=str,
            required=True,
            dest="enddate",
            metavar="enddate",
        )

        if (
            other_args
            and "-t" not in other_args[0]
            and "--town" not in other_args[0]
            and "-h" not in other_args
        ):
            other_args.insert(0, "-t")

        if (
            other_args
            and len(other_args) > 2
            and "-s" not in other_args[2]
            and "--startdate" not in other_args[2]
            and "-h" not in other_args
        ):
            other_args.insert(2, "-s")

        if (
            other_args
            and len(other_args) > 4
            and "-e" not in other_args[4]
            and "--enddate" not in other_args[4]
            and "-h" not in other_args
        ):
            other_args.insert(4, "-e")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            if ns_parser.town and ns_parser.startdate and ns_parser.enddate:
                landRegistry_view.display_towns_sold_prices(
                    ns_parser.town,
                    ns_parser.startdate,
                    ns_parser.enddate,
                    ns_parser.export,
                )
            else:
                console.print(
                    "[red]Select the town you want to know about and a valid date range.[/red]\n"
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
            required=True,
            dest="startdate",
            metavar="startdate",
        )

        parser.add_argument(
            "-e",
            "--enddate",
            help="End date that we want sales information for",
            type=str,
            required=True,
            dest="enddate",
            metavar="enddate",
        )

        if (
            other_args
            and "-r" not in other_args[0]
            and "--region" not in other_args[0]
            and "-h" not in other_args
        ):
            other_args.insert(0, "-r")

        if (
            other_args
            and len(other_args) > 2
            and "-s" not in other_args[2]
            and "--startdate" not in other_args[2]
            and "-h" not in other_args
        ):
            other_args.insert(2, "-s")

        if (
            other_args
            and len(other_args) > 4
            and "-e" not in other_args[4]
            and "--enddate" not in other_args[4]
            and "-h" not in other_args
        ):
            other_args.insert(4, "-e")

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
        else:
            console.print(
                "[red]Select the region you want to know about and a valid date range.[/red]\n"
            )
