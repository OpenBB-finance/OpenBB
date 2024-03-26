"""Feature Flags Controller Module"""

__docformat__ = "numpy"

import argparse
from pathlib import Path
from typing import List, Optional, Union

# pylint: disable=too-many-lines,no-member,too-many-public-methods,C0302
# pylint:disable=import-outside-toplevel
from openbb_terminal.core.plots.terminal_style import theme
from openbb_terminal.core.session.current_settings import (
    get_current_settings,
    set_settings,
)
from openbb_terminal.core.session.env_handler import write_to_dotenv
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import MenuText, console


def set_and_save_preference(name: str, value: Union[bool, Path, str]):
    """Set preference and write to .env

    Parameters
    ----------
    name : str
        Preference name
    value : Union[bool, Path, str]
        Preference value
    """
    set_settings(name, value)
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
        "console_style",
    ]
    PATH = "/featflags/"

    def __init__(self, queue: Optional[List[str]] = None):
        """Constructor"""
        super().__init__(queue)

        if session and get_current_settings().USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        settings = get_current_settings()

        mt = MenuText("featflags/")
        mt.add_info("_info_")
        mt.add_raw("\n")
        mt.add_setting("interactive", settings.USE_INTERACTIVE_DF)
        mt.add_setting("cls", settings.USE_CLEAR_AFTER_CMD)
        mt.add_setting("promptkit", settings.USE_PROMPT_TOOLKIT)
        mt.add_setting("exithelp", settings.ENABLE_EXIT_AUTO_HELP)
        mt.add_setting("rcontext", settings.REMEMBER_CONTEXTS)
        mt.add_setting("richpanel", settings.ENABLE_RICH_PANEL)
        mt.add_setting("tbhint", settings.TOOLBAR_HINT)
        mt.add_setting("overwrite", settings.FILE_OVERWRITE)
        mt.add_setting("version", settings.SHOW_VERSION)
        mt.add_raw("\n")
        mt.add_info("_settings_")
        mt.add_raw("\n")
        mt.add_cmd("console_style")

        console.print(text=mt.menu_text, menu="Feature Flags")

    def call_overwrite(self, _):
        """Process overwrite command"""
        set_and_save_preference(
            "FILE_OVERWRITE", not get_current_settings().FILE_OVERWRITE
        )

    def call_version(self, _):
        """Process version command"""
        set_and_save_preference("SHOW_VERSION", not get_current_settings().SHOW_VERSION)

    def call_interactive(self, _):
        """Process interactive command"""
        set_and_save_preference(
            "USE_INTERACTIVE_DF", not get_current_settings().USE_INTERACTIVE_DF
        )

    def call_cls(self, _):
        """Process cls command"""
        set_and_save_preference(
            "USE_CLEAR_AFTER_CMD",
            not get_current_settings().USE_CLEAR_AFTER_CMD,
        )

    def call_promptkit(self, _):
        """Process promptkit command"""
        set_and_save_preference(
            "USE_PROMPT_TOOLKIT",
            not get_current_settings().USE_PROMPT_TOOLKIT,
        )

    def call_exithelp(self, _):
        """Process exithelp command"""
        set_and_save_preference(
            "ENABLE_EXIT_AUTO_HELP",
            not get_current_settings().ENABLE_EXIT_AUTO_HELP,
        )

    def call_rcontext(self, _):
        """Process rcontext command"""
        set_and_save_preference(
            "REMEMBER_CONTEXTS",
            not get_current_settings().REMEMBER_CONTEXTS,
        )

    def call_dt(self, _):
        """Process dt command"""
        set_and_save_preference("USE_DATETIME", not get_current_settings().USE_DATETIME)

    def call_richpanel(self, _):
        """Process richpanel command"""
        set_and_save_preference(
            "ENABLE_RICH_PANEL",
            not get_current_settings().ENABLE_RICH_PANEL,
        )

    def call_tbhint(self, _):
        """Process tbhint command"""
        if get_current_settings().TOOLBAR_HINT:
            console.print("Will take effect when running terminal next.")
        set_and_save_preference("TOOLBAR_HINT", not get_current_settings().TOOLBAR_HINT)

    def call_console_style(self, other_args: List[str]) -> None:
        """Process cosole_style command"""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="console_style",
            description="Change your custom console style.",
            add_help=False,
        )
        parser.add_argument(
            "-s",
            "--style",
            dest="style",
            action="store",
            required=True,
            choices=theme.available_styles,
        )

        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser:
            theme.apply_console_style(ns_parser.style)
            set_and_save_preference("RICH_STYLE", ns_parser.style)
