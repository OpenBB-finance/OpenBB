"""Settings Controller Module"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
import os
import argparse
import logging
from typing import List

# IMPORTATION THIRDPARTY
from dotenv import set_key
from prompt_toolkit.completion import NestedCompleter

# IMPORTATION INTERNAL
from openbb_terminal import config_plot as cfg_plot
from openbb_terminal import feature_flags as obbff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_flair, parse_known_args_and_warn
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console, MenuText

# pylint: disable=too-many-lines,no-member,too-many-public-methods,C0302
# pylint:disable=import-outside-toplevel

logger = logging.getLogger(__name__)


class SettingsController(BaseController):
    """Settings Controller class"""

    CHOICES_COMMANDS: List[str] = [
        "logcollection",
        "tab",
        "cls",
        "color",
        "flair",
        "dt",
        "ion",
        "watermark",
        "cmdloc",
        "promptkit",
        "predict",
        "autoscaling",
        "thoughts",
        "reporthtml",
        "exithelp",
        "rcontext",
        "rich",
        "richpanel",
        "dpi",
        "backend",
        "height",
        "width",
        "pheight",
        "pwidth",
        "monitor",
        "lang",
    ]
    PATH = "/settings/"

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and obbff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("settings/")
        mt.add_info("_feature_flags_")
        mt.add_raw("\n")
        mt.add_setting("logcollection", obbff.LOG_COLLECTION)
        mt.add_setting("tab", obbff.USE_TABULATE_DF)
        mt.add_setting("cls", obbff.USE_CLEAR_AFTER_CMD)
        mt.add_setting("color", obbff.USE_COLOR)
        mt.add_setting("promptkit", obbff.USE_PROMPT_TOOLKIT)
        mt.add_setting("predict", obbff.ENABLE_PREDICT)
        mt.add_setting("thoughts", obbff.ENABLE_THOUGHTS_DAY)
        mt.add_setting("reporthtml", obbff.OPEN_REPORT_AS_HTML)
        mt.add_setting("exithelp", obbff.ENABLE_EXIT_AUTO_HELP)
        mt.add_setting("rcontext", obbff.REMEMBER_CONTEXTS)
        mt.add_setting("rich", obbff.ENABLE_RICH)
        mt.add_setting("richpanel", obbff.ENABLE_RICH_PANEL)
        mt.add_setting("ion", obbff.USE_ION)
        mt.add_setting("watermark", obbff.USE_WATERMARK)
        mt.add_setting("cmdloc", obbff.USE_CMD_LOCATION_FIGURE)
        mt.add_setting("autoscaling", obbff.USE_PLOT_AUTOSCALING)
        mt.add_setting("dt", obbff.USE_DATETIME)
        mt.add_raw("\n")
        mt.add_cmd("flair")
        mt.add_raw("\n")
        mt.add_param("_flair", get_flair())
        mt.add_raw("\n")
        mt.add_cmd("lang")
        mt.add_raw("\n")
        mt.add_param("_language", obbff.USE_LANGUAGE)
        mt.add_raw("\n")
        mt.add_cmd("dpi")
        mt.add_cmd("backend")
        mt.add_cmd("height", "", not obbff.USE_PLOT_AUTOSCALING)
        mt.add_cmd("width", "", not obbff.USE_PLOT_AUTOSCALING)
        mt.add_cmd("pheight", "", obbff.USE_PLOT_AUTOSCALING)
        mt.add_cmd("pwidth", "", obbff.USE_PLOT_AUTOSCALING)
        mt.add_cmd("monitor")
        mt.add_raw("\n")
        mt.add_param("_dpi", cfg_plot.PLOT_DPI, 19)
        mt.add_param("_backend", cfg_plot.BACKEND, 19)
        if obbff.USE_PLOT_AUTOSCALING:
            mt.add_param("_plot_height_pct", cfg_plot.PLOT_HEIGHT_PERCENTAGE, 19)
            mt.add_param("_plot_width_pct", cfg_plot.PLOT_WIDTH_PERCENTAGE, 19)
        else:
            mt.add_param("_plot_height", cfg_plot.PLOT_HEIGHT, 19)
            mt.add_param("_plot_width", cfg_plot.PLOT_WIDTH, 19)
        mt.add_param("_monitor", cfg_plot.MONITOR, 19)

        console.print(text=mt.menu_text, menu="Settings")

    @log_start_end(log=logger)
    def call_logcollection(self, _):
        """Process logcollection command"""
        obbff.LOG_COLLECTION = not obbff.LOG_COLLECTION
        set_key(obbff.ENV_FILE, "OPENBB_LOG_COLLECTION", str(obbff.LOG_COLLECTION))
        console.print("")

    @log_start_end(log=logger)
    def call_tab(self, _):
        """Process tab command"""
        obbff.USE_TABULATE_DF = not obbff.USE_TABULATE_DF
        set_key(obbff.ENV_FILE, "OPENBB_USE_TABULATE_DF", str(obbff.USE_TABULATE_DF))
        console.print("")

    @log_start_end(log=logger)
    def call_cls(self, _):
        """Process cls command"""
        obbff.USE_CLEAR_AFTER_CMD = not obbff.USE_CLEAR_AFTER_CMD
        set_key(
            obbff.ENV_FILE,
            "OPENBB_USE_CLEAR_AFTER_CMD",
            str(obbff.USE_CLEAR_AFTER_CMD),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_color(self, _):
        """Process color command"""
        obbff.USE_COLOR = not obbff.USE_COLOR
        set_key(obbff.ENV_FILE, "OPENBB_USE_COLOR", str(obbff.USE_COLOR))
        console.print("")

    @log_start_end(log=logger)
    def call_promptkit(self, _):
        """Process promptkit command"""
        obbff.USE_PROMPT_TOOLKIT = not obbff.USE_PROMPT_TOOLKIT
        set_key(
            obbff.ENV_FILE,
            "OPENBB_USE_PROMPT_TOOLKIT",
            str(obbff.USE_PROMPT_TOOLKIT),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_predict(self, _):
        """Process predict command"""
        obbff.ENABLE_PREDICT = not obbff.ENABLE_PREDICT
        set_key(obbff.ENV_FILE, "OPENBB_ENABLE_PREDICT", str(obbff.ENABLE_PREDICT))
        console.print("")

    @log_start_end(log=logger)
    def call_thoughts(self, _):
        """Process thoughts command"""
        obbff.ENABLE_THOUGHTS_DAY = not obbff.ENABLE_THOUGHTS_DAY
        set_key(
            obbff.ENV_FILE,
            "OPENBB_ENABLE_THOUGHTS_DAY",
            str(obbff.ENABLE_THOUGHTS_DAY),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_reporthtml(self, _):
        """Process reporthtml command"""
        obbff.OPEN_REPORT_AS_HTML = not obbff.OPEN_REPORT_AS_HTML
        set_key(
            obbff.ENV_FILE,
            "OPENBB_OPEN_REPORT_AS_HTML",
            str(obbff.OPEN_REPORT_AS_HTML),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_exithelp(self, _):
        """Process exithelp command"""
        obbff.ENABLE_EXIT_AUTO_HELP = not obbff.ENABLE_EXIT_AUTO_HELP
        set_key(
            obbff.ENV_FILE,
            "OPENBB_ENABLE_EXIT_AUTO_HELP",
            str(obbff.ENABLE_EXIT_AUTO_HELP),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_rcontext(self, _):
        """Process rcontext command"""
        obbff.REMEMBER_CONTEXTS = not obbff.REMEMBER_CONTEXTS
        set_key(
            obbff.ENV_FILE,
            "OPENBB_REMEMBER_CONTEXTS",
            str(obbff.REMEMBER_CONTEXTS),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_dt(self, _):
        """Process dt command"""
        obbff.USE_DATETIME = not obbff.USE_DATETIME
        set_key(obbff.ENV_FILE, "OPENBB_USE_DATETIME", str(obbff.USE_DATETIME))
        console.print("")

    @log_start_end(log=logger)
    def call_rich(self, _):
        """Process rich command"""
        obbff.ENABLE_RICH = not obbff.ENABLE_RICH
        set_key(obbff.ENV_FILE, "OPENBB_ENABLE_RICH", str(obbff.ENABLE_RICH))
        console.print("")

    @log_start_end(log=logger)
    def call_richpanel(self, _):
        """Process richpanel command"""
        obbff.ENABLE_RICH_PANEL = not obbff.ENABLE_RICH_PANEL
        set_key(
            obbff.ENV_FILE,
            "OPENBB_ENABLE_RICH_PANEL",
            str(obbff.ENABLE_RICH_PANEL),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_ion(self, _):
        """Process ion command"""
        obbff.USE_ION = not obbff.USE_ION
        set_key(obbff.ENV_FILE, "OPENBB_USE_ION", str(obbff.USE_ION))
        console.print("")

    @log_start_end(log=logger)
    def call_watermark(self, _):
        """Process watermark command"""
        obbff.USE_WATERMARK = not obbff.USE_WATERMARK
        set_key(obbff.ENV_FILE, "OPENBB_USE_WATERMARK", str(obbff.USE_WATERMARK))
        console.print("")

    @log_start_end(log=logger)
    def call_cmdloc(self, _):
        """Process cmdloc command"""
        obbff.USE_CMD_LOCATION_FIGURE = not obbff.USE_CMD_LOCATION_FIGURE
        set_key(
            obbff.ENV_FILE,
            "OPENBB_USE_CMD_LOCATION_FIGURE",
            str(obbff.USE_CMD_LOCATION_FIGURE),
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
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
        ns_parser = parse_known_args_and_warn(parser, other_args)
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
        languages_i18n = os.path.join(
            os.path.dirname(os.path.abspath(os.path.dirname(__file__))), "i18n"
        )
        languages_available = [
            lang.strip(".yml")
            for lang in os.listdir(languages_i18n)
            if lang.endswith(".yml")
        ]

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
            choices=languages_available,
            required=True,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            set_key(obbff.ENV_FILE, "OPENBB_USE_LANGUAGE", str(ns_parser.value))
            obbff.USE_LANGUAGE = ns_parser.value
            console.print("")
