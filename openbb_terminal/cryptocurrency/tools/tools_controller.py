"""Tools Controller Module"""
__docformat__ = "numpy"

# pylint: disable=C0302

import argparse
import logging
from typing import List, Optional

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.cryptocurrency.tools import tools_view
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    check_non_negative,
    check_positive,
    check_positive_float,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class ToolsController(BaseController):
    """Tools Controller class"""

    CHOICES_COMMANDS = ["aprtoapy", "il"]

    PATH = "/crypto/tools/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

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
            "-a",
            "--priceChangeA",
            dest="priceChangeA",
            type=check_non_negative,
            help="Token A price change in percentage",
            default=0,
            choices=range(1, 101),
            metavar="PRICECHANGEA",
        )
        parser.add_argument(
            "-b",
            "--priceChangeB",
            dest="priceChangeB",
            type=check_non_negative,
            help="Token B price change in percentage",
            default=100,
            choices=range(1, 101),
            metavar="PRICECHANGEB",
        )
        parser.add_argument(
            "-p",
            "--proportion",
            dest="proportion",
            type=check_positive,
            help="""Pool proportion. E.g., 50 means that pool contains 50%% of token A and 50%% of token B,
            30 means that pool contains 30%% of token A and 70%% of token B""",
            default=50,
            choices=range(1, 101),
            metavar="PROPORTION",
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
        if other_args and other_args[0][0] != "-":
            other_args.insert(0, "-a")

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
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
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
            type=check_positive,
            help="APR value in percentage to convert",
            default=100,
            choices=range(1, 101),
            metavar="APR",
        )
        parser.add_argument(
            "-c",
            "--compounding",
            dest="compounding",
            type=check_positive,
            help="Number of compounded periods in a year. 12 means compounding monthly",
            default=12,
            choices=range(1, 101),
            metavar="COMPOUNDING",
        )
        parser.add_argument(
            "-n",
            "--narrative",
            dest="narrative",
            action="store_true",
            help="Flag to show narrative instead of dataframe",
            default=False,
        )

        if other_args and other_args[0][0] != "-":
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
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
