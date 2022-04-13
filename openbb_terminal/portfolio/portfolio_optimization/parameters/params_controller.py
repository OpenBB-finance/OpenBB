""" Parameters Controller Module """
__docformat__ = "numpy"

# pylint: disable=C0302

import os
import argparse
import logging
from typing import List
import configparser
from pathlib import Path
from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as gtff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    check_non_negative,
    check_non_negative_float,
    get_rf,
    parse_known_args_and_warn,
    log_and_raise
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio.portfolio_optimization import (
    optimizer_helper,
    optimizer_view,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)

def check_save_file(file: str) -> str:
    """Argparse type to check parameter file to be saved"""
    if file == "defaults.ini":
        log_and_raise(argparse.ArgumentTypeError(f"Cannot overwrite defaults.ini file, please save with a different name"))
    else:
        if not file.endswith(".ini") and not file.endswith(".xlsx"):
            log_and_raise(argparse.ArgumentTypeError(f"File to be saved needs to be .ini or .xlsx"))
    return file


class ParametersController(BaseController):
    """Portfolio Optimization Parameters Controller class"""

    CHOICES_COMMANDS = [
        "set",
        "load",
        "save",
        "new",
        "clear",
    ]
    CHOICES_PARAMS = [
        "freq",
        "threshold",
        "method",
        "alpha",
        "maxnan"
    ]
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

    model_params ={
        "maxsharpe": ["freq", "maxnan", "method", "risk_measure"],
        "minrisk": ["freq", "threshold", "method", "risk_measure", "alpha"],
    }

    current_model = ""
    current_file = ""
    params = configparser.RawConfigParser()

    def __init__(self, file: str, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.current_file = file
        
        self.params.read(os.path.join(os.path.dirname(__file__), self.current_file if self.current_file else "defaults.ini"))
        self.params.optionxform = str  # type: ignore

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["set"] = {c: None for c in self.models}
            choices["set"]["-m"] = {c: None for c in self.models}
            self.completer = NestedCompleter.from_nested_dict(choices)

    def print_help(self):
        """Print help"""
        help_text = f"""
[param]Loaded file:[/param] {self.current_file} [cmds]

[info]Portfolio Risk Parameters (.ini or .xlsx)[/info]
    load          load portfolio risk parameters
    save          save portfolio risk parameters to specified file[/cmds]

[param]Model of interest:[/param] {self.current_model} [cmds]
    clear         clear model of interest from filtered parameters
    set           set model of interest to filter parameters[/cmds]
"""
        if self.current_model:
            max_len = max([len(k) for k in self.params["OPENBB"].keys()])
            help_text += "\n[info]Parameters:[/info]\n"
            for k, v in self.params["OPENBB"].items():
                if k in self.model_params[self.current_model]:
                    help_text += f"    [param]{k}{' ' * (max_len-len(k))} :[/param] {v}\n"
        else:
            max_len = max([len(k) for k in self.params["OPENBB"].keys()])
            help_text += "\n[info]Parameters:[/info]\n"
            for k, v in self.params["OPENBB"].items():
                help_text += f"    [param]{k}{' ' * (max_len-len(k))} :[/param] {v}\n"
            
        console.print(text=help_text, menu="Portfolio - Portfolio Optimization - Parameters")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.current_file:
            if self.current_model:
                return ["portfolio", "po", f"file {self.current_file}", "params", f"set {self.current_model}"]
            else:
                return ["portfolio", "po", f"file {self.current_file}", "params"]
        return []

    @log_start_end(log=logger)
    def call_load(self, other_args: List[str]):
        """Process load command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="load",
            description="Load portfolio risk parameters (ini or xlsx)",
        )
        files_available = [f for f in os.listdir(os.path.dirname(__file__)) if (f.endswith(".ini") or f.endswith(".xlsx"))]
        parser.add_argument(
            "-f",
            "--file",
            required=True,
            dest="file",
            help="Parameter file to be used",
            choices=files_available,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = parse_known_args_and_warn(
            parser, other_args
        )
        if ns_parser:
            self.current_file = ns_parser.file
            console.print()

            if self.current_file.endswith(".ini"):
                self.params = configparser.RawConfigParser()
                self.params.read(os.path.join(os.path.dirname(__file__), ns_parser.file))
                self.params.optionxform = str  # type: ignore

                max_len = max([len(k) for k in self.params["OPENBB"].keys()])
                help_text = "[info]Parameters:[/info]\n"
                if self.current_model:
                    for k, v in self.params["OPENBB"].items():
                        if k in self.model_params[self.current_model]:
                            help_text += f"    [param]{k}{' ' * (max_len-len(k))} :[/param] {v}\n"
                else:
                    for k, v in self.params["OPENBB"].items():
                        help_text += f"    [param]{k}{' ' * (max_len-len(k))} :[/param] {v}\n"
                console.print(help_text)
            
            elif self.current_file.endswith(".xlsx"):
                # Jeroen to do for excel :D
                pass

            else:
                console.print("Should never get here!")
                

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args
        )
        if ns_parser:
            if ns_parser.file.endswith(".ini"):
                # Create file if it does not exist
                filepath = os.path.join(os.path.dirname(__file__), ns_parser.file)
                Path(filepath)

                with open(filepath, 'w') as configfile:
                    self.params.write(configfile)
                
                self.current_file = ns_parser.file
                console.print()

            elif ns_parser.file.endswith(".xlsx"):
                # To be done by Jer eheh
                pass
            else:
                console.print("Error, should never get here.")

    @log_start_end(log=logger)
    def call_clear(self, other_args: List[str]):
        """Process set command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="clear",
            description="Clear selected portfolio optimization models",
        )
        ns_parser = parse_known_args_and_warn(
            parser, other_args
        )
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
        ns_parser = parse_known_args_and_warn(
            parser, other_args
        )
        if ns_parser:
            self.current_model = ns_parser.model
            console.print("")

    # From here one allow to alter ALL model params

    @log_start_end(log=logger)
    def call_maxnan(self, other_args: List[str]):
        """Process maxnan command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="maxnan",
            description="Explain what this maxnan argument is",
        )
        # Jeroen to get from xlsx
        parser.add_argument(
            "-v",
            "--value",
            required="-h" not in other_args,
            type=check_non_negative_float,
            dest="value",
            help="Get description from xlsx",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-v")
        ns_parser = parse_known_args_and_warn(
            parser, other_args
        )
        if ns_parser:
            if self.current_model:
                if "maxnan" not in self.params["OPENBB"]:
                    console.print("[red]The parameter you are trying to access is unused in this model.[/red]\n")
                    return
                self.params["OPENBB"]["maxnan"] = str(ns_parser.value)
                console.print("")
                return
            else:
                self.params["OPENBB"]["maxnan"] = str(ns_parser.value)
            console.print("")
