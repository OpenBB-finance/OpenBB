"""Settings Controller Module"""
__docformat__ = "numpy"

import argparse
import logging
import os
from pathlib import Path
from typing import List

import dotenv
from prompt_toolkit.completion import NestedCompleter

from gamestonk_terminal import config_plot as cfg_plot
from gamestonk_terminal import feature_flags as gtff
from gamestonk_terminal.decorators import log_start_end
from gamestonk_terminal.helper_funcs import get_flair, parse_known_args_and_warn
from gamestonk_terminal.menu import session
from gamestonk_terminal.parent_classes import BaseController
from gamestonk_terminal.rich_config import console

# pylint: disable=too-many-lines,no-member,too-many-public-methods,C0302

logger = logging.getLogger(__name__)
# pylint:disable=import-outside-toplevel


class SettingsController(BaseController):
    """Settings Controller class"""

    CHOICES_COMMANDS: List[str] = [
        "tab",
        "cls",
        "color",
        "flair",
        "dt",
        "ion",
        "watermark",
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
    env_file = ".env"
    env_files = [f for f in os.listdir() if f.endswith(".env")]
    if env_files:
        env_file = env_files[0]
        dotenv.load_dotenv(env_file)
    else:
        # create env file
        Path(".env")

    def __init__(self, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = "\n[info]Feature flags through environment variables:[/info]\n"
        color = "green" if gtff.USE_TABULATE_DF else "red"
        help_text += (
            f"   [{color}]tab              use tabulate to print dataframes[/{color}]\n"
        )
        color = "green" if gtff.USE_CLEAR_AFTER_CMD else "red"
        help_text += (
            f"   [{color}]cls              clear console after each command[/{color}]\n"
        )
        color = "green" if gtff.USE_PROMPT_TOOLKIT else "red"
        help_text += f"   [{color}]promptkit        enable prompt toolkit (autocomplete and history)[/{color}]\n"
        color = "green" if gtff.ENABLE_PREDICT else "red"
        help_text += f"   [{color}]predict          prediction features[/{color}]\n"
        color = "green" if gtff.ENABLE_THOUGHTS_DAY else "red"
        help_text += f"   [{color}]thoughts         thoughts of the day[/{color}]\n"
        color = "green" if gtff.OPEN_REPORT_AS_HTML else "red"
        help_text += f"   [{color}]reporthtml       open report as HTML otherwise notebook[/{color}]\n"
        color = "green" if gtff.ENABLE_EXIT_AUTO_HELP else "red"
        help_text += f"   [{color}]exithelp         automatically print help when quitting menu[/{color}]\n"
        color = "green" if gtff.REMEMBER_CONTEXTS else "red"
        help_text += f"   [{color}]rcontext         remember contexts loaded params during session[/{color}]\n"
        color = "green" if gtff.ENABLE_RICH_PANEL else "red"
        help_text += (
            f"   [{color}]richpanel        colorful rich terminal panel[/{color}]\n"
        )
        color = "green" if gtff.USE_ION else "red"
        help_text += (
            f"   [{color}]ion              interactive matplotlib mode[/{color}]\n"
        )
        color = "green" if gtff.USE_WATERMARK else "red"
        help_text += f"   [{color}]watermark        watermark in figures[/{color}]\n"
        color = "green" if gtff.USE_PLOT_AUTOSCALING else "red"
        help_text += f"   [{color}]autoscaling      plot autoscaling[/{color}]\n\n"
        color = "green" if gtff.USE_DATETIME else "red"
        help_text += f"   [{color}]dt               add date and time to command line[/{color}]\n"
        help_text += "[cmds]   flair            console flair[/cmds]\n\n"
        help_text += f"[param]USE_FLAIR:[/param]  {get_flair()}\n\n[cmds]"
        help_text += "   dpi              dots per inch\n"
        help_text += (
            "   backend          plotting backend (None, tkAgg, MacOSX, Qt5Agg)\n"
        )
        help_text += "[unvl]" if gtff.USE_PLOT_AUTOSCALING else ""
        help_text += "   height           select plot height\n"
        help_text += "   width            select plot width\n"
        help_text += "[/unvl]" if gtff.USE_PLOT_AUTOSCALING else ""
        help_text += "[unvl]" if not gtff.USE_PLOT_AUTOSCALING else ""
        help_text += "   pheight          select plot percentage height\n"
        help_text += "   pwidth           select plot percentage width\n"
        help_text += (
            "   monitor          which monitor to display (primary: 0, secondary: 1)\n"
        )
        help_text += "[/unvl]" if not gtff.USE_PLOT_AUTOSCALING else ""
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

        # color = "green" if gtff.USE_FLAIR else "red"
        # help_text += f"   [{color}]cls        clear console after each command[/{color}]\n"

        console.print(text=help_text, menu="Settings")

    @log_start_end(log=logger)
    def call_tab(self, _):
        """Process tab command"""
        gtff.USE_TABULATE_DF = not gtff.USE_TABULATE_DF
        dotenv.set_key(self.env_file, "GTFF_USE_TABULATE_DF", str(gtff.USE_TABULATE_DF))
        console.print("")

    @log_start_end(log=logger)
    def call_cls(self, _):
        """Process cls command"""
        gtff.USE_CLEAR_AFTER_CMD = not gtff.USE_CLEAR_AFTER_CMD
        dotenv.set_key(
            self.env_file, "GTFF_USE_CLEAR_AFTER_CMD", str(gtff.USE_CLEAR_AFTER_CMD)
        )
        console.print("")

    @log_start_end(log=logger)
    def call_promptkit(self, _):
        """Process promptkit command"""
        gtff.USE_PROMPT_TOOLKIT = not gtff.USE_PROMPT_TOOLKIT
        dotenv.set_key(
            self.env_file, "GTFF_USE_PROMPT_TOOLKIT", str(gtff.USE_PROMPT_TOOLKIT)
        )
        console.print("")

    @log_start_end(log=logger)
    def call_predict(self, _):
        """Process predict command"""
        gtff.ENABLE_PREDICT = not gtff.ENABLE_PREDICT
        dotenv.set_key(self.env_file, "GTFF_ENABLE_PREDICT", str(gtff.ENABLE_PREDICT))
        console.print("")

    @log_start_end(log=logger)
    def call_thoughts(self, _):
        """Process thoughts command"""
        gtff.ENABLE_THOUGHTS_DAY = not gtff.ENABLE_THOUGHTS_DAY
        dotenv.set_key(
            self.env_file, "GTFF_ENABLE_THOUGHTS_DAY", str(gtff.ENABLE_THOUGHTS_DAY)
        )
        console.print("")

    @log_start_end(log=logger)
    def call_reporthtml(self, _):
        """Process reporthtml command"""
        gtff.OPEN_REPORT_AS_HTML = not gtff.OPEN_REPORT_AS_HTML
        dotenv.set_key(
            self.env_file, "GTFF_OPEN_REPORT_AS_HTML", str(gtff.OPEN_REPORT_AS_HTML)
        )
        console.print("")

    @log_start_end(log=logger)
    def call_exithelp(self, _):
        """Process exithelp command"""
        gtff.ENABLE_EXIT_AUTO_HELP = not gtff.ENABLE_EXIT_AUTO_HELP
        dotenv.set_key(
            self.env_file, "GTFF_ENABLE_EXIT_AUTO_HELP", str(gtff.ENABLE_EXIT_AUTO_HELP)
        )
        console.print("")

    @log_start_end(log=logger)
    def call_rcontext(self, _):
        """Process rcontext command"""
        gtff.REMEMBER_CONTEXTS = not gtff.REMEMBER_CONTEXTS
        dotenv.set_key(
            self.env_file, "GTFF_REMEMBER_CONTEXTS", str(gtff.REMEMBER_CONTEXTS)
        )
        console.print("")

    @log_start_end(log=logger)
    def call_dt(self, _):
        """Process dt command"""
        gtff.USE_DATETIME = not gtff.USE_DATETIME
        dotenv.set_key(self.env_file, "GTFF_USE_DATETIME", str(gtff.USE_DATETIME))
        console.print("")

    @log_start_end(log=logger)
    def call_richpanel(self, _):
        """Process richpanel command"""
        gtff.ENABLE_RICH_PANEL = not gtff.ENABLE_RICH_PANEL
        dotenv.set_key(
            self.env_file, "GTFF_ENABLE_RICH_PANEL", str(gtff.ENABLE_RICH_PANEL)
        )
        console.print("")

    @log_start_end(log=logger)
    def call_ion(self, _):
        """Process ion command"""
        gtff.USE_ION = not gtff.USE_ION
        dotenv.set_key(self.env_file, "GTFF_USE_ION", str(gtff.USE_ION))
        console.print("")

    @log_start_end(log=logger)
    def call_watermark(self, _):
        """Process watermark command"""
        gtff.USE_WATERMARK = not gtff.USE_WATERMARK
        dotenv.set_key(self.env_file, "GTFF_USE_WATERMARK", str(gtff.USE_WATERMARK))
        console.print("")

    @log_start_end(log=logger)
    def call_autoscaling(self, _):
        """Process autoscaling command"""
        gtff.USE_PLOT_AUTOSCALING = not gtff.USE_PLOT_AUTOSCALING
        dotenv.set_key(
            self.env_file, "GTFF_USE_PLOT_AUTOSCALING", str(gtff.USE_PLOT_AUTOSCALING)
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
            dotenv.set_key(self.env_file, "GTFF_PLOT_DPI", str(ns_parser.value))
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
            dotenv.set_key(self.env_file, "GTFF_PLOT_HEIGHT", str(ns_parser.value))
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
            dotenv.set_key(self.env_file, "GTFF_PLOT_WIDTH", str(ns_parser.value))
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
            dotenv.set_key(
                self.env_file, "GTFF_PLOT_HEIGHT_PERCENTAGE", str(ns_parser.value)
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
            dotenv.set_key(
                self.env_file, "GTFF_PLOT_WIDTH_PERCENTAGE", str(ns_parser.value)
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
            dotenv.set_key(self.env_file, "GTFF_MONITOR", str(ns_parser.value))
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
            dotenv.set_key(self.env_file, "GTFF_BACKEND", str(ns_parser.value))
            if ns_parser.value == "None":
                cfg_plot.BACKEND = None  # type: ignore
            else:
                cfg_plot.BACKEND = ns_parser.value
            console.print("")
