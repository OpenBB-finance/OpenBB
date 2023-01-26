import logging
from typing import List, Dict
from pathlib import Path

from prompt_toolkit.completion import NestedCompleter
from openbb_terminal.featflags_controller import FeatureFlagsController

from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText
from openbb_terminal.decorators import log_start_end
from openbb_terminal.core.config.paths import (
    USER_ROUTINES_DIRECTORY,
)
from openbb_terminal import feature_flags as obbff
from openbb_terminal.menu import session
from openbb_terminal.session.user import User

logger = logging.getLogger(__name__)


class AccountController(BaseController):
    """Account Controller Class"""

    CHOICES_COMMANDS = [
        "sync",
        "force",
        "upload",
        "download",
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
            choices["send"] = self.ROUTINE_CHOICES

            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""

        mt = MenuText("account/", 100)
        mt.add_info("_info_")
        mt.add_cmd("sync")
        mt.add_cmd("force")
        mt.add_raw("\n")
        mt.add_info("_routines_")
        mt.add_cmd("upload")
        mt.add_cmd("download")
        console.print(text=mt.menu_text, menu="Account")

    @log_start_end(log=logger)
    def call_sync(self, _):
        """Sync"""
        FeatureFlagsController.set_feature_flag(
            "OPENBB_SYNC_ENABLED", not obbff.SYNC_ENABLED, force=True
        )
        User.update_flair()

    def call_force(self, _):
        """Force sync"""
        console.print("Pull, Diff, Push")
        pass

    @log_start_end(log=logger)
    def call_upload(self, _):
        """Upload"""
        console.print("Upload routine")
        pass

    @log_start_end(log=logger)
    def call_download(self, _):
        """Download"""
        console.print("Download routine")
        pass
