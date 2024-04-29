"""Feature Flags Controller Module."""

import argparse
from typing import List, Optional

from openbb_terminal.config.completer import NestedCompleter
from openbb_terminal.config.constants import AVAILABLE_FLAIRS
from openbb_terminal.config.menu_text import MenuText

# pylint: disable=too-many-lines,no-member,too-many-public-methods,C0302
# pylint:disable=import-outside-toplevel
from openbb_terminal.controllers.base_controller import BaseController
from openbb_terminal.controllers.utils import all_timezones, is_timezone_valid
from openbb_terminal.session import Session


class FeatureFlagsController(BaseController):
    """Feature Flags Controller class."""

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
        "flair",
        "timezone",
        "language",
        "n_rows",
        "n_cols",
    ]
    PATH = "/settings/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Initialize the Constructor."""
        super().__init__(queue)

        self._session = Session()

        if self._session.prompt_session and self._session.settings.USE_PROMPT_TOOLKIT:
            choices: dict = self.choices_default
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help."""
        settings = self._session.settings

        mt = MenuText("settings/")
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
        mt.add_cmd("flair")
        mt.add_cmd("timezone")
        mt.add_cmd("language")
        mt.add_cmd("n_rows")
        mt.add_cmd("n_cols")

        self._session.console.print(text=mt.menu_text, menu="Feature Flags")

    def call_overwrite(self, _):
        """Process overwrite command."""
        self._session.settings.set_item(
            "FILE_OVERWRITE", not self._session.settings.FILE_OVERWRITE
        )

    def call_version(self, _):
        """Process version command."""
        self._session.settings.SHOW_VERSION = not self._session.settings.SHOW_VERSION

    def call_interactive(self, _):
        """Process interactive command."""
        self._session.settings.set_item(
            "USE_INTERACTIVE_DF", not self._session.settings.USE_INTERACTIVE_DF
        )

    def call_cls(self, _):
        """Process cls command."""
        self._session.settings.set_item(
            "USE_CLEAR_AFTER_CMD", not self._session.settings.USE_CLEAR_AFTER_CMD
        )

    def call_promptkit(self, _):
        """Process promptkit command."""
        self._session.settings.set_item(
            "USE_PROMPT_TOOLKIT", not self._session.settings.USE_PROMPT_TOOLKIT
        )

    def call_exithelp(self, _):
        """Process exithelp command."""
        self._session.settings.set_item(
            "ENABLE_EXIT_AUTO_HELP", not self._session.settings.ENABLE_EXIT_AUTO_HELP
        )

    def call_rcontext(self, _):
        """Process rcontext command."""
        self._session.settings.set_item(
            "REMEMBER_CONTEXTS", not self._session.settings.REMEMBER_CONTEXTS
        )

    def call_dt(self, _):
        """Process dt command."""
        self._session.settings.set_item(
            "USE_DATETIME", not self._session.settings.USE_DATETIME
        )

    def call_richpanel(self, _):
        """Process richpanel command."""
        self._session.settings.set_item(
            "ENABLE_RICH_PANEL", not self._session.settings.ENABLE_RICH_PANEL
        )

    def call_tbhint(self, _):
        """Process tbhint command."""
        if self._session.settings.TOOLBAR_HINT:
            self._session.console.print("Will take effect when running terminal next.")
        self._session.settings.set_item(
            "TOOLBAR_HINT", not self._session.settings.TOOLBAR_HINT
        )

    def call_console_style(self, other_args: List[str]) -> None:
        """Process cosole_style command."""
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
            required=False,
            choices=self._session.style.available_styles,
        )
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser and ns_parser.style:
            self._session.style.apply(ns_parser.style)
            self._session.settings.set_item("RICH_STYLE", ns_parser.style)
            self._session.console.print(
                f"Console style changed to: {self._session.settings.RICH_STYLE}, run 'reset'"
                " or restart the program to apply the changes."
            )
        elif not other_args:
            self._session.console.print(
                f"Current console style: {self._session.settings.RICH_STYLE}"
            )

    def call_flair(self, other_args: List[str]) -> None:
        """Process flair command."""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="flair",
            description="Change your custom flair.",
            add_help=False,
        )
        parser.add_argument(
            "-f",
            "--flair",
            dest="flair",
            action="store",
            required=False,
            choices=list(AVAILABLE_FLAIRS.keys()),
        )
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser and ns_parser.flair:
            self._session.settings.set_item("FLAIR", ns_parser.flair)
        elif not other_args:
            self._session.console.print(
                f"Current flair: {self._session.settings.FLAIR}"
            )

    def call_timezone(self, other_args: List[str]) -> None:
        """Process timezone command."""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="timezone",
            description="Change your custom timezone.",
            add_help=False,
        )
        parser.add_argument(
            "-t",
            "--timezone",
            dest="timezone",
            action="store",
            required=False,
            type=str,
            choices=all_timezones,
        )
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser and ns_parser.timezone:
            if is_timezone_valid(ns_parser.timezone):
                self._session.settings.set_item("TIMEZONE", ns_parser.timezone)
            else:
                self._session.console.print(
                    "Invalid timezone. Please enter a valid timezone."
                )
                self._session.console.print(
                    f"Available timezones are: {', '.join(all_timezones)}"
                )
        elif not other_args:
            self._session.console.print(
                f"Current timezone: {self._session.settings.TIMEZONE}"
            )

    def call_language(self, other_args: List[str]) -> None:
        """Process language command."""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="language",
            description="Change your custom language.",
            add_help=False,
        )
        parser.add_argument(
            "-l",
            "--language",
            dest="language",
            action="store",
            required=False,
            type=str,
        )
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser and ns_parser.language:
            self._session.settings.set_item("USE_LANGUAGE", ns_parser.language)

        elif not other_args:
            self._session.console.print(
                f"Current language: {self._session.settings.USE_LANGUAGE}"
            )

    def call_n_rows(self, other_args: List[str]) -> None:
        """Process n_rows command."""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="n_rows",
            description="Number of rows to show (when not using interactive tables).",
            add_help=False,
        )
        parser.add_argument(
            "-r",
            "--rows",
            dest="rows",
            action="store",
            required=False,
            type=int,
        )
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser and ns_parser.rows:
            self._session.settings.set_item("ALLOWED_NUMBER_OF_ROWS", ns_parser.rows)

        elif not other_args:
            self._session.console.print(
                f"Current number of rows: {self._session.settings.ALLOWED_NUMBER_OF_ROWS}"
            )

    def call_n_cols(self, other_args: List[str]) -> None:
        """Process n_cols command."""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="n_cols",
            description="Number of columns to show (when not using interactive tables).",
            add_help=False,
        )
        parser.add_argument(
            "-c",
            "--columns",
            dest="columns",
            action="store",
            required=False,
            type=int,
        )
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser and ns_parser.columns:
            self._session.settings.set_item(
                "ALLOWED_NUMBER_OF_COLUMNS", ns_parser.columns
            )

        elif not other_args:
            self._session.console.print(
                f"Current number of columns: {self._session.settings.ALLOWED_NUMBER_OF_COLUMNS}"
            )
