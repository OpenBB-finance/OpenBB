"""Sources Controller Module"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
import argparse
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from openbb_terminal.core.session.constants import SOURCES_URL

# IMPORTATION THIRDPARTY
# IMPORTATION INTERNAL
from openbb_terminal.core.session.current_user import (
    get_current_user,
    is_local,
    set_sources,
)
from openbb_terminal.core.session.hub_model import upload_config
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

# pylint: disable=too-many-lines,no-member,too-many-public-methods,C0302
# pylint:disable=import-outside-toplevel

logger = logging.getLogger(__name__)


def unique(sequence):
    seen = set()
    return [x for x in sequence if not (x in seen or seen.add(x))]


# TODO: This menu needs to be refactored


class SourcesController(BaseController):
    """Sources Controller class"""

    CHOICES_COMMANDS: List[str] = [
        "get",
        "set",
    ]
    PATH = "/sources/"

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        self.commands_with_sources: Dict[str, List[str]] = {}
        self.json_doc: dict = {}
        self.update_json_doc()

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["get"] = {c: None for c in list(self.commands_with_sources.keys())}
            choices["set"] = {c: None for c in list(self.commands_with_sources.keys())}
            for cmd in list(self.commands_with_sources.keys()):
                choices["set"][cmd] = {c: None for c in self.commands_with_sources[cmd]}

            self.completer = NestedCompleter.from_nested_dict(choices)

    def update_json_doc(self):
        """Update the json doc. If local, read from file."""
        if is_local():
            try:
                sources_path = Path(
                    get_current_user().preferences.PREFERRED_DATA_SOURCE_FILE
                )
                with open(sources_path) as file:
                    sources_dict = json.load(file)
            except Exception as e:
                msg = (
                    f"Failed to read sources file {sources_path}, set a valid file"
                    " to use this menu."
                )
                raise Exception(msg) from e

            set_sources(sources_dict)
        self.json_doc = get_current_user().sources.sources_dict
        self.generate_commands_with_sources()

    def generate_commands_with_sources(self):
        """Generate choices"""
        for context in self.json_doc:
            for menu in self.json_doc[context]:
                if isinstance(self.json_doc[context][menu], Dict):
                    for submenu in self.json_doc[context][menu]:
                        if isinstance(self.json_doc[context][menu][submenu], Dict):
                            for subsubmenu in self.json_doc[context][menu][submenu]:
                                self.commands_with_sources[
                                    f"{context}_{menu}_{submenu}_{subsubmenu}"
                                ] = self.json_doc[context][menu][submenu][subsubmenu]
                        else:
                            self.commands_with_sources[
                                f"{context}_{menu}_{submenu}"
                            ] = self.json_doc[context][menu][submenu]
                else:
                    self.commands_with_sources[f"{context}_{menu}"] = self.json_doc[
                        context
                    ][menu]

    def print_help(self):
        """Print help"""
        mt = MenuText("sources/")
        mt.add_param(
            "_source",
            get_current_user().preferences.PREFERRED_DATA_SOURCE_FILE
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
            description="Get sources associated with a command and the one selected by default, using 'get <command>'.",
        )
        parser.add_argument(
            "-c",
            "--cmd",
            action="store",
            dest="cmd",
            choices=list(self.commands_with_sources.keys()),
            required="-h" not in other_args,
            help="Command that we want to check the available data sources and the default one.",
            metavar="COMMAND",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.update_json_doc()
            try:
                the_item = self.commands_with_sources[ns_parser.cmd]
            except KeyError:
                console.print(
                    [f"[red]'{ns_parser.cmd}' is not a valid command.[/red]\n"]
                )
                return
            if the_item:
                console.print(
                    f"\n[param]Default   :[/param] {self.commands_with_sources[ns_parser.cmd][0]}"
                )
                console.print(
                    f"[param]Available :[/param] {', '.join(self.commands_with_sources[ns_parser.cmd])}\n"
                )
            else:
                console.print("This command has no data sources available.\n")

    # pylint: disable=R0912
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
            choices=list(self.commands_with_sources.keys()),
            help="Command that we to select the default data source.",
            metavar="COMMAND",
        )
        parser.add_argument(
            "-s",
            "--source",
            action="store",
            dest="source",
            type=str,
            help="Data source to use by default on specified command.",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-c")
            if "-s" not in other_args and "--source" not in other_args:
                other_args.insert(2, "-s")
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            self.update_json_doc()

            success, valid_sources = self.update_dict_and_valid_sources(ns_parser)

            if success:
                set_sources(self.json_doc)
                if is_local():
                    try:
                        self.write_json()
                        self.update_dictionary()
                        console.print(
                            "[green]The data source was specified successfully.\n[/green]"
                        )
                    except Exception as e:
                        console.print(
                            f"[red]Failed to write preferred data sources to file: "
                            f"{get_current_user().preferences.PREFERRED_DATA_SOURCE_FILE}[/red]"
                        )
                        console.print(f"[red]{e}[/red]")
                else:
                    key = str(ns_parser.cmd).replace("_", "/")
                    valid = self.commands_with_sources[ns_parser.cmd]
                    valid.remove(ns_parser.source)
                    valid.insert(0, ns_parser.source)
                    value = ", ".join(valid)
                    upload_config(
                        key=key,
                        value=value,
                        type_="sources",
                        auth_header=get_current_user().profile.get_auth_header(),
                    )
            else:
                console.print(
                    f"[red]The data source selected is not valid, select one from: {', '.join(valid_sources)}.\n[/red]"
                )

    def update_dict_and_valid_sources(self, ns_parser):
        """Update dictionary and valid sources"""
        menus = ns_parser.cmd.split("_")
        num_menus = len(menus)
        valid_sources = list()
        success = True

        # TODO: Change this to be recursive and handle any number of menus

        # Update dictionary
        if num_menus == 1:
            if ns_parser.source not in self.json_doc[menus[0]]:
                success = False
                valid_sources = self.json_doc[menus[0]]
            else:
                self.json_doc[menus[0]] = unique(
                    [ns_parser.source] + self.json_doc[menus[0]]
                )
        elif num_menus == 2:
            if ns_parser.source not in self.json_doc[menus[0]][menus[1]]:
                success = False
                valid_sources = self.json_doc[menus[0]][menus[1]]
            else:
                self.json_doc[menus[0]][menus[1]] = unique(
                    [ns_parser.source] + self.json_doc[menus[0]][menus[1]]
                )
        elif num_menus == 3:
            if ns_parser.source not in self.json_doc[menus[0]][menus[1]][menus[2]]:
                success = False
                valid_sources = self.json_doc[menus[0]][menus[1]][menus[2]]
            else:
                self.json_doc[menus[0]][menus[1]][menus[2]] = unique(
                    [ns_parser.source] + self.json_doc[menus[0]][menus[1]][menus[2]]
                )
        elif num_menus == 4:
            if (
                ns_parser.source
                not in self.json_doc[menus[0]][menus[1]][menus[2]][menus[3]]
            ):
                success = False
                valid_sources = self.json_doc[menus[0]][menus[1]][menus[2]][menus[3]]
            else:
                self.json_doc[menus[0]][menus[1]][menus[2]][menus[3]] = unique(
                    [ns_parser.source]
                    + self.json_doc[menus[0]][menus[1]][menus[2]][menus[3]]
                )

        return success, valid_sources

    def write_json(self):
        """Write json to file"""
        with open(
            get_current_user().preferences.PREFERRED_DATA_SOURCE_FILE,
            "w",
        ) as f:
            json.dump(self.json_doc, f, indent=4)

    def update_dictionary(self):
        """Update dictionary with new data sources"""
        for context in self.json_doc:
            for menu in self.json_doc[context]:
                if isinstance(self.json_doc[context][menu], Dict):
                    for submenu in self.json_doc[context][menu]:
                        if isinstance(self.json_doc[context][menu][submenu], Dict):
                            for subsubmenu in self.json_doc[context][menu][submenu]:
                                self.commands_with_sources[
                                    f"{context}_{menu}_{submenu}_{subsubmenu}"
                                ] = self.json_doc[context][menu][submenu][subsubmenu]
                        else:
                            self.commands_with_sources[
                                f"{context}_{menu}_{submenu}"
                            ] = self.json_doc[context][menu][submenu]
                else:
                    self.commands_with_sources[f"{context}_{menu}"] = self.json_doc[
                        context
                    ][menu]
