""" Parameters Controller Module """
__docformat__ = "numpy"

# pylint: disable=C0302, no-else-return

import argparse
import configparser
import logging
import os
from pathlib import Path
from typing import List, Optional

from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as gtff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import parse_known_args_and_warn, log_and_raise
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio.portfolio_optimization.parameters import params_view
from openbb_terminal.portfolio.portfolio_optimization.parameters.params_view import (
    AVAILABLE_OPTIONS,
    DEFAULT_PARAMETERS,
    MODEL_PARAMS,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


def check_save_file(file: str) -> str:
    """Argparse type to check parameter file to be saved"""
    if file == "defaults.ini":
        log_and_raise(
            argparse.ArgumentTypeError(
                "Cannot overwrite defaults.ini file, please save with a different name"
            )
        )
    else:
        if not file.endswith(".ini") and not file.endswith(".xlsx"):
            log_and_raise(
                argparse.ArgumentTypeError("File to be saved needs to be .ini or .xlsx")
            )

    return file


class ParametersController(BaseController):
    """Portfolio Optimization Parameters Controller class"""

    CHOICES_COMMANDS = [
        "set",
        "file",
        "save",
        "new",
        "clear",
        "arg",
    ]
    CHOICES_PARAMS = ["freq", "threshold", "method", "alpha", "maxnan"]
    CHOICES_COMMANDS += CHOICES_PARAMS

    PATH = "/portfolio/po/params/"

    models = [
        "maxsharpe",
        "minrisk",
        "maxutil",
        "maxret",
        "maxdiv",
        "maxdecorr",
        "ef",
        "riskparity",
        "relriskparity",
        "hrp",
        "herc",
        "nco",
    ]

    current_model = ""
    current_file = ""
    params = configparser.RawConfigParser()

    def __init__(
        self,
        file: str,
        queue: List[str] = None,
        params=None,
        current_model=None,
    ):
        """Constructor"""
        super().__init__(queue)

        self.current_file = file
        self.current_model = current_model
        self.description: Optional[str] = None
        self.DEFAULT_PATH = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__),
                "..",
                "..",
                "..",
                "..",
                "portfolio",
                "optimization",
            )
        )

        self.file_types = ["xlsx", "ini"]
        self.DATA_FILES = {
            filepath.name: filepath
            for file_type in self.file_types
            for filepath in Path(self.DEFAULT_PATH).rglob(f"*.{file_type}")
            if filepath.is_file()
        }

        if params:
            self.params = params
        else:
            pass
            # TODO: Enable .ini reading
            # self.params.read(
            #     os.path.join(
            #         self.DEFAULT_PATH,
            #         self.current_file if self.current_file else "defaults.ini",
            #     )
            # )
            # self.params.optionxform = str  # type: ignore
            # self.params = self.params["OPENBB"]

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["set"] = {c: None for c in self.models}
            choices["set"]["-m"] = {c: None for c in self.models}
            choices["arg"] = {c: None for c in AVAILABLE_OPTIONS}
            choices["file"] = {c: None for c in self.DATA_FILES}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = f"""
[info]Portfolio Risk Parameters (.ini or .xlsx)[/info]

[param]Loaded file:[/param] {self.current_file} [cmds]

    file             load portfolio risk parameters
    save             save portfolio risk parameters to specified file[/cmds]

[param]Model of interest:[/param] {self.current_model} [cmds]

    clear            clear model of interest from filtered parameters
    set              set model of interest to filter parameters
    arg              set a different value for an argument[/cmds]
"""
        if self.current_model:
            max_len = max(len(k) for k in self.params.keys())
            help_text += "\n[info]Parameters:[/info]\n"
            for k, v in self.params.items():
                all_params = DEFAULT_PARAMETERS + MODEL_PARAMS[self.current_model]
                if k in all_params:
                    help_text += (
                        f"    [param]{k}{' ' * (max_len - len(k))} :[/param] {v}\n"
                    )
        else:
            max_len = max(len(k) for k in self.params.keys())
            help_text += "\n[info]Parameters:[/info]\n"
            for k, v in self.params.items():
                help_text += f"    [param]{k}{' ' * (max_len - len(k))} :[/param] {v}\n"

        console.print(
            text=help_text, menu="Portfolio - Portfolio Optimization - Parameters"
        )

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.current_file:
            if self.current_model:
                return [
                    "portfolio",
                    "po",
                    f"file {self.current_file}",
                    "params",
                    f"set {self.current_model}",
                ]
            else:
                return ["portfolio", "po", f"file {self.current_file}", "params"]
        return []

    @log_start_end(log=logger)
    def call_file(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="file",
            description="Load portfolio risk parameters (ini or xlsx)",
        )

        parser.add_argument(
            "-f",
            "--file",
            required="-h" not in other_args,
            nargs="+",
            dest="file",
            help="Parameter file to be used",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            self.current_file = " ".join(ns_parser.file)

            if self.current_file in self.DATA_FILES:
                file_location = str(self.DATA_FILES[self.current_file])
            else:
                file_location = str(self.current_file)

            self.params, self.current_model = params_view.load_file(file_location)

            console.print()

    @log_start_end(log=logger)
    def call_save(self, other_args: List[str]):
        """Process save command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="save",
            description="Save portfolio risk parameters (ini or xlsx)",
        )
        parser.add_argument(
            "-f",
            "--file",
            required=True,
            type=check_save_file,
            dest="file",
            help="Filename to be saved",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.file.endswith(".ini"):
                # Create file if it does not exist
                filepath = os.path.abspath(
                    os.path.join(
                        os.path.dirname(__file__),
                        ".",
                        "portfolio",
                        "optimization",
                        ns_parser.file,
                    )
                )
                Path(filepath)

                with open(filepath, "w") as configfile:
                    self.params.write(configfile)

                self.current_file = ns_parser.file
                console.print()

            elif ns_parser.file.endswith(".xlsx"):
                console.print("It is not yet possible to save to .xlsx")

    @log_start_end(log=logger)
    def call_clear(self, other_args: List[str]):
        """Process set command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="clear",
            description="Clear selected portfolio optimization models",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            self.current_model = ""
            console.print("")

    @log_start_end(log=logger)
    def call_set(self, other_args: List[str]):
        """Process set command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="set",
            description="Select one of the portfolio optimization models",
        )
        parser.add_argument(
            "-m",
            "--model",
            required=True,
            dest="model",
            help="Frequency used to calculate returns",
            choices=self.models,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-m")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.current_model = ns_parser.model
            console.print("")

    @log_start_end(log=logger)
    def call_arg(self, other_args: List[str]):
        """Process arg command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="arg",
            description="Set a different value for one of the available arguments.",
        )

        parser.add_argument(
            "-a",
            "--argument",
            nargs=2,
            dest="argument",
            help="Set a value for an argument",
        )

        parser.add_argument(
            "-s",
            "--show_arguments",
            dest="show",
            action="store_true",
            default=False,
            help="Show the available arguments, the options and a description.",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-a")
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if ns_parser.show:
                params_view.show_arguments(AVAILABLE_OPTIONS, self.description)

            if ns_parser.argument:
                argument = ns_parser.argument[0]
                value = ns_parser.argument[1]

                if self.current_model:
                    if argument not in self.params:
                        console.print(
                            "[red]The parameter you are trying to access is unused in this model.[/red]\n"
                        )

                try:
                    value = float(value)
                except ValueError:
                    pass

                if argument == "historic_period":
                    for option in AVAILABLE_OPTIONS[argument]:
                        if option in str(value):
                            self.params[argument] = value
                            break
                    if self.params[argument] != value:
                        console.print(
                            f"[red]The value {value} is not an option for {argument}.\n"
                            f"Please select enter a "
                            f"number before the option d, w, mo and y or select ytd or max. For example: 252d, "
                            f"12w, 10y or max[/red]"
                        )
                elif (
                    value in AVAILABLE_OPTIONS[argument]
                    or "Any" in AVAILABLE_OPTIONS[argument]
                ):
                    self.params[argument] = value
                else:
                    if len(AVAILABLE_OPTIONS[argument]) > 15:
                        minimum = min(AVAILABLE_OPTIONS[argument])
                        maximum = max(AVAILABLE_OPTIONS[argument])
                        options = (
                            f"between {minimum} and {maximum} in steps of "
                            f"{maximum / sum(x > 0 for x in AVAILABLE_OPTIONS[argument])}"
                        )
                    else:
                        options = AVAILABLE_OPTIONS[argument]

                    console.print(
                        f"[red]The value {value} is not an option for {argument}.\n"
                        f"The value needs to be {options}[/red]"
                    )

            console.print()
