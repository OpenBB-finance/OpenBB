"""Settings Controller Module"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
import argparse
import logging
from typing import List

# IMPORTATION THIRDPARTY
from dotenv import load_dotenv, set_key
from prompt_toolkit.completion import NestedCompleter

# IMPORTATION INTERNAL
from openbb_terminal import config_plot as cfg_plot
from openbb_terminal import feature_flags as obbff
from openbb_terminal.core.config.constants import ENV_FILE
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import get_flair, parse_known_args_and_warn
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console

# pylint: disable=too-many-lines,no-member,too-many-public-methods,C0302
# pylint:disable=import-outside-toplevel

logger = logging.getLogger(__name__)

if ENV_FILE.is_file():
    load_dotenv(ENV_FILE)


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
        help_text = "\n[info]Feature flags through environment variables:[/info]\n\n"
        color = "green" if obbff.LOG_COLLECTION else "red"
        help_text += f"   [{color}]logcollection    allow logs to be sent[/{color}]\n\n"
        color = "green" if obbff.USE_TABULATE_DF else "red"
        help_text += (
            f"   [{color}]tab              use tabulate to print dataframes[/{color}]\n"
        )
        color = "green" if obbff.USE_CLEAR_AFTER_CMD else "red"
        help_text += (
            f"   [{color}]cls              clear console after each command[/{color}]\n"
        )
        color = "green" if obbff.USE_COLOR else "red"
        help_text += f"   [{color}]color            use coloring features[/{color}]\n"
        color = "green" if obbff.USE_PROMPT_TOOLKIT else "red"
        help_text += f"   [{color}]promptkit        enable prompt toolkit (autocomplete and history)[/{color}]\n"
        color = "green" if obbff.ENABLE_PREDICT else "red"
        help_text += f"   [{color}]predict          prediction features[/{color}]\n"
        color = "green" if obbff.ENABLE_THOUGHTS_DAY else "red"
        help_text += f"   [{color}]thoughts         thoughts of the day[/{color}]\n"
        color = "green" if obbff.OPEN_REPORT_AS_HTML else "red"
        help_text += f"   [{color}]reporthtml       open report as HTML otherwise notebook[/{color}]\n"
        color = "green" if obbff.ENABLE_EXIT_AUTO_HELP else "red"
        help_text += f"   [{color}]exithelp         automatically print help when quitting menu[/{color}]\n"
        color = "green" if obbff.REMEMBER_CONTEXTS else "red"
        help_text += f"   [{color}]rcontext         remember contexts loaded params during session[/{color}]\n"
        color = "green" if obbff.ENABLE_RICH else "red"
        help_text += f"   [{color}]rich             colorful rich terminal[/{color}]\n"
        color = "green" if obbff.ENABLE_RICH_PANEL else "red"
        help_text += (
            f"   [{color}]richpanel        colorful rich terminal panel[/{color}]\n"
        )
        color = "green" if obbff.USE_ION else "red"
        help_text += (
            f"   [{color}]ion              interactive matplotlib mode[/{color}]\n"
        )
        color = "green" if obbff.USE_WATERMARK else "red"
        help_text += f"   [{color}]watermark        watermark in figures[/{color}]\n"
        color = "green" if obbff.USE_CMD_LOCATION_FIGURE else "red"
        help_text += f"   [{color}]cmdloc           command location displayed in figures[/{color}]\n"
        color = "green" if obbff.USE_PLOT_AUTOSCALING else "red"
        help_text += f"   [{color}]autoscaling      plot autoscaling[/{color}]\n\n"
        color = "green" if obbff.USE_DATETIME else "red"
        help_text += f"   [{color}]dt               add date and time to command line[/{color}]\n"
        help_text += "[cmds]   flair            console flair[/cmds]\n\n"
        help_text += f"[param]USE_FLAIR:[/param]  {get_flair()}\n\n[cmds]"
        help_text += "   dpi              dots per inch\n"
        help_text += (
            "   backend          plotting backend (None, tkAgg, MacOSX, Qt5Agg)\n"
        )
        help_text += "[unvl]" if obbff.USE_PLOT_AUTOSCALING else ""
        help_text += "   height           select plot height\n"
        help_text += "   width            select plot width\n"
        help_text += "[/unvl]" if obbff.USE_PLOT_AUTOSCALING else ""
        help_text += "[unvl]" if not obbff.USE_PLOT_AUTOSCALING else ""
        help_text += "   pheight          select plot percentage height\n"
        help_text += "   pwidth           select plot percentage width\n"
        help_text += (
            "   monitor          which monitor to display (primary: 0, secondary: 1)\n"
        )
        help_text += "[/unvl]" if not obbff.USE_PLOT_AUTOSCALING else ""
        help_text += "[/cmds]\n"
        help_text += f"[param]PLOT_DPI:[/param]                 {cfg_plot.PLOT_DPI}\n"
        help_text += f"[param]BACKEND:[/param]                  {cfg_plot.BACKEND}\n"
        help_text += (
            f"[param]PLOT_HEIGHT:[/param]              {cfg_plot.PLOT_HEIGHT}\n"
        )
        help_text += f"[param]PLOT_WIDTH:[/param]               {cfg_plot.PLOT_WIDTH}\n"
        help_text += f"[param]PLOT_HEIGHT_PERCENTAGE:[/param]   {cfg_plot.PLOT_HEIGHT_PERCENTAGE}%\n"
        help_text += f"[param]PLOT_WIDTH_PERCENTAGE:[/param]    {cfg_plot.PLOT_WIDTH_PERCENTAGE}%\n"
        help_text += f"[param]MONITOR:[/param]                  {cfg_plot.MONITOR}\n"

        # color = "green" if obbff.USE_FLAIR else "red"
        # help_text += f"   [{color}]cls        clear console after each command[/{color}]\n"

        console.print(text=help_text, menu="Settings")

    @log_start_end(log=logger)
    def call_logcollection(self, _):
        """Process logcollection command"""
        obbff.LOG_COLLECTION = not obbff.LOG_COLLECTION
        set_key(ENV_FILE, "OPENBB_LOG_COLLECTION", str(obbff.LOG_COLLECTION))
        console.print("")

    @log_start_end(log=logger)
    def call_tab(self, _):
        """Process tab command"""
        obbff.USE_TABULATE_DF = not obbff.USE_TABULATE_DF
        set_key(ENV_FILE, "OPENBB_USE_TABULATE_DF", str(obbff.USE_TABULATE_DF))
        console.print("")

    @log_start_end(log=logger)
    def call_cls(self, _):
        """Process cls command"""
        obbff.USE_CLEAR_AFTER_CMD = not obbff.USE_CLEAR_AFTER_CMD
        set_key(ENV_FILE, "OPENBB_USE_CLEAR_AFTER_CMD", str(obbff.USE_CLEAR_AFTER_CMD))
        console.print("")

    @log_start_end(log=logger)
    def call_color(self, _):
        """Process color command"""
        obbff.USE_COLOR = not obbff.USE_COLOR
        set_key(ENV_FILE, "OPENBB_USE_COLOR", str(obbff.USE_COLOR))
        console.print("")

    @log_start_end(log=logger)
    def call_promptkit(self, _):
        """Process promptkit command"""
        obbff.USE_PROMPT_TOOLKIT = not obbff.USE_PROMPT_TOOLKIT
        set_key(ENV_FILE, "OPENBB_USE_PROMPT_TOOLKIT", str(obbff.USE_PROMPT_TOOLKIT))
        console.print("")

    @log_start_end(log=logger)
    def call_predict(self, _):
        """Process predict command"""
        obbff.ENABLE_PREDICT = not obbff.ENABLE_PREDICT
        set_key(ENV_FILE, "OPENBB_ENABLE_PREDICT", str(obbff.ENABLE_PREDICT))
        console.print("")

    @log_start_end(log=logger)
    def call_thoughts(self, _):
        """Process thoughts command"""
        obbff.ENABLE_THOUGHTS_DAY = not obbff.ENABLE_THOUGHTS_DAY
        set_key(ENV_FILE, "OPENBB_ENABLE_THOUGHTS_DAY", str(obbff.ENABLE_THOUGHTS_DAY))
        console.print("")

    @log_start_end(log=logger)
    def call_reporthtml(self, _):
        """Process reporthtml command"""
        obbff.OPEN_REPORT_AS_HTML = not obbff.OPEN_REPORT_AS_HTML
        set_key(ENV_FILE, "OPENBB_OPEN_REPORT_AS_HTML", str(obbff.OPEN_REPORT_AS_HTML))
        console.print("")

    @log_start_end(log=logger)
    def call_exithelp(self, _):
        """Process exithelp command"""
        obbff.ENABLE_EXIT_AUTO_HELP = not obbff.ENABLE_EXIT_AUTO_HELP
        set_key(
            ENV_FILE,
            "OPENBB_ENABLE_EXIT_AUTO_HELP",
            str(obbff.ENABLE_EXIT_AUTO_HELP),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_rcontext(self, _):
        """Process rcontext command"""
        obbff.REMEMBER_CONTEXTS = not obbff.REMEMBER_CONTEXTS
        set_key(ENV_FILE, "OPENBB_REMEMBER_CONTEXTS", str(obbff.REMEMBER_CONTEXTS))
        console.print("")

    @log_start_end(log=logger)
    def call_dt(self, _):
        """Process dt command"""
        obbff.USE_DATETIME = not obbff.USE_DATETIME
        set_key(ENV_FILE, "OPENBB_USE_DATETIME", str(obbff.USE_DATETIME))
        console.print("")

    @log_start_end(log=logger)
    def call_rich(self, _):
        """Process rich command"""
        obbff.ENABLE_RICH = not obbff.ENABLE_RICH
        set_key(ENV_FILE, "OPENBB_ENABLE_RICH", str(obbff.ENABLE_RICH))
        console.print("")

    @log_start_end(log=logger)
    def call_richpanel(self, _):
        """Process richpanel command"""
        obbff.ENABLE_RICH_PANEL = not obbff.ENABLE_RICH_PANEL
        set_key(ENV_FILE, "OPENBB_ENABLE_RICH_PANEL", str(obbff.ENABLE_RICH_PANEL))
        console.print("")

    @log_start_end(log=logger)
    def call_ion(self, _):
        """Process ion command"""
        obbff.USE_ION = not obbff.USE_ION
        set_key(ENV_FILE, "OPENBB_USE_ION", str(obbff.USE_ION))
        console.print("")

    @log_start_end(log=logger)
    def call_watermark(self, _):
        """Process watermark command"""
        obbff.USE_WATERMARK = not obbff.USE_WATERMARK
        set_key(ENV_FILE, "OPENBB_USE_WATERMARK", str(obbff.USE_WATERMARK))
        console.print("")

    @log_start_end(log=logger)
    def call_cmdloc(self, _):
        """Process cmdloc command"""
        obbff.USE_CMD_LOCATION_FIGURE = not obbff.USE_CMD_LOCATION_FIGURE
        set_key(
            ENV_FILE,
            "OPENBB_USE_CMD_LOCATION_FIGURE",
            str(obbff.USE_CMD_LOCATION_FIGURE),
        )
        console.print("")

    @log_start_end(log=logger)
    def call_autoscaling(self, _):
        """Process autoscaling command"""
        obbff.USE_PLOT_AUTOSCALING = not obbff.USE_PLOT_AUTOSCALING
        set_key(
            ENV_FILE,
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
            set_key(ENV_FILE, "OPENBB_PLOT_DPI", str(ns_parser.value))
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
            set_key(ENV_FILE, "OPENBB_PLOT_HEIGHT", str(ns_parser.value))
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
            set_key(ENV_FILE, "OPENBB_PLOT_WIDTH", str(ns_parser.value))
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
            set_key(ENV_FILE, "OPENBB_PLOT_HEIGHT_PERCENTAGE", str(ns_parser.value))
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
            set_key(ENV_FILE, "OPENBB_PLOT_WIDTH_PERCENTAGE", str(ns_parser.value))
            cfg_plot.PLOT_WIDTH_PERCENTAGE = ns_parser.value
            console.print("")

    @log_start_end(log=logger)
    def call_monitor(self, other_args: List[str]):
        """Process pwidth command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="pwidth",
            description="choose which monitor to scale: 0-primary, 1-seconday (autoscaling enabled)",
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
            set_key(ENV_FILE, "OPENBB_MONITOR", str(ns_parser.value))
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
            set_key(ENV_FILE, "OPENBB_BACKEND", str(ns_parser.value))
            if ns_parser.value == "None":
                cfg_plot.BACKEND = None  # type: ignore
            else:
                cfg_plot.BACKEND = ns_parser.value
            console.print("")
