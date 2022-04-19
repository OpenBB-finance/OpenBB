""" Parameters Controller Module """
__docformat__ = "numpy"

# pylint: disable=C0302

import argparse
import configparser
import logging
import os
from pathlib import Path
from typing import List

from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as gtff
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    parse_known_args_and_warn,
    log_and_raise
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio.portfolio_optimization import (
    excel_model
)
from openbb_terminal.portfolio.portfolio_optimization.parameters import params_view
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


def check_save_file(file: str) -> str:
    """Argparse type to check parameter file to be saved"""
    if file == "defaults.ini":
        log_and_raise(
            argparse.ArgumentTypeError(f"Cannot overwrite defaults.ini file, please save with a different name"))
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
        "arg",
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

    DEFAULT_RANGE = [value / 1000 for value in range(0, 1001)]

    AVAILABLE_OPTIONS = {
        "historic_period": ["d", "w", "mo", "y", "ytd", "max"],
        "start_period": ["Any"],
        "end_period": ["Any"],
        "log_returns": ['0', '1'],
        "return_frequency": ["d", "w", "m"],
        "max_nan": DEFAULT_RANGE,
        "threshold_value": DEFAULT_RANGE,
        "nan_fill_method": ["linear", "time", "nearest", "zero", "slinear", "quadratic", "cubic"],
        "risk_free": DEFAULT_RANGE,
        "significance_level": DEFAULT_RANGE,
        "risk_measure": ["MV", "MAD", "MSV", "FLPM", "SLPM", "CVaR", "EVaR", "WR", "ADD", "UCI", "CDaR", "EDaR", "MDD"],
        "target_return": DEFAULT_RANGE + [-x for x in DEFAULT_RANGE],
        "target_risk": DEFAULT_RANGE + [-x for x in DEFAULT_RANGE],
        "expected_return": ["hist", "ewma1", "ewma2"],
        "covariance": ["hist", "ewma1", "ewma2", "ledoit", "oas", "shrunk", "gl", "jlogo", "fixed", "spectral",
                       "shrink"],
        "smoothing_factor_ewma": DEFAULT_RANGE,
        "long_allocation": DEFAULT_RANGE,
        "short_allocation": DEFAULT_RANGE,
        "risk_aversion": [value / 100 for value in range(-500, 501)],
        "amount_portfolios": range(1, 10001),
        "random_seed": range(1, 10001),
        "tangency": ["0", "1"],
        "risk_parity_model": ['A', 'B', 'C'],
        "penal_factor": DEFAULT_RANGE + [-x for x in DEFAULT_RANGE],
        "co_dependence": ["pearson", "spearman", "abs_pearson", "abs_spearman", "distance", "mutual_info", "tail"],
        "cvar_simulations": range(1, 10001),
        "cvar_significance": DEFAULT_RANGE,
        "linkage": ["single", "complete", "average", "weighted", "centroid", "ward", "dbht"],
        "max_clusters": range(1, 101),
        "amount_bins": ["KN", "FD", "SC", "HGR", "Integer"],
        "alpha_tail": DEFAULT_RANGE,
        "leaf_order": ['0', '1'],
        "objective": ["MinRisk", "Utility", "Sharpe", "MaxRet"]
    }

    DEFAULT_PARAMETERS = ['historic_period', 'start_period', 'end_period', 'log_returns', 'return_frequency',
                          'max_nan', 'threshold_value', 'nan_fill_method', 'risk_free', 'significance_level']
    MODEL_PARAMS = {
        "maxsharpe": ["risk_measure", "target_return", "target_risk", "expected_return", "covariance",
                      "smoothing_factor_ewma", "long_allocation", "short_allocation"],
        "minrisk": ["risk_measure", "target_return", "target_risk", "expected_return", "covariance",
                    "smoothing_factor_ewma", "long_allocation", "short_allocation"],
        "maxutil": ["risk_measure", "target_return", "target_risk", "expected_return", "covariance",
                    "smoothing_factor_ewma", "long_allocation", "short_allocation", "risk_aversion"],
        "maxret": ["risk_measure", "target_return", "target_risk", "expected_return", "covariance",
                   "smoothing_factor_ewma", "long_allocation"],
        "maxdiv": ["covariance", "long_allocation"],
        "maxdecorr": ["covariance", "long_allocation"],
        "ef": ["risk_measure", "long_allocation", "short_allocation", "amount_portfolios", "random_seed", "tangency"],
        "equal": ["risk_measure", "long_allocation"],
        "mktcap": ["risk_measure", "long_allocation"],
        "dividend": ["risk_measure", "long_allocation"],
        "riskparity": ["risk_measure", "target_return", "long_allocation", "risk_contribution"],
        "relriskparity": ["risk_measure", "covariance", "smoothing_factor_ewma", "long_allocation",
                          "risk_contribution", "risk_parity_model", "penal_factor"],
        "hrp": ["risk_measure", "covariance", "smoothing_factor_ewma", "long_allocation", "co_dependence",
                "cvar_simulations", "cvar_significance", "linkage", "amount_clusters", "max_clusters", "amount_bins",
                "alpha_tail", "leaf_order", "objective"],
        "herc": ["risk_measure", "covariance", "smoothing_factor_ewma", "long_allocation", "co_dependence",
                 "cvar_simulations", "cvar_significance", "linkage", "amount_clusters", "max_clusters", "amount_bins",
                 "alpha_tail", "leaf_order", "objective"],
        "nco": ["risk_measure", "covariance", "smoothing_factor_ewma", "long_allocation", "co_dependence",
                "cvar_simulations", "cvar_significance", "linkage", "amount_clusters", "max_clusters", "amount_bins",
                "alpha_tail", "leaf_order", "objective"],
    }

    current_model = ""
    current_file = ""
    params = configparser.RawConfigParser()

    def __init__(self, file: str, queue: List[str] = None):
        """Constructor"""
        super().__init__(queue)

        self.current_file = file
        self.description = None

        self.params.read(os.path.join(
            os.path.dirname(__file__), self.current_file if self.current_file else "defaults.ini"))
        self.params.optionxform = str  # type: ignore
        self.params = self.params['OPENBB']

        if session and gtff.USE_PROMPT_TOOLKIT:
            choices: dict = {c: {} for c in self.controller_choices}
            choices["set"] = {c: None for c in self.models}
            choices["set"]["-m"] = {c: None for c in self.models}
            choices["arg"] = {c: None for c in self.AVAILABLE_OPTIONS.keys()}
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
    set           set model of interest to filter parameters
    arg           set a different value for an argument[/cmds]
