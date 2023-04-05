"""Sources Controller Module"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
import argparse
import logging
from pathlib import Path
from typing import List, Optional

from openbb_terminal.core.session.constants import SOURCES_URL

# IMPORTATION THIRDPARTY
# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    get_current_user,
    is_local,
    set_sources,
)
from openbb_terminal.core.session.hub_model import upload_user_field
from openbb_terminal.core.session.sources_handler import write_sources
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import parse_and_split_input
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class SourcesController(BaseController):
    """Sources Controller class"""

    CHOICES_COMMANDS: List[str] = [
        "get",
        "set",
    ]
    PATH = "/sources/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            self.choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(self.choices)

    def parse_input(self, an_input: str) -> List:
        """Parse controller input

        Overrides the parent class function to handle github org/repo path convention.
        See `BaseController.parse_input()` for details.
        """
        cmd_filter = r"((set\ --cmd |set\ -c |get\ --cmd |get\ -c ).*?("
        for cmd in get_current_user().sources.sources_dict:
            cmd = cmd.replace("/", r"\/")
            cmd_filter += f"{cmd}|"
        cmd_filter += ")*)"
        commands = parse_and_split_input(an_input=an_input, custom_filters=[cmd_filter])
        return commands

    def print_help(self):
        """Print help"""
        mt = MenuText("sources/")
        mt.add_param(
            "_source",
            get_current_user().preferences.USER_DATA_SOURCES_FILE
            if is_local()
            else SOURCES_URL,
        )
        mt.add_raw("\n")
        mt.add_info("_info_")
        mt.add_cmd("get")
        mt.add_cmd("set")
        console.print(text=mt.menu_text, menu="Data Sources")

    @log_start_end(log=logger)
    def call_get(self, other_args):
        """Process get command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="get",
            description="Get sources associated with a command and the one selected by default.",
        )
        parser.add_argument(
            "-c",
            "--cmd",
            action="store",
            dest="cmd",
            choices=list(get_current_user().sources.sources_dict.keys()),
            required="-h" not in other_args,
            help="Command that we want to check the available data sources and the default one.",
            metavar="COMMAND",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            sources_dict = get_current_user().sources.sources_dict
            cmd_defaults = sources_dict.get(ns_parser.cmd, None)
            if cmd_defaults is None:
                console.print(f"[red]'{ns_parser.cmd}' is not a valid command.[/red]\n")
            elif len(cmd_defaults) == 0:
                console.print("This command has no data sources available.\n")
            else:
                console.print(
                    f"[param]Default   :[/param] {cmd_defaults[0]}\n"
                    f"[param]Available :[/param] {', '.join(cmd_defaults)}"
                )

    @log_start_end(log=logger)
    def call_set(self, other_args):
        """Process set command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="set",
            description="Set a default data sources associated with a command, using 'set <command> <source>'.",
        )
        parser.add_argument(
            "-c",
            "--cmd",
            action="store",
            dest="cmd",
            choices=list(get_current_user().sources.sources_dict.keys()),
            required="-h" not in other_args and "--help" not in other_args,
            help="Command that we to select the default data source.",
            metavar="COMMAND",
        )
        parser.add_argument(
            "-s",
            "--source",
            action="store",
            dest="source",
            type=str,
            required="-h" not in other_args and "--help" not in other_args,
            help="Data source to use by default on specified command.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            sources_dict = get_current_user().sources.sources_dict
            if ns_parser.source in sources_dict[ns_parser.cmd]:
                sources_dict[ns_parser.cmd].remove(ns_parser.source)
                sources_dict[ns_parser.cmd].insert(0, ns_parser.source)
                set_sources(sources_dict)

                if is_local():
                    write_sources(
                        sources=sources_dict,
                        path=Path(
                            get_current_user().preferences.USER_DATA_SOURCES_FILE
                        ),
                    )
                else:
                    upload_user_field(
                        key="features_sources",
                        value=sources_dict,
                        auth_header=get_current_user().profile.get_auth_header(),
                    )
                    console.print("")
                console.print(
                    f"Default data source for '{ns_parser.cmd}' set to "
                    f"'{ns_parser.source}'.\n"
                )
            else:
                console.print(
                    f"[red]'{ns_parser.source}' is not a valid data source for "
                    f"'{ns_parser.cmd}' command.[/red]\n"
                    f"[param]\nAvailable :[/param] {', '.join(sources_dict[ns_parser.cmd])}\n"
                )
