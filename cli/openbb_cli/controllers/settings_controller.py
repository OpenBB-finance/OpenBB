"""Settings Controller Module."""

import argparse
from typing import List, Optional

from openbb_cli.config.constants import AVAILABLE_FLAIRS
from openbb_cli.config.menu_text import MenuText

# pylint: disable=too-many-lines,no-member,too-many-public-methods,C0302
# pylint:disable=import-outside-toplevel
from openbb_cli.controllers.base_controller import BaseController
from openbb_cli.controllers.utils import all_timezones, is_timezone_valid
from openbb_cli.session import Session

session = Session()


class SettingsController(BaseController):
    """Settings Controller class."""

    CHOICES_COMMANDS: List[str] = [
        "interactive",
        "cls",
        "promptkit",
        "exithelp",
        "rcontext",
        "richpanel",
        "tbhint",
        "overwrite",
        "version",
        "console_style",
        "flair",
        "timezone",
        "n_rows",
        "n_cols",
        "obbject_msg",
        "obbject_res",
        "obbject_display",
    ]
    PATH = "/settings/"
    CHOICES_GENERATION = True

    def __init__(self, queue: Optional[List[str]] = None):
        """Initialize the Constructor."""
        super().__init__(queue)

        self.update_completer(self.choices_default)

    def print_help(self):
        """Print help."""
        settings = session.settings

        mt = MenuText("settings/")
        mt.add_info("Feature flags")
        mt.add_setting(
            "interactive",
            settings.USE_INTERACTIVE_DF,
            description="open dataframes in interactive window",
        )
        mt.add_setting(
            "cls",
            settings.USE_CLEAR_AFTER_CMD,
            description="clear console after each command",
        )
        mt.add_setting(
            "promptkit",
            settings.USE_PROMPT_TOOLKIT,
            description="enable prompt toolkit (autocomplete and history)",
        )
        mt.add_setting(
            "exithelp",
            settings.ENABLE_EXIT_AUTO_HELP,
            description="automatically print help when quitting menu",
        )
        mt.add_setting(
            "rcontext",
            settings.REMEMBER_CONTEXTS,
            description="remember contexts between menus",
        )
        mt.add_setting(
            "richpanel",
            settings.ENABLE_RICH_PANEL,
            description="colorful rich CLI panel",
        )
        mt.add_setting(
            "tbhint",
            settings.TOOLBAR_HINT,
            description="displays usage hints in the bottom toolbar",
        )
        mt.add_setting(
            "overwrite",
            settings.FILE_OVERWRITE,
            description="whether to overwrite Excel files if they already exists",
        )
        mt.add_setting(
            "version",
            settings.SHOW_VERSION,
            description="whether to show the version in the bottom right corner",
        )
        mt.add_setting(
            "obbject_msg",
            settings.SHOW_MSG_OBBJECT_REGISTRY,
            description="show obbject registry message after a new result is added",
        )
        mt.add_raw("\n")
        mt.add_info("Preferences")
        mt.add_cmd("console_style", description="apply a custom rich style to the CLI")
        mt.add_cmd("flair", description="choose flair icon")
        mt.add_cmd("timezone", description="pick timezone")
        mt.add_cmd(
            "n_rows", description="number of rows to show on non interactive tables"
        )
        mt.add_cmd(
            "n_cols", description="number of columns to show on non interactive tables"
        )
        mt.add_cmd(
            "obbject_res",
            description="define the maximum number of obbjects allowed in the registry",
        )
        mt.add_cmd(
            "obbject_display",
            description="define the maximum number of cached results to display on the help menu",
        )

        session.console.print(text=mt.menu_text, menu="Settings")

    def call_overwrite(self, _):
        """Process overwrite command."""
        session.settings.set_item("FILE_OVERWRITE", not session.settings.FILE_OVERWRITE)

    def call_version(self, _):
        """Process version command."""
        session.settings.SHOW_VERSION = not session.settings.SHOW_VERSION

    def call_interactive(self, _):
        """Process interactive command."""
        session.settings.set_item(
            "USE_INTERACTIVE_DF", not session.settings.USE_INTERACTIVE_DF
        )

    def call_cls(self, _):
        """Process cls command."""
        session.settings.set_item(
            "USE_CLEAR_AFTER_CMD", not session.settings.USE_CLEAR_AFTER_CMD
        )

    def call_promptkit(self, _):
        """Process promptkit command."""
        session.settings.set_item(
            "USE_PROMPT_TOOLKIT", not session.settings.USE_PROMPT_TOOLKIT
        )

    def call_exithelp(self, _):
        """Process exithelp command."""
        session.settings.set_item(
            "ENABLE_EXIT_AUTO_HELP", not session.settings.ENABLE_EXIT_AUTO_HELP
        )

    def call_rcontext(self, _):
        """Process rcontext command."""
        session.settings.set_item(
            "REMEMBER_CONTEXTS", not session.settings.REMEMBER_CONTEXTS
        )

    def call_dt(self, _):
        """Process dt command."""
        session.settings.set_item("USE_DATETIME", not session.settings.USE_DATETIME)

    def call_richpanel(self, _):
        """Process richpanel command."""
        session.settings.set_item(
            "ENABLE_RICH_PANEL", not session.settings.ENABLE_RICH_PANEL
        )

    def call_tbhint(self, _):
        """Process tbhint command."""
        if session.settings.TOOLBAR_HINT:
            session.console.print("Will take effect when running CLI again.")
        session.settings.set_item("TOOLBAR_HINT", not session.settings.TOOLBAR_HINT)

    def call_obbject_msg(self, _):
        """Process obbject_msg command."""
        session.settings.set_item(
            "SHOW_MSG_OBBJECT_REGISTRY",
            not session.settings.SHOW_MSG_OBBJECT_REGISTRY,
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
            choices=session.style.available_styles,
        )
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser and ns_parser.style:
            session.style.apply(ns_parser.style)
            session.settings.set_item("RICH_STYLE", ns_parser.style)
        elif not other_args:
            session.console.print(
                f"Current console style: {session.settings.RICH_STYLE}"
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
            session.settings.set_item("FLAIR", ns_parser.flair)
        elif not other_args:
            session.console.print(f"Current flair: {session.settings.FLAIR}")

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
                session.settings.set_item("TIMEZONE", ns_parser.timezone)
            else:
                session.console.print(
                    "Invalid timezone. Please enter a valid timezone."
                )
                session.console.print(
                    f"Available timezones are: {', '.join(all_timezones)}"
                )
        elif not other_args:
            session.console.print(f"Current timezone: {session.settings.TIMEZONE}")

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
            session.settings.set_item("ALLOWED_NUMBER_OF_ROWS", ns_parser.rows)

        elif not other_args:
            session.console.print(
                f"Current number of rows: {session.settings.ALLOWED_NUMBER_OF_ROWS}"
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
            session.settings.set_item("ALLOWED_NUMBER_OF_COLUMNS", ns_parser.columns)

        elif not other_args:
            session.console.print(
                f"Current number of columns: {session.settings.ALLOWED_NUMBER_OF_COLUMNS}"
            )

    def call_obbject_res(self, other_args: List[str]):
        """Process obbject_res command."""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="obbject_res",
            description="Maximum allowed number of results to keep in the OBBject Registry.",
            add_help=False,
        )
        parser.add_argument(
            "-n",
            "--number",
            dest="number",
            action="store",
            required=False,
            type=int,
        )
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser and ns_parser.number:
            session.settings.set_item("N_TO_KEEP_OBBJECT_REGISTRY", ns_parser.number)

        elif not other_args:
            session.console.print(
                f"Current maximum allowed number of results to keep in the OBBject registry:"
                f" {session.settings.N_TO_KEEP_OBBJECT_REGISTRY}"
            )

    def call_obbject_display(self, other_args: List[str]):
        """Process obbject_display command."""
        parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="obbject_display",
            description="Number of results to display from the OBBject Registry.",
            add_help=False,
        )
        parser.add_argument(
            "-n",
            "--number",
            dest="number",
            action="store",
            required=False,
            type=int,
        )
        ns_parser = self.parse_simple_args(parser, other_args)

        if ns_parser and ns_parser.number:
            session.settings.set_item("N_TO_DISPLAY_OBBJECT_REGISTRY", ns_parser.number)

        elif not other_args:
            session.console.print(
                f"Current number of results to display from the OBBject registry:"
                f" {session.settings.N_TO_DISPLAY_OBBJECT_REGISTRY}"
            )
