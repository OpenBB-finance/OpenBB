"""Tools Controller Module"""
__docformat__ = "numpy"

# pylint: disable=C0302

import argparse
import logging
from typing import List

from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_non_negative_float,
    check_percentage_range,
    check_positive,
    check_positive_float,
)
from openbb_terminal.cryptocurrency.tools import tools_view
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText

logger = logging.getLogger(__name__)


class ToolsController(BaseController):
    """Tools Controller class"""

    CHOICES_COMMANDS = ["aprtoapy", "il"]

    PATH = "/crypto/tools/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}

            choices["support"] = self.SUPPORT_CHOICES
            choices["about"] = self.ABOUT_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("crypto/tools/")
        mt.add_cmd("aprtoapy")
        mt.add_cmd("il")
        console.print(text=mt.menu_text, menu="Cryptocurrency - Tools")

    @log_start_end(log=logger)
    def call_il(self, other_args: List[str]):
        """Process il command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="il",
            description="""Tool to calculate Impermanent Loss in a custom liquidity pool.
            Users can provide percentages increases for two tokens (and their weight in the liquidity pool)
            and verify the impermanent loss that can occur.""",
        )

        parser.add_argument(
            "-pcA",
            "--priceChangeA",
            dest="priceChangeA",
            type=check_non_negative_float,
            help="Token A price change in percentage",
            default=0,
        )

        parser.add_argument(
            "-pcB",
            "--priceChangeB",
            dest="priceChangeB",
            type=check_non_negative_float,
            help="Token B price change in percentage",
            default=100,
        )
        parser.add_argument(
            "-p",
            "--proportion",
            dest="proportion",
            type=check_percentage_range,
            help="""Pool proportion. E.g., 50 means that pool contains 50%% of token A and 50%% of token B,
            30 means that pool contains 30%% of token A and 70%% of token B""",
            default=50,
        )

        parser.add_argument(
            "-v",
            "--value",
            dest="value",
            type=check_positive_float,
            help="Initial amount of dollars that user provides to liquidity pool",
            default=1000,
        )

        parser.add_argument(
            "-n",
            "--narrative",
            dest="narrative",
            action="store_true",
            help="Flag to show narrative instead of dataframe",
            default=False,
        )

        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "-pcA")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            tools_view.display_il(
                price_changeA=ns_parser.priceChangeA,
                price_changeB=ns_parser.priceChangeB,
                proportion=ns_parser.proportion,
                initial_pool_value=ns_parser.value,
                narrative=ns_parser.narrative,
                export=ns_parser.export,
            )

    @log_start_end(log=logger)
    def call_aprtoapy(self, other_args: List[str]):
        """Process aprtoapy command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="aprtoapy",
            description="""
                      Tool to calculate APY from APR value.
                      Compouding periods, i.e., the number of times compounded per year
                      can be defined with -c argument.
                  """,
        )

        parser.add_argument(
            "--apr",
            dest="apr",
            type=check_positive_float,
            help="APR value in percentage to convert",
            default=100,
        )

        parser.add_argument(
            "-c",
            "--compounding",
            dest="compounding",
            type=check_positive,
            help="Number of compounded periods in a year. 12 means compounding monthly",
            default=12,
        )
        parser.add_argument(
            "-n",
            "--narrative",
            dest="narrative",
            action="store_true",
            help="Flag to show narrative instead of dataframe",
            default=False,
        )

        if other_args and not other_args[0][0] == "-":
            other_args.insert(0, "--apr")

        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, EXPORT_ONLY_RAW_DATA_ALLOWED
        )

        if ns_parser:
            tools_view.display_apy(
                apr=ns_parser.apr,
                compounding_times=ns_parser.compounding,
                narrative=ns_parser.narrative,
                export=ns_parser.export,
            )