"""
        if self.current_model:
            max_len = max([len(k) for k in self.params.keys()])
            help_text += "\n[info]Parameters:[/info]\n"
            for k, v in self.params.items():
                all_params = self.DEFAULT_PARAMETERS + self.MODEL_PARAMS[self.current_model]
                if k in all_params:
                    help_text += f"    [param]{k}{' ' * (max_len - len(k))} :[/param] {v}\n"
        else:
            max_len = max([len(k) for k in self.params.keys()])
            help_text += "\n[info]Parameters:[/info]\n"
            for k, v in self.params.items():
                help_text += f"    [param]{k}{' ' * (max_len - len(k))} :[/param] {v}\n"

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

        parser.add_argument(
            "-f",
            "--file",
            required=True,
            nargs="+",
            dest="file",
            help="Parameter file to be used"
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = parse_known_args_and_warn(
            parser, other_args
        )

        if ns_parser:
            self.current_file = " ".join(ns_parser.file)
            console.print(self.current_file)

            console.print()

            if self.current_file.endswith(".ini"):
                self.params = configparser.RawConfigParser()
                self.params.read(os.path.join(os.path.dirname(__file__), self.current_file))
                self.params.optionxform = str  # type: ignore
                self.params = self.params['OPENBB']

            elif self.current_file.endswith(".xlsx"):
                self.params, self.description = excel_model.load_configuration(
                    os.path.join(os.path.dirname(__file__), self.current_file))
                self.current_model = self.params['technique']
            else:
                console.print("Can not load in the file due to not being an .ini or .xlsx file.")
                pass

            max_len = max([len(k) for k in self.params.keys()])
            help_text = "[info]Parameters:[/info]\n"
            if self.current_model:
                for k, v in self.params.items():
                    all_params = self.DEFAULT_PARAMETERS + self.MODEL_PARAMS[self.current_model]
                    if k in all_params:
                        help_text += f"    [param]{k}{' ' * (max_len - len(k))} :[/param] {v}\n"
            else:
                for k, v in self.params.items():
                    help_text += f"    [param]{k}{' ' * (max_len - len(k))} :[/param] {v}\n"

            console.print(help_text)

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
                console.print("It is not yet possible to save to .xlsx")
                pass

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
        ns_parser = parse_known_args_and_warn(
            parser, other_args
        )
        if ns_parser:
            if ns_parser.show:
                params_view.show_arguments(self.AVAILABLE_OPTIONS, self.description)

            if ns_parser.argument:
                argument = ns_parser.argument[0]
                value = ns_parser.argument[1]

                if self.current_model:
                    if argument not in self.params:
                        console.print("[red]The parameter you are trying to access is unused in this model.[/red]\n")

                try:
                    value = float(value)
                except ValueError:
                    pass

                if argument == "historic_period":
                    for option in self.AVAILABLE_OPTIONS[argument]:
                        if option in str(value):
                            self.params[argument] = str(value)
                            break
                    if self.params[argument] != str(value):
                        console.print(
                            f"[red]The value {value} is not an option for {argument}.\n" f"Please select enter a "
                            f"number before the option d, w, mo and y or select ytd or max. For example: 252d, "
                            f"12w, 10y or max[/red]")
                elif value in self.AVAILABLE_OPTIONS[argument] or "Any" in self.AVAILABLE_OPTIONS[argument]:
                    self.params[argument] = str(value)
                else:
                    if len(self.AVAILABLE_OPTIONS[argument]) > 15:
                        minimum = min(self.AVAILABLE_OPTIONS[argument])
                        maximum = max(self.AVAILABLE_OPTIONS[argument])
                        options = f"between {minimum} and {maximum} in steps of " \
                                  f"{maximum / sum(x > 0 for x in self.AVAILABLE_OPTIONS[argument])}"
                    else:
                        options = self.AVAILABLE_OPTIONS[argument]

                    console.print(f"[red]The value {value} is not an option for {argument}.\n"
                                  f"The value needs to be {options}[/red]")

            console.print()