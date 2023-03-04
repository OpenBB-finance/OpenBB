"""OS Controller Module"""
__docformat__ = "numpy"

import argparse
import logging
from typing import List, Optional

from openbb_terminal.alternative.oss import github_view, runa_model, runa_view
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_RAW_DATA_ALLOWED,
    parse_and_split_input,
    valid_repo,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class OSSController(BaseController):
    """Open Source Controller class"""

    CHOICES_COMMANDS = ["sh", "tr", "rs", "rossidx"]
    PATH = "/alternative/oss/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default

            self.completer = NestedCompleter.from_nested_dict(choices)

    def parse_input(self, an_input: str) -> List:
        """Parse controller input

        Overrides the parent class function to handle github org/repo path convention.
        See `BaseController.parse_input()` for details.
        """
        # Covering the github "org/repo" convention in rs and sh commands
        custom_filters = [
            r"(sh .*?(\/[a-zA-Z0-9_\-\/]).*?((?=\/)|(?= )|(?=$)))",
            r"(rs .*?(\/[a-zA-Z0-9_\-\/]).*?((?=\/)|(?= )|(?=$)))",
        ]
        commands = parse_and_split_input(
            an_input=an_input, custom_filters=custom_filters
        )
        return commands

    def print_help(self):
        """Print help"""
        mt = MenuText("alternative/oss/", 80)
        mt.add_cmd("rossidx")
        mt.add_cmd("rs")
        mt.add_cmd("sh")
        mt.add_cmd("tr")
        console.print(text=mt.menu_text, menu="Alternative - Open Source")

    @log_start_end(log=logger)
    def call_sh(self, other_args: List[str]):
        """Process sh command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="sh",
            description="Display a repo star history [Source: https://api.github.com]",
        )
        parser.add_argument(
            "-r",
            "--repo",
            type=str,
            required="-h" not in other_args,
            dest="repo",
            help="Repository to search for star history. Format: org/repo, e.g., openbb-finance/openbbterminal",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-r")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
        )
        if ns_parser and valid_repo(ns_parser.repo):
            github_view.display_star_history(
                repo=ns_parser.repo, export=ns_parser.export
            )

    @log_start_end(log=logger)
    def call_rs(self, other_args: List[str]):
        """Process rs command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rs",
            description="Display a repo summary [Source: https://api.github.com]",
        )
        parser.add_argument(
            "-r",
            "--repo",
            type=str,
            required="-h" not in other_args,
            dest="repo",
            help="Repository to search for repo summary. Format: org/repo, e.g., openbb-finance/openbbterminal",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-r")
        ns_parser = self.parse_known_args_and_warn(
            parser, other_args, export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED, raw=True
        )
        if ns_parser and valid_repo(ns_parser.repo):
            github_view.display_repo_summary(
                repo=ns_parser.repo,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_rossidx(self, other_args: List[str]):
        """Process rossidx command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="rossidx",
            description="""
            Display list of startups from ross index [Source: https://runacap.com/]
            Use --chart to display chart and -t {stars,forks} to set chart type
            """,
        )
        parser.add_argument(
            "-s",
            "--sortby",
            type=str,
            dest="sortby",
            nargs="+",
            help="Sort startups by column",
            default="Stars AGR [%]",
            choices=runa_model.SORT_COLUMNS,
            metavar="SORTBY",
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
            "-c",
            "--chart",
            action="store_true",
            help="Flag to show chart",
            dest="show_chart",
            default=False,
        )
        parser.add_argument(
            "-g",
            "--growth",
            action="store_true",
            help="Flag to show growth chart",
            dest="show_growth",
            default=False,
        )
        parser.add_argument(
            "-t",
            "--chart-type",
            type=str,
            dest="chart_type",
            help="Chart type: {stars, forks}",
            default="stars",
            choices=["stars", "forks"],
        )
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_ONLY_RAW_DATA_ALLOWED,
            limit=10,
        )

        if ns_parser:
            runa_view.display_rossindex(
                sortby=" ".join(ns_parser.sortby),
                ascend=ns_parser.reverse,
                limit=ns_parser.limit,
                show_chart=ns_parser.show_chart,
                show_growth=ns_parser.show_growth,
                chart_type=ns_parser.chart_type,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )

    @log_start_end(log=logger)
    def call_tr(self, other_args: List[str]):
        """Process tr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="tr",
            description="Display top repositories [Source: https://api.github.com]",
        )
        parser.add_argument(
            "-s",
            "--sortby",
            type=str,
            dest="sortby",
            help="Sort repos by {stars, forks}. Default: stars",
            default="stars",
            choices=["stars", "forks"],
        )

        parser.add_argument(
            "-c",
            "--categories",
            type=str,
            dest="categories",
            help="Filter by repo categories. If more than one separate with a comma: e.g., finance,investment",
            default="",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = self.parse_known_args_and_warn(
            parser,
            other_args,
            export_allowed=EXPORT_BOTH_RAW_DATA_AND_FIGURES,
            raw=True,
            limit=10,
        )
        if ns_parser:
            github_view.display_top_repos(
                sortby=ns_parser.sortby,
                categories=ns_parser.categories,
                limit=ns_parser.limit,
                export=ns_parser.export,
                sheet_name=" ".join(ns_parser.sheet_name)
                if ns_parser.sheet_name
                else None,
            )
