import argparse
import logging
from typing import List, Dict
from pathlib import Path

from prompt_toolkit.completion import NestedCompleter
from openbb_terminal.featflags_controller import FeatureFlagsController
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.decorators import log_start_end
from openbb_terminal.core.config.paths import USER_ROUTINES_DIRECTORY
from openbb_terminal import feature_flags as obbff
from openbb_terminal.menu import session

# from openbb_terminal.session.user import User

# from openbb_terminal.session import hub_model as Hub
# from openbb_terminal.session import local_model as Local

logger = logging.getLogger(__name__)


class AccountController(BaseController):
    """Account Controller Class"""

    CHOICES_COMMANDS = [
        "sync",
        "pull",
        "defaults",
        # "upload",
        # "download",
    ]

    PATH = "/account/"

    def __init__(self, queue: List[str] = None):
        super().__init__(queue)
        self.ROUTINE_FILES: Dict[str, Path] = {}
        self.ROUTINE_CHOICES: Dict[str, None] = {}
        self.update_runtime_choices()

    def update_runtime_choices(self):
        """Update runtime choices"""
        self.ROUTINE_FILES = {
            filepath.name: filepath
            for filepath in USER_ROUTINES_DIRECTORY.rglob("*.openbb")
        }
        self.ROUTINE_CHOICES = {filename: None for filename in self.ROUTINE_FILES}
        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["sync"] = {"--on": {}, "--off": {}}
            # choices["upload"]["--file"] = self.ROUTINE_CHOICES
            # choices["upload"]["-f"] = choices["upload"]["--file"]

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""

        mt = MenuText("account/", 100)
        mt.add_info("_info_")
        mt.add_cmd("sync")
        mt.add_cmd("pull")
        mt.add_cmd("defaults")
        # mt.add_info("_routines_")
        # mt.add_cmd("upload")
        # mt.add_cmd("download")
        console.print(text=mt.menu_text, menu="Account")

    @log_start_end(log=logger)
    def call_sync(self, other_args: List[str]):
        """Sync"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load your portfolio transactions.",
        )
        parser.add_argument(
            "--on",
            dest="on",
            help="Turn on sync",
            action="store_true",
            default=False,
        )
        parser.add_argument(
            "--off",
            dest="off",
            help="Turn on sync",
            action="store_true",
            default=False,
        )
        ns_parser = self.parse_simple_args(parser, other_args)
        if ns_parser:
            if ns_parser.on:
                if not obbff.SYNC_ENABLED:
                    FeatureFlagsController.set_feature_flag(
                        "OPENBB_SYNC_ENABLED", True, force=True
                    )
            elif ns_parser.off:
                FeatureFlagsController.set_feature_flag(
                    "OPENBB_SYNC_ENABLED", False, force=True
                )

            if obbff.SYNC_ENABLED:
                sync = "ON"
            else:
                sync = "OFF"
            console.print(f"[info]sync:[/info] {sync}")

    def call_pull(self, _):
        """Pull data"""
        console.print("Pull, Diff and Merge.")
        pass

    def call_defaults(self, _):
        """Reset to defaults"""
        console.print("No implemented yet.")
        pass

    # @log_start_end(log=logger)
    # def call_upload(self, other_args: List[str]):
    #     """Upload"""
    #     parser = argparse.ArgumentParser(
    #         add_help=False,
    #         formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    #         prog="load",
    #         description="Load your portfolio transactions.",
    #     )
    #     parser.add_argument(
    #         "-f",
    #         "--file",
    #         type=str,
    #         dest="file",
    #         required="-h" not in other_args,
    #         help="The file to be loaded",
    #         choices={c: {} for c in self.ROUTINE_FILES},
    #         metavar="FILE",
    #     )
    #     parser.add_argument(
    #         "-n",
    #         "--name",
    #         type=str,
    #         dest="name",
    #         required="-h" not in other_args,
    #         help="The name of the routine",
    #     )
    #     if other_args and "-" not in other_args[0][0]:
    #         other_args.insert(0, "-f")
    #     ns_parser = self.parse_known_args_and_warn(parser, other_args)
    #     if ns_parser:
    #         routine = Local.get_routine(ns_parser.file)
    #         if routine:
    #             Hub.upload_routine(ns_parser.name, routine)

    # @log_start_end(log=logger)
    # def call_download(self, _):
    #     """Download"""
    #     Hub.download_routine()
