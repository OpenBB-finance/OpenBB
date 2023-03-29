# type: ignore
""" Parameters Controller Module """
__docformat__ = "numpy"
# pylint: disable=C0302, no-else-return

import argparse
import logging
from typing import List, Optional

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.custom_prompt_toolkit import NestedCompleter
from openbb_terminal.decorators import log_start_end
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio.portfolio_optimization.parameters import (
    params_helpers,
    params_view,
)
from openbb_terminal.portfolio.portfolio_optimization.parameters.params_statics import (
    AVAILABLE_OPTIONS,
    DEFAULT_BOOL,
    DEFAULT_PARAMETERS,
    MODEL_PARAMS,
)
from openbb_terminal.rich_config import MenuText, console

logger = logging.getLogger(__name__)


class ParametersController(BaseController):
    """Portfolio Optimization Parameters Controller class"""

    CHOICES_COMMANDS = [
        "set",
        "load",
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

    def __init__(
        self,
        file: str,
        queue: Optional[List[str]] = None,
        params: Optional[dict] = None,
        current_model=None,
    ):
        """Constructor"""
        super().__init__(queue)

        self.params: dict = params if params else {}
        self.current_file = file
        self.current_model = current_model
        self.description: Optional[str] = None
        self.DATA_FILES = params_helpers.load_data_files()

        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["set"] = {c: None for c in self.models}
            choices["set"]["--model"] = {c: None for c in self.models}
            choices["set"]["-m"] = "--model"
            choices["arg"] = {c: None for c in AVAILABLE_OPTIONS}
            choices["load"] = {c: {} for c in self.DATA_FILES}
            choices["load"]["--file"] = {c: {} for c in self.DATA_FILES}
            choices["load"]["-f"] = "--file"
            choices["save"]["--file"] = None
            choices["save"]["-f"] = "--file"
            choices["arg"] = {
                "--argument": None,
                "-a": "--argument",
                "--show_arguments": {},
                "-s": "--show_arguments",
            }
            self.choices = choices
            self.completer = NestedCompleter.from_nested_dict(choices)

    def update_runtime_choices(self):
        if session and get_current_user().preferences.USE_PROMPT_TOOLKIT:
            self.DATA_FILES = params_helpers.load_data_files()
            self.choices["load"]["--file"] = {c: {} for c in self.DATA_FILES}
            self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help"""
        mt = MenuText("portfolio/po/params/")
        mt.add_param("_loaded", self.current_file)
        mt.add_raw("\n")
        mt.add_cmd("load")
        mt.add_cmd("save")
        mt.add_raw("\n")
        mt.add_param("_model", self.current_model or "")
        mt.add_raw("\n")
        mt.add_cmd("clear", self.current_file)
        mt.add_cmd("set", self.current_file)
        mt.add_cmd("arg", self.current_file)
        if self.current_file:
            mt.add_raw("\n")
            mt.add_info("_parameters_")
            if self.current_model:
                max_len = max(len(k) for k in self.params)
                for k, v in self.params.items():
                    v = params_helpers.booltostr(v)
                    all_params = DEFAULT_PARAMETERS + MODEL_PARAMS[self.current_model]
                    if k in all_params:
                        mt.add_raw(
                            f"    [param]{k}{' ' * (max_len - len(k))} :[/param] {v}\n"
                        )
            else:
                max_len = max(len(k) for k in self.params)
                for k, v in self.params.items():
                    v = params_helpers.booltostr(v)
                    mt.add_raw(
                        f"    [param]{k}{' ' * (max_len - len(k))} :[/param] {v}\n"
                    )
        console.print(
            text=mt.menu_text, menu="Portfolio - Portfolio Optimization - Parameters"
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
    def call_load(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="file",
            description="Select parameter file to use (ini or xlsx). The OpenBB Parameters Template can be "
            "found inside the Portfolio Optimization documentation. Please type `about` to access the documentation.",
        )

        parser.add_argument(
            "-f",
            "--file",
            nargs="+",
            dest="file",
            help="Parameter file to be used",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if not ns_parser.file:
                console.print(
                    "[green]The OpenBB Parameters Template can be found inside "
                    "the Portfolio Optimization documentation. Please type `about` "
                    "to access the documentation. [green]\n"
                )
            else:
                self.current_file = " ".join(ns_parser.file)

                if self.current_file in self.DATA_FILES:
                    file_location = str(self.DATA_FILES[self.current_file])
                else:
                    file_location = str(self.current_file)

                self.params, self.current_model = params_view.load_file(file_location)

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
            type=params_helpers.check_save_file,
            dest="file",
            help="Filename to be saved",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.current_file = str(params_view.save_file(ns_parser.file, self.params))

        self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_clear(self, other_args: List[str]):
        """Process set command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="clear",
            description="Clear selected portfolio optimization models",
        )
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            self.current_model = ""

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
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if not self.current_file:
                console.print(
                    "[red]Load portfolio risk parameters first using `file`.\n[/red]"
                )
                return
            self.current_model = ns_parser.model

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
        ns_parser = self.parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if not self.current_file:
                console.print(
                    "[red]Load portfolio risk parameters first using `file`.\n[/red]"
                )
                return
            if self.current_file.endswith(".ini"):
                console.print(
                    f"Please adjust the parameters directly in the {self.current_file} file."
                )
            elif ns_parser.show:
                params_view.show_arguments(AVAILABLE_OPTIONS, self.description)

            elif ns_parser.argument:
                argument = ns_parser.argument[0]
                value = ns_parser.argument[1]

                if self.current_model and argument not in self.params:
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
                    if AVAILABLE_OPTIONS[argument] == DEFAULT_BOOL:
                        value = value == "True"
                    self.params[argument] = value
                else:
                    options = ", ".join(AVAILABLE_OPTIONS[argument])
                    if len(AVAILABLE_OPTIONS[argument]) > 15:
                        minimum = min(AVAILABLE_OPTIONS[argument])
                        maximum = max(AVAILABLE_OPTIONS[argument])
                        options = (
                            f"between {minimum} and {maximum} in steps of "
                            f"{maximum / sum(x > 0 for x in AVAILABLE_OPTIONS[argument])}"
                        )

                        console.print(
                            f"[red]The value {value} is not an option for {argument}.\n"
                            f"The value needs to be {options}[/red]"
                        )

                    else:
                        self.params[argument] = str(AVAILABLE_OPTIONS[argument])  # type: ignore

            console.print()
