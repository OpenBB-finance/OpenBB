"""Settings Controller Module"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
import os
import os.path
import argparse
import logging
from pathlib import Path
from typing import List
import pytz

# IMPORTATION THIRDPARTY
from dotenv import set_key

# IMPORTATION INTERNAL
from openbb_terminal import config_plot as cfg_plot
from openbb_terminal import feature_flags as obbff
from openbb_terminal.core.config.paths import USER_ENV_FILE, USER_DATA_DIRECTORY
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    get_flair,
    parse_simple_args,
    get_user_timezone_or_invalid,
    replace_user_timezone,
    set_user_data_folder,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText

# pylint: disable=too-many-lines,no-member,too-many-public-methods,C0302
# pylint: disable=import-outside-toplevel

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
        "userdata",
        "source",
        "flair",
        "colors",
    ]
    PATH = "/settings/"

    all_timezones = [tz.replace("/", "_") for tz in pytz.all_timezones]

    languages_available = [
        lang.strip(".yml")
        for lang in os.listdir(obbff.i18n_dict_location)
        if lang.endswith(".yml")
    ]

    def __init__(self, queue: List[str] = None, env_file: str = str(USER_ENV_FILE)):
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
        mt.add_cmd("colors")
        mt.add_setting("dt", obbff.USE_DATETIME)
        mt.add_cmd("flair")
        mt.add_raw("\n")
        mt.add_param("_flair", get_flair())
        mt.add_raw("\n")
        mt.add_cmd("lang")
        mt.add_raw("\n")
        mt.add_param("_language", obbff.USE_LANGUAGE)
        mt.add_raw("\n")
        mt.add_cmd("userdata")
        mt.add_raw("\n")
        mt.add_param(
            "_user_data_folder",
            USER_DATA_DIRECTORY,
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
    def call_colors(self, _):
        """Process colors command"""
        console.print(
            "\n1. Play with the terminal coloring embedded in our website https://openbb.co/customize\n"
        )
        console.print("2. Once happy, click 'Download Theme'\n")
        console.print(
            "3. The file 'openbb_config.richstyle.json' should be downloaded\n"
        )
        console.print(
            "4. Insert that config file inside /OpenBBUserData/styles/user/\n"
        )
        console.print("5. Close the terminal and run it again.\n")

    @log_start_end(log=logger)
    def call_dt(self, _):
        """Process dt command"""
        obbff.USE_DATETIME = not obbff.USE_DATETIME
        set_key(obbff.USER_ENV_FILE, "OPENBB_USE_DATETIME", str(obbff.USE_DATETIME))

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
                obbff.USER_ENV_FILE,
                "OPENBB_PREFERRED_DATA_SOURCE_FILE",
                str(ns_parser.value),
            )

    @log_start_end(log=logger)
    def call_autoscaling(self, _):
        """Process autoscaling command"""
        obbff.USE_PLOT_AUTOSCALING = not obbff.USE_PLOT_AUTOSCALING
        set_key(
            obbff.USER_ENV_FILE,
            "OPENBB_USE_PLOT_AUTOSCALING",
            str(obbff.USE_PLOT_AUTOSCALING),
        )

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
            required="-h" not in other_args,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser and ns_parser.value:
            set_key(obbff.USER_ENV_FILE, "OPENBB_PLOT_DPI", str(ns_parser.value))
            cfg_plot.PLOT_DPI = ns_parser.value

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
            required="-h" not in other_args,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            set_key(obbff.USER_ENV_FILE, "OPENBB_PLOT_HEIGHT", str(ns_parser.value))
            cfg_plot.PLOT_HEIGHT = ns_parser.value

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
            required="-h" not in other_args,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            set_key(obbff.USER_ENV_FILE, "OPENBB_PLOT_WIDTH", str(ns_parser.value))
            cfg_plot.PLOT_WIDTH = ns_parser.value

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
                obbff.USER_ENV_FILE,
                "OPENBB_PLOT_HEIGHT_PERCENTAGE",
                str(ns_parser.value),
            )
            cfg_plot.PLOT_HEIGHT_PERCENTAGE = ns_parser.value

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
                obbff.USER_ENV_FILE,
                "OPENBB_PLOT_WIDTH_PERCENTAGE",
                str(ns_parser.value),
            )
            cfg_plot.PLOT_WIDTH_PERCENTAGE = ns_parser.value

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
            set_key(obbff.USER_ENV_FILE, "OPENBB_MONITOR", str(ns_parser.value))
            cfg_plot.MONITOR = ns_parser.value

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
            set_key(obbff.USER_ENV_FILE, "OPENBB_BACKEND", str(ns_parser.value))
            if ns_parser.value == "None":
                cfg_plot.BACKEND = None  # type: ignore
            else:
                cfg_plot.BACKEND = ns_parser.value

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
                set_key(
                    obbff.USER_ENV_FILE, "OPENBB_USE_LANGUAGE", str(ns_parser.value)
                )
                obbff.USE_LANGUAGE = ns_parser.value
            else:
                console.print(
                    f"Languages available: {', '.join(self.languages_available)}"
                )

    @log_start_end(log=logger)
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

    @log_start_end(log=logger)
    def call_flair(self, other_args: List[str]):
        """Process flair command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="flair",
            description="set the flair emoji to be used",
        )
        parser.add_argument(
            "-e",
            "--emoji",
            type=str,
            dest="emoji",
            help="flair emoji to be used",
            nargs="+",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-e")
        ns_parser = parse_simple_args(parser, other_args)
        if ns_parser:
            if not ns_parser.emoji:
                ns_parser.emoji = ""
            else:
                ns_parser.emoji = " ".join(ns_parser.emoji)
            set_key(obbff.USER_ENV_FILE, "OPENBB_USE_FLAIR", str(ns_parser.emoji))
            obbff.USE_FLAIR = ns_parser.emoji

    @log_start_end(log=logger)
    def call_userdata(self, other_args: List[str]):
        """Process userdata command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="userdata",
            description="Set folder to store user data such as exports, presets, logs",
        )
        parser.add_argument(
            "--folder",
            type=str,
            dest="folder",
            help="Folder where to store user data. ",
            default=f"{str(Path.home() / 'OpenBBUserData')}",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "--folder")
        ns_parser = parse_simple_args(parser, other_args)

        if ns_parser:
            if other_args or self.queue:
                if other_args:
                    userdata_path = ""
                else:
                    # Re-add the initial slash for an absolute directory provided
                    userdata_path = "/"

                userdata_path += "/".join([ns_parser.folder] + self.queue)
                self.queue = []

                userdata_path = userdata_path.replace("'", "").replace('"', "")

                default_path = Path.home() / "OpenBBUserData"

                success_userdata = False
                while not success_userdata:
                    if userdata_path.upper() == "DEFAULT":
                        console.print(
                            f"User data to be saved in the default folder: '{default_path}'"
                        )
                        set_user_data_folder(
                            self.env_file, path_folder=str(default_path)
                        )
                        success_userdata = True
                    else:
                        # If the path selected does not start from the user root, give relative location from root
                        if userdata_path[0] == "~":
                            userdata_path = userdata_path.replace(
                                "~", os.path.expanduser("~")
                            )

                        # Check if the directory exists
                        if os.path.isdir(userdata_path):
                            console.print(
                                f"User data to be saved in the selected folder: '{userdata_path}'"
                            )
                            set_user_data_folder(
                                self.env_file, path_folder=userdata_path
                            )
                            success_userdata = True
                        else:
                            console.print(
                                "[red]The path selected to user data does not exist![/red]\n"
                            )
                            user_opt = "None"
                            while user_opt not in ("Y", "N"):
                                user_opt = input(
                                    f"Do you wish to create folder: `{userdata_path}` ? [Y/N]\n"
                                ).upper()

                            if user_opt == "Y":
                                os.makedirs(userdata_path)
                                console.print(
                                    f"[green]Folder '{userdata_path}' successfully created.[/green]"
                                )
                                set_user_data_folder(
                                    self.env_file, path_folder=userdata_path
                                )
                            else:
                                # Do not update userdata_folder path since we will keep the same as before
                                console.print(
                                    "[yellow]User data to keep being saved in"
                                    + f"the selected folder: {str(USER_DATA_DIRECTORY)}[/yellow]"
                                )
                            success_userdata = True

        console.print()
