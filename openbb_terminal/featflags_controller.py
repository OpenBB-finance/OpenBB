"""Feature Flags Controller Module"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging
from pathlib import Path
from typing import List, Optional, Union

# IMPORTATION THIRDPARTY
from openbb_terminal.core.session.current_user import (
    get_current_user,
    set_preference,
)
from openbb_terminal.core.session.env_handler import write_to_dotenv

# IMPORTATION INTERNAL
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console

# pylint: disable=too-many-lines,no-member,too-many-public-methods,C0302
# pylint:disable=import-outside-toplevel

logger = logging.getLogger(__name__)


def set_and_save_preference(name: str, value: Union[bool, Path, str]):
    """Set preference and write to .env

    Parameters
    ----------
    name : str
        Preference name
    value : Union[bool, Path, str]
        Preference value
    """
    set_preference(name, value)
    write_to_dotenv("OPENBB_" + name, str(value))


class FeatureFlagsController(BaseController):
    """Feature Flags Controller class"""

    CHOICES_COMMANDS: List[str] = [
        "retryload",
        "tab",
        "interactive",
        "cls",
        "watermark",
        "promptkit",
        "thoughts",
        "reporthtml",
        "exithelp",
        "rcontext",
        "richpanel",
        "tbhint",
        "overwrite",
        "version",
    ]
    PATH = "/featflags/"

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        current_user = get_current_user()

        mt = MenuText("featflags/")
        mt.add_info("_info_")
        mt.add_raw("\n")
        mt.add_setting("retryload", current_user.preferences.RETRY_WITH_LOAD)
        mt.add_setting("interactive", current_user.preferences.USE_INTERACTIVE_DF)
        mt.add_setting("cls", current_user.preferences.USE_CLEAR_AFTER_CMD)
        mt.add_setting("promptkit", current_user.preferences.USE_PROMPT_TOOLKIT)
        mt.add_setting("thoughts", current_user.preferences.ENABLE_THOUGHTS_DAY)
        mt.add_setting("reporthtml", current_user.preferences.OPEN_REPORT_AS_HTML)
        mt.add_setting("exithelp", current_user.preferences.ENABLE_EXIT_AUTO_HELP)
        mt.add_setting("rcontext", current_user.preferences.REMEMBER_CONTEXTS)
        mt.add_setting("richpanel", current_user.preferences.ENABLE_RICH_PANEL)
        mt.add_setting("tbhint", current_user.preferences.TOOLBAR_HINT)
        mt.add_setting("overwrite", current_user.preferences.FILE_OVERWRITE)
        mt.add_setting("version", current_user.preferences.SHOW_VERSION)

        console.print(text=mt.menu_text, menu="Feature Flags")

    def call_overwrite(self, _):
        """Process overwrite command"""
        set_and_save_preference(
            "FILE_OVERWRITE", not get_current_user().preferences.FILE_OVERWRITE
        )

    def call_version(self, _):
        """Process version command"""
        set_and_save_preference(
            "SHOW_VERSION", not get_current_user().preferences.SHOW_VERSION
        )

    def call_retryload(self, _):
        """Process retryload command"""
        set_and_save_preference(
            "RETRY_WITH_LOAD", not get_current_user().preferences.RETRY_WITH_LOAD
        )

    @log_start_end(log=logger)
    def call_interactive(self, _):
        """Process interactive command"""
        set_and_save_preference(
            "USE_INTERACTIVE_DF", not get_current_user().preferences.USE_INTERACTIVE_DF
        )

    @log_start_end(log=logger)
    def call_cls(self, _):
        """Process cls command"""
        set_and_save_preference(
            "USE_CLEAR_AFTER_CMD",
            not get_current_user().preferences.USE_CLEAR_AFTER_CMD,
        )

    @log_start_end(log=logger)
    def call_promptkit(self, _):
        """Process promptkit command"""
        set_and_save_preference(
            "USE_PROMPT_TOOLKIT",
            not get_current_user().preferences.USE_PROMPT_TOOLKIT,
        )

    @log_start_end(log=logger)
    def call_thoughts(self, _):
        """Process thoughts command"""
        set_and_save_preference(
            "ENABLE_THOUGHTS_DAY",
            not get_current_user().preferences.ENABLE_THOUGHTS_DAY,
        )

    @log_start_end(log=logger)
    def call_reporthtml(self, _):
        """Process reporthtml command"""
        set_and_save_preference(
            "OPEN_REPORT_AS_HTML",
            not get_current_user().preferences.OPEN_REPORT_AS_HTML,
        )

    @log_start_end(log=logger)
    def call_exithelp(self, _):
        """Process exithelp command"""
        set_and_save_preference(
            "ENABLE_EXIT_AUTO_HELP",
            not get_current_user().preferences.ENABLE_EXIT_AUTO_HELP,
        )

    @log_start_end(log=logger)
    def call_rcontext(self, _):
        """Process rcontext command"""
        set_and_save_preference(
            "REMEMBER_CONTEXTS",
            not get_current_user().preferences.REMEMBER_CONTEXTS,
        )

    @log_start_end(log=logger)
    def call_dt(self, _):
        """Process dt command"""
        set_and_save_preference(
            "USE_DATETIME", not get_current_user().preferences.USE_DATETIME
        )

    @log_start_end(log=logger)
    def call_richpanel(self, _):
        """Process richpanel command"""
        set_and_save_preference(
            "ENABLE_RICH_PANEL",
            not get_current_user().preferences.ENABLE_RICH_PANEL,
        )

    @log_start_end(log=logger)
    def call_tbhint(self, _):
        """Process tbhint command"""
        if get_current_user().preferences.TOOLBAR_HINT:
            console.print("Will take effect when running terminal next.")
        set_and_save_preference(
            "TOOLBAR_HINT", not get_current_user().preferences.TOOLBAR_HINT
        )
