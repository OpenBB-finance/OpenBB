"""Settings Controller Module"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
import os
import os.path
import argparse
import logging
from typing import List
import pytz

# IMPORTATION THIRDPARTY
from dotenv import set_key
from prompt_toolkit.completion import NestedCompleter

# IMPORTATION INTERNAL
from openbb_terminal import config_plot as cfg_plot
from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    get_flair,
    parse_simple_args,
    get_user_timezone_or_invalid,
    replace_user_timezone,
    set_export_folder,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText

# pylint: disable=too-many-lines,no-member,too-many-public-methods,C0302
# pylint:disable=import-outside-toplevel

logger = logging.getLogger(__name__)


class SettingsController(BaseController):
    """Settings Controller class"""

    CHOICES_COMMANDS: List[str] = [
        "dt",
        "autoscaling",
        "dpi",
        "backend",
        "height",
        "width",
        "pheight",
        "pwidth",
        "monitor",
        "lang",
        "tz",
        "export",
        "source",
    ]
    PATH = "/settings/"

    all_timezones = [tz.replace("/", "_") for tz in pytz.all_timezones]

    languages_available = [
        lang.strip(".yml")
        for lang in os.listdir(obbff.i18n_dict_location)
        if lang.endswith(".yml")
    ]

    def __init__(self, queue: List[str] = None, env_file: str = ".env"):
        """Constructor"""
        super().__init__(queue)
        self.env_file = env_file

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["tz"] = {c: None for c in self.all_timezones}
            choices["lang"] = {c: None for c in self.languages_available}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("settings/")
        mt.add_info("_info_")
        mt.add_raw("\n")
        mt.add_setting("dt", obbff.USE_DATETIME)
        mt.add_raw("\n")
        mt.add_param("_flair", get_flair())
        mt.add_raw("\n")
        mt.add_cmd("lang")
        mt.add_raw("\n")
        mt.add_param("_language", obbff.USE_LANGUAGE)
        mt.add_raw("\n")
        mt.add_cmd("export")
        mt.add_raw("\n")
        mt.add_param(
            "_export_folder",
            obbff.EXPORT_FOLDER_PATH
            if obbff.EXPORT_FOLDER_PATH
            else "DEFAULT (folder: exports/)",
        )
        mt.add_raw("\n")
        mt.add_cmd("tz")
        mt.add_raw("\n")
        mt.add_param("_timezone", get_user_timezone_or_invalid())
        mt.add_raw("\n")
        mt.add_setting("autoscaling", obbff.USE_PLOT_AUTOSCALING)
        if obbff.USE_PLOT_AUTOSCALING:
            mt.add_cmd("pheight")
            mt.add_cmd("pwidth")
            mt.add_raw("\n")
            mt.add_param("_plot_height_pct", cfg_plot.PLOT_HEIGHT_PERCENTAGE, 16)
            mt.add_param("_plot_width_pct", cfg_plot.PLOT_WIDTH_PERCENTAGE, 16)
        else:
            mt.add_cmd("height")
            mt.add_cmd("width")
            mt.add_raw("\n")
            mt.add_param("_plot_height", cfg_plot.PLOT_HEIGHT, 12)
            mt.add_param("_plot_width", cfg_plot.PLOT_WIDTH, 12)
        mt.add_raw("\n")
        mt.add_cmd("dpi")
        mt.add_raw("\n")
        mt.add_param("_dpi", cfg_plot.PLOT_DPI)
        mt.add_raw("\n")
        mt.add_cmd("backend")
        mt.add_raw("\n")
        mt.add_param("_backend", cfg_plot.BACKEND)
        mt.add_raw("\n")
        mt.add_cmd("monitor")
        mt.add_raw("\n")
        mt.add_param("_monitor", cfg_plot.MONITOR)
        mt.add_raw("\n")
        mt.add_cmd("source")
        mt.add_raw("\n")
        mt.add_param("_data_source", obbff.PREFERRED_DATA_SOURCE_FILE)
        mt.add_raw("\n")

        console.print(text=mt.menu_text, menu="Settings")

    @log_start_end(log=logger)
    def call_dt(self, _):
        """Process dt command"""
        obbff.USE_DATETIME = not obbff.USE_DATETIME
        set_key(obbff.ENV_FILE, "OPENBB_USE_DATETIME", str(obbff.USE_DATETIME))
        console.print("")

    @log_start_end(log=logger)
    def call_source(self, other_args: List[str]):
        """Process source command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="source",
            description="Preferred data source file.",
        )
        parser.add_argument(
            "-v",
            "--value",
            type=str,
            default=os.getcwd() + os.path.sep + "sources.json.default",
            dest="value",
            help="value",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            try:

                the_path = os.getcwd() + os.path.sep + ns_parser.value
                console.print("Loading sources from " + the_path)
                with open(the_path):
                    # Try to open the file to get an exception if the file doesn't exist
                    pass

            except Exception as e:
                console.print("Couldn't open the sources file!")
                console.print(e)
            obbff.PREFERRED_DATA_SOURCE_FILE = ns_parser.value
            set_key(
                obbff.ENV_FILE,
                "OPENBB_PREFERRED_DATA_SOURCE_FILE",
                str(ns_parser.value),
            )
            console.print("")

    @log_start_end(log=logger)
    def call_autoscaling(self, _):
        """Process autoscaling command"""
        obbff.USE_PLOT_AUTOSCALING = not obbff.USE_PLOT_AUTOSCALING
        set_key(
            obbff.ENV_FILE,
            "OPENBB_USE_PLOT_AUTOSCALING",
            str(obbff.USE_PLOT_AUTOSCALING),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_dpi(self, other_args: List[str]):
        """Process dpi command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dpi",
            description="Dots per inch.",
        )
        parser.add_argument(
            "-v",
            "--value",
            type=int,
            dest="value",
            help="value",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            set_key(obbff.ENV_FILE, "OPENBB_PLOT_DPI", str(ns_parser.value))
            cfg_plot.PLOT_DPI = ns_parser.value
            console.print("")

    @log_start_end(log=logger)
    def call_height(self, other_args: List[str]):
        """Process height command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="height",
            description="select plot height (autoscaling disabled)",
        )
        parser.add_argument(
            "-v",
            "--value",
            type=int,
            dest="value",
            help="value",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            set_key(obbff.ENV_FILE, "OPENBB_PLOT_HEIGHT", str(ns_parser.value))
            cfg_plot.PLOT_HEIGHT = ns_parser.value
            console.print("")

    @log_start_end(log=logger)
    def call_width(self, other_args: List[str]):
        """Process width command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="width",
            description="select plot width (autoscaling disabled)",
        )
        parser.add_argument(
            "-v",
            "--value",
            type=int,
            dest="value",
            help="value",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            set_key(obbff.ENV_FILE, "OPENBB_PLOT_WIDTH", str(ns_parser.value))
            cfg_plot.PLOT_WIDTH = ns_parser.value
            console.print("")

    @log_start_end(log=logger)
    def call_pheight(self, other_args: List[str]):
        """Process pheight command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pheight",
            description="select plot height percentage (autoscaling enabled)",
        )
        parser.add_argument(
            "-v",
            "--value",
            type=int,
            dest="value",
            help="value",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            set_key(
                obbff.ENV_FILE,
                "OPENBB_PLOT_HEIGHT_PERCENTAGE",
                str(ns_parser.value),
            )
            cfg_plot.PLOT_HEIGHT_PERCENTAGE = ns_parser.value
            console.print("")

    @log_start_end(log=logger)
    def call_pwidth(self, other_args: List[str]):
        """Process pwidth command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pwidth",
            description="select plot width percentage (autoscaling enabled)",
        )
        parser.add_argument(
            "-v",
            "--value",
            type=float,
            dest="value",
            help="value",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            set_key(
                obbff.ENV_FILE,
                "OPENBB_PLOT_WIDTH_PERCENTAGE",
                str(ns_parser.value),
            )
            cfg_plot.PLOT_WIDTH_PERCENTAGE = ns_parser.value
            console.print("")

    @log_start_end(log=logger)
    def call_monitor(self, other_args: List[str]):
        """Process pwidth command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pwidth",
            description="choose which monitor to scale: 0-primary, 1-secondary (autoscaling enabled)",
        )
        parser.add_argument(
            "-v",
            "--value",
            type=int,
            dest="value",
            help="value",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            set_key(obbff.ENV_FILE, "OPENBB_MONITOR", str(ns_parser.value))
            cfg_plot.MONITOR = ns_parser.value
            console.print("")

    @log_start_end(log=logger)
    def call_backend(self, other_args: List[str]):
        """Process backend command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="backend",
            description="Backend to use for plotting",
        )
        parser.add_argument(
            "-v",
            "--value",
            type=str,
            dest="value",
            help="value",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            set_key(obbff.ENV_FILE, "OPENBB_BACKEND", str(ns_parser.value))
            if ns_parser.value == "None":
                cfg_plot.BACKEND = None  # type: ignore
            else:
                cfg_plot.BACKEND = ns_parser.value
            console.print("")

    @log_start_end(log=logger)
    def call_lang(self, other_args: List[str]):
        """Process lang command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="lang",
            description="Choose language for terminal",
        )
        parser.add_argument(
            "-v",
            "--value",
            type=str,
            dest="value",
            help="Language",
            choices=self.languages_available,
            default="",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            if ns_parser.value:
                set_key(obbff.ENV_FILE, "OPENBB_USE_LANGUAGE", str(ns_parser.value))
                obbff.USE_LANGUAGE = ns_parser.value
            else:
                console.print(
                    f"Languages available: {', '.join(self.languages_available)}"
                )
            console.print("")

    def call_tz(self, other_args: List[str]):
        """Process tz command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            description="""
                   Setting a different timezone
               """,
        )
        parser.add_argument(
            "-t",
            dest="timezone",
            help="Choose timezone",
            required="-h" not in other_args,
            choices=self.all_timezones,
        )

        if other_args and "-t" not in other_args[0]:
            other_args.insert(0, "-t")

        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            if ns_parser.timezone:
                replace_user_timezone(ns_parser.timezone.replace("_", "/", 1))

    def call_export(self, other_args: List[str]):
        """Process export command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="export",
            description="Select folder where to export data",
        )
        parser.add_argument(
            "-f",
            "--folder",
            type=str,
            dest="folder",
            help="Folder where to export data. 'default' redirects to OpenBB Terminal 'exports'",
            default="default",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = parse_simple_args(parser, other_args)

        if ns_parser:
            if other_args or self.queue:
                if other_args:
                    export_path = ""
                else:
                    # Re-add the initial slash for an absolute directory provided
                    export_path = "/"

                export_path += "/".join([ns_parser.folder] + self.queue)
                self.queue = []

                base_path = os.path.dirname(os.path.abspath(__file__))
                default_path = os.path.join(base_path, "exports")

                success_export = False
                while not success_export:
                    if export_path.upper() == "DEFAULT":
                        console.print(
                            f"Export data to be saved in the default folder: '{default_path}'"
                        )
                        set_export_folder(self.env_file, path_folder="")
                        success_export = True
                    else:
                        # If the path selected does not start from the user root, give relative location from root
                        if export_path[0] == "~":
                            export_path = export_path.replace(
                                "~", os.path.expanduser("~")
                            )
                        elif export_path[0] != "/":
                            export_path = os.path.join(base_path, export_path)

                        # Check if the directory exists
                        if os.path.isdir(export_path):
                            console.print(
                                f"Export data to be saved in the selected folder: '{export_path}'"
                            )
                            set_export_folder(self.env_file, path_folder=export_path)
                            success_export = True
                        else:
                            console.print(
                                "[red]The path selected to export data does not exist![/red]\n"
                            )
                            user_opt = "None"
                            while user_opt not in ("Y", "N"):
                                user_opt = input(
                                    f"Do you wish to create folder: `{export_path}` ? [Y/N]\n"
                                ).upper()

                            if user_opt == "Y":
                                os.makedirs(export_path)
                                console.print(
                                    f"[green]Folder '{export_path}' successfully created.[/green]"
                                )
                                set_export_folder(
                                    self.env_file, path_folder=export_path
                                )
                            else:
                                # Do not update export_folder path since we will keep the same as before
                                path_display = (
                                    obbff.EXPORT_FOLDER_PATH
                                    if obbff.EXPORT_FOLDER_PATH
                                    else "DEFAULT (folder: exports/)"
                                )
                                console.print(
                                    "[yellow]Export data to keep being saved in"
                                    + f"the selected folder: {path_display}[/yellow]"
                                )
                            success_export = True

        console.print()
