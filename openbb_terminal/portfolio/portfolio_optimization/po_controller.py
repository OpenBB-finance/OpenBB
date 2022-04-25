""" Portfolio Optimization Controller Module """
__docformat__ = "numpy"

# pylint: disable=C0302, protected-access, too-many-instance-attributes

import argparse
import logging
import os
from pathlib import Path
from typing import List, Dict, Set

from prompt_toolkit.completion import NestedCompleter

from openbb_terminal import feature_flags as obbff
from openbb_terminal import parent_classes
from openbb_terminal.decorators import log_start_end
from openbb_terminal.helper_funcs import (
    check_non_negative,
    get_rf,
    parse_known_args_and_warn,
)
from openbb_terminal.menu import session
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.portfolio.portfolio_optimization import excel_model
from openbb_terminal.portfolio.portfolio_optimization import (
    optimizer_helper,
    optimizer_model,
    optimizer_view,
)
from openbb_terminal.portfolio.portfolio_optimization import yahoo_finance_model
from openbb_terminal.portfolio.portfolio_optimization.parameters import (
    params_controller,
    params_view,
)
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)


class PortfolioOptimizationController(BaseController):
    """Portfolio Optimization Controller class"""

    CHOICES_COMMANDS = [
        "select",
        "add",
        "rmv",
        "show",
        "rpf",
        "load",
        "plot",
        "equal",
        "mktcap",
        "dividend",
        "property",
        "maxsharpe",
        "minrisk",
        "maxutil",
        "maxret",
        "maxdiv",
        "maxdecorr",
        "blacklitterman",
        "riskparity",
        "relriskparity",
        "hrp",
        "herc",
        "nco",
        "ef",
        "yolo",
        "file",
        "params",
    ]

    period_choices = [
        "1d",
        "5d",
        "1mo",
        "3mo",
        "6mo",
        "1y",
        "2y",
        "5y",
        "10y",
        "ytd",
        "max",
    ]

    meanrisk_choices = [
        "MV",
        "MAD",
        "MSV",
        "FLPM",
        "SLPM",
        "CVaR",
        "EVaR",
        "WR",
        "ADD",
        "UCI",
        "CDaR",
        "EDaR",
        "MDD",
    ]

    riskparity_choices = [
        "MV",
        "MAD",
        "MSV",
        "FLPM",
        "SLPM",
        "CVaR",
        "EVaR",
        "CDaR",
        "EDaR",
        "UCI",
    ]

    relriskparity_choices = [
        "A",
        "B",
        "C",
    ]

    hcp_choices = [
        "MV",
        "MAD",
        "GMD",
        "MSV",
        "VaR",
        "CVaR",
        "TG",
        "EVaR",
        "RG",
        "CVRG",
        "TGRG",
        "WR",
        "FLPM",
        "SLPM",
        "MDD",
        "ADD",
        "DaR",
        "CDaR",
        "EDaR",
        "UCI",
        "MDD_Rel",
        "ADD_Rel",
        "DaR_Rel",
        "CDaR_Rel",
        "EDaR_Rel",
        "UCI_Rel",
    ]

    risk_choices = {
        "mv": "MV",
        "mad": "MAD",
        "gmd": "GMD",
        "msv": "MSV",
        "var": "VaR",
        "cvar": "CVaR",
        "tg": "TG",
        "evar": "EVaR",
        "rg": "RG",
        "cvrg": "CVRG",
        "tgrg": "TGRG",
        "wr": "WR",
        "flpm": "FLPM",
        "slpm": "SLPM",
        "mdd": "MDD",
        "add": "ADD",
        "dar": "DaR",
        "cdar": "CDaR",
        "edar": "EDaR",
        "uci": "UCI",
        "mdd_rel": "MDD_Rel",
        "add_rel": "ADD_Rel",
        "dar_rel": "DaR_Rel",
        "cdar_rel": "CDaR_Rel",
        "edar_rel": "EDaR_Rel",
        "uci_rel": "UCI_Rel",
    }
    mean_choices = [
        "hist",
        "ewma1",
        "ewma2",
    ]

    codependence_choices = [
        "pearson",
        "spearman",
        "abs_pearson",
        "abs_spearman",
        "distance",
        "mutual_info",
        "tail",
    ]

    covariance_choices = [
        "hist",
        "ewma1",
        "ewma2",
        "ledoit",
        "oas",
        "shrunk",
        "gl",
        "jlogo",
        "fixed",
        "spectral",
        "shrink",
    ]

    objective_choices = [
        "MinRisk",
        "Utility",
        "Sharpe",
        "MaxRet",
    ]

    nco_objective_choices = [
        "MinRisk",
        "Utility",
        "Sharpe",
        "ERC",
    ]

    linkage_choices = [
        "single",
        "complete",
        "average",
        "weighted",
        "centroid",
        "median",
        "ward",
        "dbht",
    ]

    bins_choices = [
        "KN",
        "FD",
        "SC",
        "HGR",
    ]

    freq_choices = [
        "d",
        "w",
        "m",
    ]

    method_choices = [
        "linear",
        "time",
        "nearest",
        "zero",
        "slinear",
        "quadratic",
        "cubic",
        "barycentric",
    ]

    PATH = "/portfolio/po/"

    files_available: List = list()

    def __init__(
        self,
        tickers: List[str] = None,
        portfolios: Dict = None,
        categories: Dict = None,
        queue: List[str] = None,
    ):
        """Constructor"""
        super().__init__(queue)
        self.current_model = None

        if tickers:
            self.tickers = list(set(tickers))
            self.tickers.sort()
        else:
            self.tickers = list()

        if portfolios:
            self.portfolios = dict(portfolios)
        else:
            self.portfolios = dict()

        if categories:
            self.categories = dict(categories)
        else:
            self.categories = dict()

        self.count = 0

        models = [
            "maxsharpe",
            "minrisk",
            "maxutil",
            "maxret",
            "maxdiv",
            "maxdecorr",
            "blacklitterman",
            "ef",
            "riskparity",
            "relriskparity",
            "hrp",
            "herc",
            "nco",
        ]
        self.file_types = ["xlsx", "ini"]
        self.DEFAULT_ALLOCATION_PATH = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "portfolio", "allocation"
            )
        )

        self.DATA_ALLOCATION_FILES = {
            filepath.name: filepath
            for file_type in self.file_types
            for filepath in Path(self.DEFAULT_ALLOCATION_PATH).rglob(f"*.{file_type}")
            if filepath.is_file()
        }

        self.current_file = ""
        self.DEFAULT_OPTIMIZATION_PATH = os.path.abspath(
            os.path.join(
                os.path.dirname(__file__), "..", "..", "..", "portfolio", "optimization"
            )
        )
        self.DATA_OPTIMIZATION_FILES = {
            filepath.name: filepath
            for file_type in self.file_types
            for filepath in Path(self.DEFAULT_OPTIMIZATION_PATH).rglob(f"*.{file_type}")
            if filepath.is_file()
        }

        self.params: Dict = {}

        if session and obbff.USE_PROMPT_TOOLKIT:
            self.choices: dict = {c: {} for c in self.controller_choices}
            self.choices["property"]["-p"] = {
                c: None for c in yahoo_finance_model.yf_info_choices
            }
            self.choices["property"]["--property"] = {
                c: None for c in yahoo_finance_model.yf_info_choices
            }
            self.choices["file"] = {c: None for c in self.DATA_OPTIMIZATION_FILES}
            self.choices["load"] = {c: None for c in self.DATA_ALLOCATION_FILES}

            for fn in models:
                self.choices[fn]["-p"] = {c: None for c in self.period_choices}
                self.choices[fn]["--period"] = {c: None for c in self.period_choices}
                self.choices[fn]["-f"] = {c: None for c in self.freq_choices}
                self.choices[fn]["--freq"] = {c: None for c in self.freq_choices}
                self.choices[fn]["-mt"] = {c: None for c in self.method_choices}
                self.choices[fn]["--method"] = {c: None for c in self.method_choices}

            for fn in ["maxsharpe", "minrisk", "maxutil", "maxret", "ef"]:
                self.choices[fn]["-rm"] = {c: None for c in self.meanrisk_choices}
                self.choices[fn]["--risk-measure"] = {
                    c: None for c in self.meanrisk_choices
                }

            self.choices["riskparity"]["-rm"] = {
                c: None for c in self.riskparity_choices
            }
            self.choices["riskparity"]["--risk-measure"] = {
                c: None for c in self.riskparity_choices
            }
            self.choices["relriskparity"]["-ve"] = {
                c: None for c in self.riskparity_choices
            }
            self.choices["relriskparity"]["--version"] = {
                c: None for c in self.riskparity_choices
            }

            for fn in [
                "maxsharpe",
                "minrisk",
                "maxutil",
                "maxret",
                "riskparity",
                "relriskparity",
            ]:
                self.choices[fn]["-m"] = {c: None for c in self.mean_choices}
                self.choices[fn]["--mean"] = {c: None for c in self.mean_choices}
                self.choices[fn]["-cv"] = {c: None for c in self.covariance_choices}
                self.choices[fn]["--covariance"] = {
                    c: None for c in self.covariance_choices
                }

            for fn in ["maxdiv", "maxdecorr"]:
                self.choices[fn]["-cv"] = {c: None for c in self.covariance_choices}
                self.choices[fn]["--covariance"] = {
                    c: None for c in self.covariance_choices
                }

            for fn in ["hrp", "herc", "nco"]:
                self.choices[fn]["-rm"] = {c: None for c in self.hcp_choices}
                self.choices[fn]["--risk-measure"] = {c: None for c in self.hcp_choices}
                self.choices[fn]["-cd"] = {c: None for c in self.codependence_choices}
                self.choices[fn]["--codependence"] = {
                    c: None for c in self.codependence_choices
                }
                self.choices[fn]["-cv"] = {c: None for c in self.covariance_choices}
                self.choices[fn]["--covariance"] = {
                    c: None for c in self.covariance_choices
                }
                self.choices[fn]["-lk"] = {c: None for c in self.linkage_choices}
                self.choices[fn]["--linkage"] = {c: None for c in self.linkage_choices}
                self.choices[fn]["-bi"] = {c: None for c in self.bins_choices}
                self.choices[fn]["--bins-info"] = {c: None for c in self.bins_choices}

            self.choices["blacklitterman"]["-o"] = {
                c: None for c in self.objective_choices
            }
            self.choices["blacklitterman"]["--objective"] = {
                c: None for c in self.objective_choices
            }
            self.choices["nco"]["-o"] = {c: None for c in self.nco_objective_choices}
            self.choices["nco"]["--objective"] = {
                c: None for c in self.nco_objective_choices
            }
            self.completer = NestedCompleter.from_nested_dict(self.choices)

    def update_runtime_choices(self):
        if session and obbff.USE_PROMPT_TOOLKIT:
            if self.portfolios:
                self.choices["show"] = {c: None for c in list(self.portfolios.keys())}

        self.completer = NestedCompleter.from_nested_dict(self.choices)

    def print_help(self):
        """Print help"""
        help_text = f"""
[param]Parameter file: [/param] {self.current_file}[cmds]

    file          select portfolio parameter file[/cmds][menu]
>   params        specify and show portfolio risk parameters[/menu][cmds]
    load          load tickers and categories from .xlsx or .csv file[/cmds]

[param]Tickers: [/param]{('None', ', '.join(self.tickers))[bool(self.tickers)]}
[param]Categories: [/param]{('None', ', '.join(self.categories.keys()))[bool(self.categories.keys())]}
[param]Portfolios: [/param]{('None', ', '.join(self.portfolios.keys()))[bool(self.portfolios.keys())]}
[cmds]
    add           add tickers to the list of the tickers to be optimized
    rmv           remove tickers from the list of the tickers to be optimized
    show          show selected portfolios and categories from the list of saved portfolios
    rpf           remove portfolios from the list of saved portfolios[/cmds]

[info]Mean Risk Optimization:[/info][cmds]
    maxsharpe       maximal Sharpe ratio portfolio (a.k.a the tangency portfolio)
    minrisk         minimum risk portfolio
    maxutil         maximal risk averse utility function, given some risk
                    aversion parameter
    maxret          maximal return portfolio
    maxdiv          maximum diversification portfolio
    maxdecorr       maximum decorrelation portfolio
    blacklitterman  black litterman portfolio
    ef              show the efficient frontier[/cmds]

[info]Risk Parity Optimization:[/info][cmds]
    riskparity      risk parity portfolio using risk budgeting approach
    relriskparity   relaxed risk parity using least squares approach[/cmds]

[info]Hierarchical Clustering Models:[/info][cmds]
    hrp             hierarchical risk parity
    herc            hierarchical equal risk contribution
    nco	            nested clustering optimization[/cmds]

[info]Other Optimization Techniques:[/info][cmds]
    equal           equally weighted
    mktcap          weighted according to market cap (property marketCap)
    dividend        weighted according to dividend yield (property dividendYield)
    property        weight according to selected info property[/cmds]
    """
        console.print(text=help_text, menu="Portfolio - Portfolio Optimization")

    def custom_reset(self):
        """Class specific component of reset command"""
        if self.current_file:
            return ["portfolio", "po", f"file {self.current_file}"]
        return []

    @log_start_end(log=logger)
    def call_add(self, other_args: List[str]):
        """Add ticker or Select tickers for portfolio to be optimized"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="add/select",
            description="""Add/Select tickers for portfolio to be optimized.""",
        )
        parser.add_argument(
            "-t",
            "--tickers",
            dest="add_tickers",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            help="tickers to be used in the portfolio to optimize.",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            tickers: Set = set(self.tickers)
            for ticker in ns_parser.add_tickers:
                tickers.add(ticker)

            tickers_list: List = list(tickers)
            tickers_list.sort()
            self.tickers = tickers_list

            if self.tickers:
                console.print(
                    f"\nCurrent Tickers: {('None', ', '.join(tickers_list))[bool(tickers_list)]}"
                )

            console.print("")

    @log_start_end(log=logger)
    def call_rmv(self, other_args: List[str]):
        """Remove one of the tickers to be optimized"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rmv",
            description="""Remove one of the tickers to be optimized.""",
        )
        parser.add_argument(
            "-t",
            "--tickers",
            dest="rmv_tickers",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            help="tickers to be removed from the tickers to optimize.",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-t")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            tickers = set(self.tickers)
            for ticker in ns_parser.rmv_tickers:
                tickers.remove(ticker)

            self.tickers = list(tickers)
            self.tickers.sort()

            if self.tickers:
                console.print(
                    f"\nCurrent Tickers: {('None', ', '.join(tickers))[bool(tickers)]}"
                )

            console.print("")

    @log_start_end(log=logger)
    def call_file(self, other_args: List[str]):
        """Process file command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="file",
            description="Select parameter file to use",
        )

        parser.add_argument(
            "-f",
            "--file",
            required=True,
            nargs="+",
            dest="file",
            help="Parameter file to be used",
        )

        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            self.current_file = " ".join(ns_parser.file)

            if self.current_file in self.DATA_OPTIMIZATION_FILES:
                file_location = self.DATA_OPTIMIZATION_FILES[self.current_file]
            else:
                file_location = self.current_file  # type: ignore

            self.params, self.current_model = params_view.load_file(file_location)

    @log_start_end(log=logger)
    def call_params(self):
        """Process params command"""
        self.queue = self.load_class(
            params_controller.ParametersController,
            self.current_file,
            self.queue,
            self.params,
            self.current_model,
        )

        self.current_file = parent_classes.controllers[
            "/portfolio/po/params/"
        ].current_file
        self.current_model = parent_classes.controllers[
            "/portfolio/po/params/"
        ].current_model
        self.params = parent_classes.controllers["/portfolio/po/params/"].params

    @log_start_end(log=logger)
    def call_show(self, other_args: List[str]):
        """Show saved portfolios"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="show",
            description="""Show selected saved portfolios""",
        )
        parser.add_argument(
            "-pf",
            "--portfolios",
            dest="portfolios",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            help="Show selected saved portfolios",
        )
        parser.add_argument(
            "-ct",
            "--categories",
            dest="categories",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            help="Show selected categories",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-pf")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            portfolios = set(self.portfolios.keys())
            if not ns_parser.categories:
                categories = list(self.categories.keys())
            else:
                categories = ns_parser.categories

            flag = True
            for portfolio in ns_parser.portfolios:
                if portfolio in portfolios:
                    console.print("")
                    console.print("Portfolio - " + portfolio)
                    optimizer_view.display_weights(self.portfolios[portfolio])

                    for category in categories:
                        console.print("")
                        optimizer_view.display_categories(
                            weights=self.portfolios[portfolio],
                            categories=self.categories,
                            column=category,
                            title="Category - " + category.title(),
                        )
                    flag = False

            if flag:
                console.print(
                    f"\nCurrent Portfolios: {('None', ', '.join(portfolios))[bool(portfolios)]}"
                )
                console.print(
                    f"\nCurrent Categories: {('None', ', '.join(categories))[bool(categories)]}"
                )
            console.print("")

    @log_start_end(log=logger)
    def call_rpf(self, other_args: List[str]):
        """Remove one portfolio"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="rpf",
            description="""Remove one of the portfolios""",
        )
        parser.add_argument(
            "-pf",
            "--portfolios",
            dest="portfolios",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            help="portfolios to be removed from the saved portfolios",
        )
        if other_args:
            if "-" not in other_args[0]:
                other_args.insert(0, "-pf")

        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            portfolios = set(self.portfolios.keys())
            for portfolio in ns_parser.portfolios:
                if portfolio in portfolios:
                    self.portfolios.pop(portfolio)
                    portfolios.remove(portfolio)

            if self.portfolios:
                console.print(
                    f"\nCurrent Portfolios: {('None', ', '.join(portfolios))[bool(portfolios)]}"
                )

            self.update_runtime_choices()
            console.print("")

    @log_start_end(log=logger)
    def call_load(self, other_args: List[str]):
        """Load file with stocks tickers and categories"""
        parser = argparse.ArgumentParser(
            add_help=False,
            prog="load",
            description="""Load file of stocks tickers with optional categories""",
        )

        parser.add_argument(
            "-f",
            "--file",
            required=True,
            nargs="+",
            dest="file",
            help="Allocation file to be used",
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-f")
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            filename = " ".join(ns_parser.file)

            if filename in self.DATA_ALLOCATION_FILES:
                file_location = self.DATA_ALLOCATION_FILES[filename]
            else:
                file_location = filename  # type: ignore

            self.tickers, self.categories = excel_model.load_allocation(file_location)
            self.portfolios = dict()
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_plot(self, other_args: List[str]):
        """Process plot command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="plot",
            description="plot selected charts for portfolios",
        )
        parser.add_argument(
            "-pf",
            "--portfolios",
            type=lambda s: [str(item).upper() for item in s.split(",")],
            default=[],
            dest="portfolios",
            help="selected portfolios that will be plotted",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                    in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-rm",
            "--risk-measure",
            default="MV",
            dest="risk_measure",
            help="""Risk measure used to optimize the portfolio. Possible values are:
                    MV : Variance
                    MAD : Mean Absolute Deviation
                    MSV : Semi Variance (Variance of negative returns)
                    FLPM : First Lower Partial Moment
                    SLPM : Second Lower Partial Moment
                    CVaR : Conditional Value at Risk
                    EVaR : Entropic Value at Risk
                    WR : Worst Realization
                    ADD : Average Drawdown of uncompounded returns
                    UCI : Ulcer Index of uncompounded returns
                    CDaR : Conditional Drawdown at Risk of uncompounded returns
                    EDaR : Entropic Drawdown at Risk of uncompounded returns
                    MDD : Maximum Drawdown of uncompounded returns
                    """,
            choices=self.meanrisk_choices,
        )
        parser.add_argument(
            "-r",
            "--risk-free-rate",
            type=float,
            dest="risk_free",
            default=get_rf(),
            help="""Risk-free rate of borrowing/lending. The period of the
                risk-free rate must be annual""",
        )
        parser.add_argument(
            "-a",
            "--alpha",
            type=float,
            default=0.05,
            dest="significance_level",
            help="Significance level of CVaR, EVaR, CDaR and EDaR",
        )
        parser.add_argument(
            "-pi",
            "--pie",
            action="store_true",
            dest="pie",
            default=False,
            help="Display a pie chart for weights",
        )
        parser.add_argument(
            "-hi",
            "--hist",
            action="store_true",
            dest="hist",
            default=False,
            help="Display a histogram with risk measures",
        )
        parser.add_argument(
            "-dd",
            "--drawdown",
            action="store_true",
            dest="dd",
            default=False,
            help="Display a drawdown chart with risk measures",
        )
        parser.add_argument(
            "-rc",
            "--rc-chart",
            action="store_true",
            dest="rc_chart",
            default=False,
            help="Display a risk contribution chart for assets",
        )
        parser.add_argument(
            "-he",
            "--heat",
            action="store_true",
            dest="heat",
            default=False,
            help="Display a heatmap of correlation matrix with dendrogram",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 loaded tickers to calculate weights.\n"
                )
                return

            portfolios = ns_parser.portfolios
            stocks = []
            for i in portfolios:
                stocks += list(self.portfolios[i].keys())
            stocks = list(set(stocks))
            stocks.sort()

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            _, stock_returns = optimizer_model.get_equal_weights(
                stocks=stocks,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                value=1,
            )

            for i in portfolios:
                weights = self.portfolios[i]
                stocks = list(self.portfolios[i].keys())
                optimizer_view.additional_plots(
                    weights=weights,
                    stock_returns=stock_returns[stocks],
                    title_opt=i,
                    freq=parameters["return_frequency"],
                    risk_measure=parameters["risk_measure"].lower(),
                    risk_free_rate=parameters["risk_free"],
                    alpha=parameters["significance_level"],
                    a_sim=100,
                    beta=parameters["significance_level"],
                    b_sim=100,
                    pie=ns_parser.pie,
                    hist=ns_parser.hist,
                    dd=ns_parser.dd,
                    rc_chart=ns_parser.rc_chart,
                    heat=ns_parser.heat,
                    external_axes=None,
                )

    @log_start_end(log=logger)
    def call_equal(self, other_args: List[str]):
        """Process equal command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="equal",
            description="Returns an equally weighted portfolio",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-rm",
            "--risk-measure",
            default="MV",
            dest="risk_measure",
            help="""Risk measure used to optimize the portfolio. Possible values are:
                    MV : Variance
                    MAD : Mean Absolute Deviation
                    MSV : Semi Variance (Variance of negative returns)
                    FLPM : First Lower Partial Moment
                    SLPM : Second Lower Partial Moment
                    CVaR : Conditional Value at Risk
                    EVaR : Entropic Value at Risk
                    WR : Worst Realization
                    ADD : Average Drawdown of uncompounded returns
                    UCI : Ulcer Index of uncompounded returns
                    CDaR : Conditional Drawdown at Risk of uncompounded returns
                    EDaR : Entropic Drawdown at Risk of uncompounded returns
                    MDD : Maximum Drawdown of uncompounded returns
                    """,
            choices=self.meanrisk_choices,
        )
        parser.add_argument(
            "-r",
            "--risk-free-rate",
            type=float,
            dest="risk_free",
            default=get_rf(),
            help="""Risk-free rate of borrowing/lending. The period of the
                risk-free rate must be annual""",
        )
        parser.add_argument(
            "-a",
            "--alpha",
            type=float,
            default=0.05,
            dest="significance_level",
            help="Significance level of CVaR, EVaR, CDaR and EDaR",
        )
        parser.add_argument(
            "-v",
            "--value",
            default=1,
            type=float,
            dest="long_allocation",
            help="Amount to allocate to portfolio",
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="EQUAL_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 loaded tickers to calculate weights.\n"
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_equal_weight(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                risk_measure=parameters["risk_measure"].lower(),
                risk_free_rate=parameters["risk_free"],
                alpha=parameters["significance_level"],
                value=parameters["long_allocation"],
            )
            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_mktcap(self, other_args: List[str]):
        """Process mktcap command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="mktcap",
            description="Returns a portfolio that is weighted based on Market Cap.",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-rm",
            "--risk-measure",
            default="MV",
            dest="risk_measure",
            help="""Risk measure used to optimize the portfolio. Possible values are:
                    MV : Variance
                    MAD : Mean Absolute Deviation
                    MSV : Semi Variance (Variance of negative returns)
                    FLPM : First Lower Partial Moment
                    SLPM : Second Lower Partial Moment
                    CVaR : Conditional Value at Risk
                    EVaR : Entropic Value at Risk
                    WR : Worst Realization
                    ADD : Average Drawdown of uncompounded returns
                    UCI : Ulcer Index of uncompounded returns
                    CDaR : Conditional Drawdown at Risk of uncompounded returns
                    EDaR : Entropic Drawdown at Risk of uncompounded returns
                    MDD : Maximum Drawdown of uncompounded returns
                    """,
            choices=self.meanrisk_choices,
        )
        parser.add_argument(
            "-r",
            "--risk-free-rate",
            type=float,
            dest="risk_free",
            default=get_rf(),
            help="""Risk-free rate of borrowing/lending. The period of the
                risk-free rate must be annual""",
        )
        parser.add_argument(
            "-a",
            "--alpha",
            type=float,
            default=0.05,
            dest="significance_level",
            help="Significance level of CVaR, EVaR, CDaR and EDaR",
        )
        parser.add_argument(
            "-v",
            "--value",
            default=1,
            type=float,
            dest="long_allocation",
            help="Amount to allocate to portfolio",
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="MKTCAP_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 stocks selected to perform calculations."
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_property_weighting(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                s_property="marketCap",
                risk_measure=parameters["risk_measure"].lower(),
                risk_free_rate=parameters["risk_free"],
                alpha=parameters["significance_level"],
                value=parameters["long_allocation"],
            )
            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_dividend(self, other_args: List[str]):
        """Process dividend command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="dividend",
            description="Returns a portfolio that is weighted based dividend yield.",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-rm",
            "--risk-measure",
            default="MV",
            dest="risk_measure",
            help="""Risk measure used to optimize the portfolio. Possible values are:
                    MV : Variance
                    MAD : Mean Absolute Deviation
                    MSV : Semi Variance (Variance of negative returns)
                    FLPM : First Lower Partial Moment
                    SLPM : Second Lower Partial Moment
                    CVaR : Conditional Value at Risk
                    EVaR : Entropic Value at Risk
                    WR : Worst Realization
                    ADD : Average Drawdown of uncompounded returns
                    UCI : Ulcer Index of uncompounded returns
                    CDaR : Conditional Drawdown at Risk of uncompounded returns
                    EDaR : Entropic Drawdown at Risk of uncompounded returns
                    MDD : Maximum Drawdown of uncompounded returns
                    """,
            choices=self.meanrisk_choices,
        )
        parser.add_argument(
            "-r",
            "--risk-free-rate",
            type=float,
            dest="risk_free",
            default=get_rf(),
            help="""Risk-free rate of borrowing/lending. The period of the
                risk-free rate must be annual""",
        )
        parser.add_argument(
            "-a",
            "--alpha",
            type=float,
            default=0.05,
            dest="significance_level",
            help="Significance level of CVaR, EVaR, CDaR and EDaR",
        )
        parser.add_argument(
            "-v",
            "--value",
            default=1,
            type=float,
            dest="long_allocation",
            help="Amount to allocate to portfolio",
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="DIVIDEND_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 stocks selected to perform calculations."
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_property_weighting(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                s_property="dividendYield",
                risk_measure=parameters["risk_measure"].lower(),
                risk_free_rate=parameters["risk_free"],
                alpha=parameters["significance_level"],
                value=parameters["long_allocation"],
            )
            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_property(self, other_args: List[str]):
        """Process property command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="property",
            description="Returns a portfolio that is weighted based on selected property.",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-pr",
            "--property",
            required=bool("-h" not in other_args),
            type=optimizer_helper.check_valid_property_type,
            dest="s_property",
            choices=yahoo_finance_model.yf_info_choices,
            help="""Property info to weight. Use one of yfinance info options.""",
        )
        parser.add_argument(
            "-rm",
            "--risk-measure",
            default="MV",
            dest="risk_measure",
            help="""Risk measure used to optimize the portfolio. Possible values are:
                    MV : Variance
                    MAD : Mean Absolute Deviation
                    MSV : Semi Variance (Variance of negative returns)
                    FLPM : First Lower Partial Moment
                    SLPM : Second Lower Partial Moment
                    CVaR : Conditional Value at Risk
                    EVaR : Entropic Value at Risk
                    WR : Worst Realization
                    ADD : Average Drawdown of uncompounded returns
                    UCI : Ulcer Index of uncompounded returns
                    CDaR : Conditional Drawdown at Risk of uncompounded returns
                    EDaR : Entropic Drawdown at Risk of uncompounded returns
                    MDD : Maximum Drawdown of uncompounded returns
                    """,
            choices=self.meanrisk_choices,
        )
        parser.add_argument(
            "-r",
            "--risk-free-rate",
            type=float,
            dest="risk_free",
            default=get_rf(),
            help="""Risk-free rate of borrowing/lending. The period of the
                risk-free rate must be annual""",
        )
        parser.add_argument(
            "-a",
            "--alpha",
            type=float,
            default=0.05,
            dest="significance_level",
            help="Significance level of CVaR, EVaR, CDaR and EDaR",
        )
        parser.add_argument(
            "-v",
            "--value",
            default=1,
            type=float,
            dest="long_allocation",
            help="Amount to allocate to portfolio",
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="PROPERTY_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)
        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 stocks selected to perform calculations."
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_property_weighting(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                s_property=parameters["s_property"],
                risk_measure=parameters["risk_measure"].lower(),
                risk_free_rate=parameters["risk_free"],
                alpha=parameters["significance_level"],
                value=parameters["long_allocation"],
            )
            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_maxsharpe(self, other_args: List[str]):
        """Process maxsharpe command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="maxsharpe",
            description="Maximizes the portfolio's return/risk ratio",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-rm",
            "--risk-measure",
            default="MV",
            dest="risk_measure",
            help="""Risk measure used to optimize the portfolio. Possible values are:
                    MV : Variance
                    MAD : Mean Absolute Deviation
                    MSV : Semi Variance (Variance of negative returns)
                    FLPM : First Lower Partial Moment
                    SLPM : Second Lower Partial Moment
                    CVaR : Conditional Value at Risk
                    EVaR : Entropic Value at Risk
                    WR : Worst Realization
                    ADD : Average Drawdown of uncompounded returns
                    UCI : Ulcer Index of uncompounded returns
                    CDaR : Conditional Drawdown at Risk of uncompounded returns
                    EDaR : Entropic Drawdown at Risk of uncompounded returns
                    MDD : Maximum Drawdown of uncompounded returns
                    """,
            choices=self.meanrisk_choices,
        )
        parser.add_argument(
            "-r",
            "--risk-free-rate",
            type=float,
            dest="risk_free",
            default=get_rf(),
            help="""Risk-free rate of borrowing/lending. The period of the
                risk-free rate must be annual""",
        )
        parser.add_argument(
            "-a",
            "--alpha",
            type=float,
            default=0.05,
            dest="significance_level",
            help="Significance level of CVaR, EVaR, CDaR and EDaR",
        )
        parser.add_argument(
            "-tr",
            "--target-return",
            dest="target_return",
            default=-1,
            help="Constraint on minimum level of portfolio's return",
        )
        parser.add_argument(
            "-tk",
            "--target-risk",
            dest="target_risk",
            default=-1,
            help="Constraint on maximum level of portfolio's risk",
        )
        parser.add_argument(
            "-m",
            "--mean",
            default="hist",
            dest="mean",
            help="Method used to estimate the expected return vector",
            choices=self.mean_choices,
        )
        parser.add_argument(
            "-cv",
            "--covariance",
            default="hist",
            dest="covariance",
            help="""Method used to estimate covariance matrix. Possible values are
                    hist: historical method
                    ewma1: exponential weighted moving average with adjust=True
                    ewma2: exponential weighted moving average with adjust=False
                    ledoit: Ledoit and Wolf shrinkage method
                    oas: oracle shrinkage method
                    shrunk: scikit-learn shrunk method
                    gl: graphical lasso method
                    jlogo: j-logo covariance
                    fixed: takes average of eigenvalues above max Marchenko Pastour limit
                    spectral:  makes zero eigenvalues above max Marchenko Pastour limit
                    shrink: Lopez de Prado's book shrinkage method
                    """,
            choices=self.covariance_choices,
        )
        parser.add_argument(
            "-de",
            "--d-ewma",
            type=float,
            default=0.94,
            dest="smoothing_factor_ewma",
            help="Smoothing factor for ewma estimators",
        )
        parser.add_argument(
            "-v",
            "--value",
            dest="long_allocation",
            help="Amount to allocate to portfolio in long positions",
            type=float,
            default=1.0,
        )
        parser.add_argument(
            "-vs",
            "--value-short",
            dest="short_allocation",
            help="Amount to allocate to portfolio in short positions",
            type=float,
            default=0.0,
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="MAXSHARPE_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 loaded tickers to calculate weights.\n"
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_max_sharpe(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                risk_measure=parameters["risk_measure"].lower(),
                risk_free_rate=parameters["risk_free"],
                alpha=parameters["significance_level"],
                target_return=parameters["target_return"],
                target_risk=parameters["target_risk"],
                mean=parameters["mean"].lower(),
                covariance=parameters["covariance"].lower(),
                d_ewma=parameters["smoothing_factor_ewma"],
                value=parameters["long_allocation"],
                value_short=parameters["short_allocation"],
            )
            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_minrisk(self, other_args: List[str]):
        """Process minrisk command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="minrisk",
            description="Minimizes portfolio's risk",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-rm",
            "--risk-measure",
            default="MV",
            dest="risk_measure",
            help="""Risk measure used to optimize the portfolio. Possible values are:
                    MV : Variance
                    MAD : Mean Absolute Deviation
                    MSV : Semi Variance (Variance of negative returns)
                    FLPM : First Lower Partial Moment
                    SLPM : Second Lower Partial Moment
                    CVaR : Conditional Value at Risk
                    EVaR : Entropic Value at Risk
                    WR : Worst Realization
                    ADD : Average Drawdown of uncompounded returns
                    UCI : Ulcer Index of uncompounded returns
                    CDaR : Conditional Drawdown at Risk of uncompounded returns
                    EDaR : Entropic Drawdown at Risk of uncompounded returns
                    MDD : Maximum Drawdown of uncompounded returns
                    """,
            choices=self.meanrisk_choices,
        )
        parser.add_argument(
            "-r",
            "--risk-free-rate",
            type=float,
            dest="risk_free",
            default=get_rf(),
            help="""Risk-free rate of borrowing/lending. The period of the
                risk-free rate must be annual""",
        )
        parser.add_argument(
            "-a",
            "--alpha",
            type=float,
            default=0.05,
            dest="significance_level",
            help="Significance level of CVaR, EVaR, CDaR and EDaR",
        )
        parser.add_argument(
            "-tr",
            "--target-return",
            dest="target_return",
            default=-1,
            help="Constraint on minimum level of portfolio's return",
        )
        parser.add_argument(
            "-tk",
            "--target-risk",
            dest="target_risk",
            default=-1,
            help="Constraint on maximum level of portfolio's risk",
        )
        parser.add_argument(
            "-m",
            "--mean",
            default="hist",
            dest="mean",
            help="Method used to estimate expected returns vector",
            choices=self.mean_choices,
        )
        parser.add_argument(
            "-cv",
            "--covariance",
            default="hist",
            dest="covariance",
            help="""Method used to estimate covariance matrix. Possible values are
                    hist: historical method
                    ewma1: exponential weighted moving average with adjust=True
                    ewma2: exponential weighted moving average with adjust=False
                    ledoit: Ledoit and Wolf shrinkage method
                    oas: oracle shrinkage method
                    shrunk: scikit-learn shrunk method
                    gl: graphical lasso method
                    jlogo: j-logo covariance
                    fixed: takes average of eigenvalues above max Marchenko Pastour limit
                    spectral:  makes zero eigenvalues above max Marchenko Pastour limit
                    shrink: Lopez de Prado's book shrinkage method
                    """,
            choices=self.covariance_choices,
        )
        parser.add_argument(
            "-de",
            "--d-ewma",
            type=float,
            default=0.94,
            dest="smoothing_factor_ewma",
            help="Smoothing factor for ewma estimators",
        )
        parser.add_argument(
            "-v",
            "--value",
            type=float,
            default=1.0,
            dest="long_allocation",
            help="Amount to allocate to portfolio in long positions",
        )
        parser.add_argument(
            "-vs",
            "--value-short",
            type=float,
            default=0.0,
            dest="short_allocation",
            help="Amount to allocate to portfolio in short positions",
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="MINRISK_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 loaded tickers to calculate weights.\n"
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_min_risk(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                risk_measure=parameters["risk_measure"].lower(),
                risk_free_rate=parameters["risk_free"],
                alpha=parameters["significance_level"],
                target_return=parameters["target_return"],
                target_risk=parameters["target_risk"],
                mean=parameters["mean"].lower(),
                covariance=parameters["covariance"].lower(),
                d_ewma=parameters["smoothing_factor_ewma"],
                value=parameters["long_allocation"],
                value_short=parameters["short_allocation"],
            )
            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_maxutil(self, other_args: List[str]):
        """Process maxutil command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="maxutil",
            description="Maximizes a risk averse utility function",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-rm",
            "--risk-measure",
            default="MV",
            dest="risk_measure",
            help="""Risk measure used to optimize the portfolio. Possible values are:
                    MV : Variance
                    MAD : Mean Absolute Deviation
                    MSV : Semi Variance (Variance of negative returns)
                    FLPM : First Lower Partial Moment
                    SLPM : Second Lower Partial Moment
                    CVaR : Conditional Value at Risk
                    EVaR : Entropic Value at Risk
                    WR : Worst Realization
                    ADD : Average Drawdown of uncompounded returns
                    UCI : Ulcer Index of uncompounded returns
                    CDaR : Conditional Drawdown at Risk of uncompounded returns
                    EDaR : Entropic Drawdown at Risk of uncompounded returns
                    MDD : Maximum Drawdown of uncompounded returns
                    """,
            choices=self.meanrisk_choices,
        )
        parser.add_argument(
            "-r",
            "--risk-free-rate",
            type=float,
            dest="risk_free",
            default=get_rf(),
            help="""Risk-free rate of borrowing/lending. The period of the
                risk-free rate must be annual""",
        )
        parser.add_argument(
            "-ra",
            "--risk-aversion",
            type=float,
            dest="risk_aversion",
            default=1.0,
            help="Risk aversion parameter",
        )
        parser.add_argument(
            "-a",
            "--alpha",
            type=float,
            default=0.05,
            dest="significance_level",
            help="Significance level of CVaR, EVaR, CDaR and EDaR",
        )
        parser.add_argument(
            "-tr",
            "--target-return",
            dest="target_return",
            default=-1,
            help="Constraint on minimum level of portfolio's return",
        )
        parser.add_argument(
            "-tk",
            "--target-risk",
            dest="target_risk",
            default=-1,
            help="Constraint on maximum level of portfolio's risk",
        )
        parser.add_argument(
            "-m",
            "--mean",
            default="hist",
            dest="mean",
            help="Method used to estimate the expected return vector",
            choices=self.mean_choices,
        )
        parser.add_argument(
            "-cv",
            "--covariance",
            default="hist",
            dest="covariance",
            help="""Method used to estimate covariance matrix. Possible values are
                    hist: historical method
                    ewma1: exponential weighted moving average with adjust=True
                    ewma2: exponential weighted moving average with adjust=False
                    ledoit: Ledoit and Wolf shrinkage method
                    oas: oracle shrinkage method
                    shrunk: scikit-learn shrunk method
                    gl: graphical lasso method
                    jlogo: j-logo covariance
                    fixed: takes average of eigenvalues above max Marchenko Pastour limit
                    spectral:  makes zero eigenvalues above max Marchenko Pastour limit
                    shrink: Lopez de Prado's book shrinkage method
                    """,
            choices=self.covariance_choices,
        )
        parser.add_argument(
            "-de",
            "--d-ewma",
            type=float,
            default=0.94,
            dest="smoothing_factor_ewma",
            help="Smoothing factor for ewma estimators",
        )
        parser.add_argument(
            "-v",
            "--value",
            dest="long_allocation",
            help="Amount to allocate to portfolio in long positions",
            type=float,
            default=1.0,
        )
        parser.add_argument(
            "-vs",
            "--value-short",
            dest="short_allocation",
            help="Amount to allocate to portfolio in short positions",
            type=float,
            default=0.0,
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="MAXUTIL_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 loaded tickers to calculate weights.\n"
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_max_util(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                risk_measure=parameters["risk_measure"].lower(),
                risk_free_rate=parameters["risk_free"],
                risk_aversion=parameters["risk_aversion"],
                alpha=parameters["significance_level"],
                target_return=parameters["target_return"],
                target_risk=parameters["target_risk"],
                mean=parameters["mean"].lower(),
                covariance=parameters["covariance"].lower(),
                d_ewma=parameters["smoothing_factor_ewma"],
                value=parameters["long_allocation"],
                value_short=parameters["short_allocation"],
            )
            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_maxret(self, other_args: List[str]):
        """Process maxret command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="maxret",
            description="Maximizes the portfolio's return ",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-rm",
            "--risk-measure",
            default="MV",
            dest="risk_measure",
            help="""Risk measure used to optimize the portfolio. Possible values are:
                    MV : Variance
                    MAD : Mean Absolute Deviation
                    MSV : Semi Variance (Variance of negative returns)
                    FLPM : First Lower Partial Moment
                    SLPM : Second Lower Partial Moment
                    CVaR : Conditional Value at Risk
                    EVaR : Entropic Value at Risk
                    WR : Worst Realization
                    ADD : Average Drawdown of uncompounded returns
                    UCI : Ulcer Index of uncompounded returns
                    CDaR : Conditional Drawdown at Risk of uncompounded returns
                    EDaR : Entropic Drawdown at Risk of uncompounded returns
                    MDD : Maximum Drawdown of uncompounded returns
                    """,
            choices=self.meanrisk_choices,
        )
        parser.add_argument(
            "-r",
            "--risk-free-rate",
            type=float,
            dest="risk_free",
            default=get_rf(),
            help="""Risk-free rate of borrowing/lending. The period of the
                risk-free rate must be annual""",
        )
        parser.add_argument(
            "-a",
            "--alpha",
            type=float,
            default=0.05,
            dest="significance_level",
            help="Significance level of CVaR, EVaR, CDaR and EDaR",
        )
        parser.add_argument(
            "-tr",
            "--target-return",
            dest="target_return",
            default=-1,
            help="Constraint on minimum level of portfolio's return",
        )
        parser.add_argument(
            "-tk",
            "--target-risk",
            dest="target_risk",
            default=-1,
            help="Constraint on maximum level of portfolio's risk",
        )
        parser.add_argument(
            "-m",
            "--mean",
            default="hist",
            dest="mean",
            help="Method used to estimate the expected return vector",
            choices=self.mean_choices,
        )
        parser.add_argument(
            "-cv",
            "--covariance",
            default="hist",
            dest="covariance",
            help="""Method used to estimate covariance matrix. Possible values are
                    hist: historical method
                    ewma1: exponential weighted moving average with adjust=True
                    ewma2: exponential weighted moving average with adjust=False
                    ledoit: Ledoit and Wolf shrinkage method
                    oas: oracle shrinkage method
                    shrunk: scikit-learn shrunk method
                    gl: graphical lasso method
                    jlogo: j-logo covariance
                    fixed: takes average of eigenvalues above max Marchenko Pastour limit
                    spectral:  makes zero eigenvalues above max Marchenko Pastour limit
                    shrink: Lopez de Prado's book shrinkage method
                    """,
            choices=self.covariance_choices,
        )
        parser.add_argument(
            "-de",
            "--d-ewma",
            type=float,
            default=0.94,
            dest="smoothing_factor_ewma",
            help="Smoothing factor for ewma estimators",
        )
        parser.add_argument(
            "-v",
            "--value",
            dest="long_allocation",
            help="Amount to allocate to portfolio in long positions",
            type=float,
            default=1.0,
        )
        parser.add_argument(
            "-vs",
            "--value-short",
            dest="short_allocation",
            help="Amount to allocate to portfolio in short positions",
            type=float,
            default=0.0,
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="MAXRET_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 loaded tickers to calculate weights.\n"
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_max_ret(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                risk_measure=parameters["risk_measure"].lower(),
                risk_free_rate=parameters["risk_free"],
                alpha=parameters["significance_level"],
                target_return=parameters["target_return"],
                target_risk=parameters["target_risk"],
                mean=parameters["mean"].lower(),
                covariance=parameters["covariance"].lower(),
                d_ewma=parameters["smoothing_factor_ewma"],
                value=parameters["long_allocation"],
                value_short=parameters["short_allocation"],
            )
            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_maxdiv(self, other_args: List[str]):
        """Process maxdiv command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="maxdiv",
            description="Maximizes the portfolio's diversification ratio",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-cv",
            "--covariance",
            default="hist",
            dest="covariance",
            help="""Method used to estimate covariance matrix. Possible values are
                    hist: historical method
                    ewma1: exponential weighted moving average with adjust=True
                    ewma2: exponential weighted moving average with adjust=False
                    ledoit: Ledoit and Wolf shrinkage method
                    oas: oracle shrinkage method
                    shrunk: scikit-learn shrunk method
                    gl: graphical lasso method
                    jlogo: j-logo covariance
                    fixed: takes average of eigenvalues above max Marchenko Pastour limit
                    spectral:  makes zero eigenvalues above max Marchenko Pastour limit
                    shrink: Lopez de Prado's book shrinkage method
                    """,
            choices=self.covariance_choices,
        )
        parser.add_argument(
            "-de",
            "--d-ewma",
            type=float,
            default=0.94,
            dest="smoothing_factor_ewma",
            help="Smoothing factor for ewma estimators",
        )
        parser.add_argument(
            "-v",
            "--value",
            dest="long_allocation",
            help="Amount to allocate to portfolio in long positions",
            type=float,
            default=1.0,
        )
        parser.add_argument(
            "-vs",
            "--value-short",
            dest="short_allocation",
            help="Amount to allocate to portfolio in short positions",
            type=float,
            default=0.0,
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="MAXDIV_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 loaded tickers to calculate weights.\n"
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_max_div(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                covariance=parameters["covariance"].lower(),
                d_ewma=parameters["smoothing_factor_ewma"],
                value=parameters["long_allocation"],
                value_short=parameters["short_allocation"],
            )
            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_maxdecorr(self, other_args: List[str]):
        """Process maxdecorr command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="maxdecorr",
            description="Maximizes the portfolio's decorrelation",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-cv",
            "--covariance",
            default="hist",
            dest="covariance",
            help="""Method used to estimate covariance matrix. Possible values are
                    hist: historical method
                    ewma1: exponential weighted moving average with adjust=True
                    ewma2: exponential weighted moving average with adjust=False
                    ledoit: Ledoit and Wolf shrinkage method
                    oas: oracle shrinkage method
                    shrunk: scikit-learn shrunk method
                    gl: graphical lasso method
                    jlogo: j-logo covariance
                    fixed: takes average of eigenvalues above max Marchenko Pastour limit
                    spectral:  makes zero eigenvalues above max Marchenko Pastour limit
                    shrink: Lopez de Prado's book shrinkage method
                    """,
            choices=self.covariance_choices,
        )
        parser.add_argument(
            "-de",
            "--d-ewma",
            type=float,
            default=0.94,
            dest="smoothing_factor_ewma",
            help="Smoothing factor for ewma estimators",
        )
        parser.add_argument(
            "-v",
            "--value",
            dest="long_allocation",
            help="Amount to allocate to portfolio in long positions",
            type=float,
            default=1.0,
        )
        parser.add_argument(
            "-vs",
            "--value-short",
            dest="short_allocation",
            help="Amount to allocate to portfolio in short positions",
            type=float,
            default=0.0,
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="MAXDECORR_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 loaded tickers to calculate weights.\n"
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_max_decorr(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                covariance=parameters["covariance"].lower(),
                d_ewma=parameters["smoothing_factor_ewma"],
                value=parameters["long_allocation"],
                value_short=parameters["short_allocation"],
            )
            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_blacklitterman(self, other_args: List[str]):
        """Process blacklitterman command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="blacklitterman",
            description="Optimize portfolio using Black Litterman estimates",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-bm",
            "--benchmark",
            type=str,
            default=None,
            dest="benchmark",
            help="portfolio name from current portfolio list",
        )
        parser.add_argument(
            "-o",
            "--objective",
            default="Sharpe",
            dest="objective",
            help="Objective function used to optimize the portfolio",
            choices=self.objective_choices,
        )
        parser.add_argument(
            "-pv",
            "--p-views",
            type=lambda s: [
                [float(item) for item in row.split(",")] for row in s.split(";")
            ],
            default=None,
            dest="p_views",
            help="matrix P of views",
        )
        parser.add_argument(
            "-qv",
            "--q-views",
            type=lambda s: [float(item) for item in s.split(",")],
            default=None,
            dest="q_views",
            help="matrix Q of views",
        )
        parser.add_argument(
            "-r",
            "--risk-free-rate",
            type=float,
            dest="risk_free",
            default=get_rf(),
            help="""Risk-free rate of borrowing/lending. The period of the
                risk-free rate must be annual""",
        )
        parser.add_argument(
            "-ra",
            "--risk-aversion",
            type=float,
            dest="risk_aversion",
            default=1.0,
            help="Risk aversion parameter",
        )
        parser.add_argument(
            "-d",
            "--delta",
            default=None,
            dest="delta",
            help="Risk aversion factor of Black Litterman model",
        )
        parser.add_argument(
            "-eq",
            "--equilibrium",
            action="store_true",
            default=True,
            dest="equilibrium",
            help="""If True excess returns are based on equilibrium market portfolio, if False
                excess returns are calculated as historical returns minus risk free rate.
                """,
        )
        parser.add_argument(
            "-op",
            "--optimize",
            action="store_false",
            default=True,
            dest="optimize",
            help="""If True Black Litterman estimates are used as inputs of mean variance model,
                if False returns equilibrium weights from Black Litterman model
                """,
        )
        parser.add_argument(
            "-v",
            "--value",
            type=float,
            default=1.0,
            dest="long_allocation",
            help="Amount to allocate to portfolio in long positions",
        )
        parser.add_argument(
            "-vs",
            "--value-short",
            type=float,
            default=0.0,
            dest="short_allocation",
            help="Amount to allocate to portfolio in short positions",
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="BL_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 loaded tickers to calculate weights.\n"
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_black_litterman(
                stocks=self.tickers,
                p_views=parameters["p_views"],
                q_views=parameters["q_views"],
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                benchmark=self.portfolios[ns_parser.benchmark].upper(),
                objective=parameters["objective"].lower(),
                risk_free_rate=parameters["risk_free"],
                risk_aversion=parameters["risk_aversion"],
                delta=ns_parser.delta,
                equilibrium=ns_parser.equilibrium,
                optimize=ns_parser.optimize,
                value=parameters["long_allocation"],
                value_short=parameters["short_allocation"],
            )

            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_ef(self, other_args):
        """Process ef command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="ef",
            description="""This function plots random portfolios based on their
                risk and returns and shows the efficient frontier.""",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-rm",
            "--risk-measure",
            default="MV",
            dest="risk_measure",
            help="""Risk measure used to optimize the portfolio. Possible values are:
                    MV : Variance
                    MAD : Mean Absolute Deviation
                    MSV : Semi Variance (Variance of negative returns)
                    FLPM : First Lower Partial Moment
                    SLPM : Second Lower Partial Moment
                    CVaR : Conditional Value at Risk
                    EVaR : Entropic Value at Risk
                    WR : Worst Realization
                    ADD : Average Drawdown of uncompounded returns
                    UCI : Ulcer Index of uncompounded returns
                    CDaR : Conditional Drawdown at Risk of uncompounded returns
                    EDaR : Entropic Drawdown at Risk of uncompounded returns
                    MDD : Maximum Drawdown of uncompounded returns
                    """,
            choices=self.meanrisk_choices,
        )
        parser.add_argument(
            "-r",
            "--risk-free-rate",
            type=float,
            dest="risk_free",
            default=get_rf(),
            help="""Risk-free rate of borrowing/lending. The period of the
                risk-free rate must be annual""",
        )
        parser.add_argument(
            "-a",
            "--alpha",
            type=float,
            default=0.05,
            dest="significance_level",
            help="Significance level of CVaR, EVaR, CDaR and EDaR",
        )
        parser.add_argument(
            "-v",
            "--value",
            dest="long_allocation",
            help="Amount to allocate to portfolio in long positions",
            type=float,
            default=1.0,
        )
        parser.add_argument(
            "-vs",
            "--value-short",
            dest="short_allocation",
            help="Amount to allocate to portfolio in short positions",
            type=float,
            default=0.0,
        )
        if other_args and "-" not in other_args[0][0]:
            other_args.insert(0, "-n")
        parser.add_argument(
            "-n",
            "--number-portfolios",
            default=100,
            type=check_non_negative,
            dest="amount_portfolios",
            help="Number of portfolios to simulate",
        )
        parser.add_argument(
            "-se",
            "--seed",
            default=123,
            type=check_non_negative,
            dest="random_seed",
            help="Seed used to generate random portfolios",
        )
        parser.add_argument(
            "-t",
            "--tangency",
            action="store_true",
            dest="tangency",
            default=False,
            help="Adds the optimal line with the risk-free asset",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 loaded tickers to calculate weights.\n"
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            optimizer_view.display_ef(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                risk_measure=parameters["risk_measure"].lower(),
                risk_free_rate=parameters["risk_free"],
                alpha=parameters["significance_level"],
                value=parameters["long_allocation"],
                value_short=parameters["short_allocation"],
                n_portfolios=parameters["amount_portfolios"],
                seed=parameters["random_seed"],
                tangency=parameters["tangency"],
            )

    @log_start_end(log=logger)
    def call_riskparity(self, other_args: List[str]):
        """Process riskparity command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="riskparity",
            description="""Build a risk parity portfolio based on risk
                budgeting approach""",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                    considered in the optimization process. """,
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-rm",
            "--risk-measure",
            default="MV",
            dest="risk_measure",
            help="""Risk measure used to optimize the portfolio. Possible values are:
                    MV : Variance
                    MAD : Mean Absolute Deviation
                    MSV : Semi Variance (Variance of negative returns)
                    FLPM : First Lower Partial Moment
                    SLPM : Second Lower Partial Moment
                    CVaR : Conditional Value at Risk
                    EVaR : Entropic Value at Risk
                    UCI : Ulcer Index of uncompounded returns
                    CDaR : Conditional Drawdown at Risk of uncompounded returns
                    EDaR : Entropic Drawdown at Risk of uncompounded returns
                    """,
            choices=self.riskparity_choices,
        )
        parser.add_argument(
            "-rc",
            "--risk-cont",
            type=lambda s: [float(item) for item in s.split(",")],
            default=None,
            dest="risk_contribution",
            help="vector of risk contribution constraint",
        )
        parser.add_argument(
            "-r",
            "--risk-free-rate",
            type=float,
            dest="risk_free",
            default=get_rf(),
            help="""Risk-free rate of borrowing/lending. The period of the
                risk-free rate must be annual""",
        )
        parser.add_argument(
            "-a",
            "--alpha",
            type=float,
            default=0.05,
            dest="significance_level",
            help="Significance level of CVaR, EVaR, CDaR and EDaR",
        )
        parser.add_argument(
            "-tr",
            "--target-return",
            dest="target_return",
            default=-1,
            help="Constraint on minimum level of portfolio's return",
        )
        parser.add_argument(
            "-de",
            "--d-ewma",
            type=float,
            default=0.94,
            dest="smoothing_factor_ewma",
            help="Smoothing factor for ewma estimators",
        )
        parser.add_argument(
            "-v",
            "--value",
            dest="long_allocation",
            help="Amount to allocate to portfolio",
            type=float,
            default=1.0,
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="RP_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 loaded tickers to calculate weights.\n"
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_risk_parity(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                risk_measure=parameters["risk_measure"].lower(),
                risk_cont=parameters["risk_contribution"],
                risk_free_rate=parameters["risk_free"],
                alpha=parameters["significance_level"],
                target_return=parameters["target_return"],
                value=parameters["long_allocation"],
            )
            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_relriskparity(self, other_args: List[str]):
        """Process relriskparity command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="relriskparity",
            description="""Build a relaxed risk parity portfolio based on
                least squares approach""",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-ve",
            "--version",
            default="A",
            dest="risk_parity_model",
            help="version of relaxed risk parity model",
            choices=self.relriskparity_choices,
        )
        parser.add_argument(
            "-rc",
            "--risk-cont",
            type=lambda s: [float(item) for item in s.split(",")],
            default=None,
            dest="risk_contribution",
            help="Vector of risk contribution constraints",
        )
        parser.add_argument(
            "-pf",
            "--penal-factor",
            type=float,
            dest="penal_factor",
            default=1,
            help="""The penalization factor of penalization constraints. Only
            used with version 'C'.""",
        )
        parser.add_argument(
            "-tr",
            "--target-return",
            dest="target_return",
            default=-1,
            help="Constraint on minimum level of portfolio's return",
        )
        parser.add_argument(
            "-de",
            "--d-ewma",
            type=float,
            default=0.94,
            dest="smoothing_factor_ewma",
            help="Smoothing factor for ewma estimators",
        )
        parser.add_argument(
            "-v",
            "--value",
            dest="long_allocation",
            help="Amount to allocate to portfolio",
            type=float,
            default=1.0,
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="RRP_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 loaded tickers to calculate weights.\n"
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_rel_risk_parity(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                version=parameters["risk_parity_model"],
                risk_cont=parameters["risk_contribution"],
                penal_factor=parameters["penal_factor"],
                target_return=parameters["target_return"],
                d_ewma=parameters["smoothing_factor_ewma"],
                value=parameters["long_allocation"],
            )
            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_hrp(self, other_args: List[str]):
        """Process hierarchical risk parity command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="hrp",
            description="Builds a hierarchical risk parity portfolio",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-cd",
            "--codependence",
            default="pearson",
            dest="co_dependence",
            help="""The codependence or similarity matrix used to build the
                distance metric and clusters. Possible values are:
                pearson: pearson correlation matrix
                spearman: spearman correlation matrix
                abs_pearson: absolute value of pearson correlation matrix
                abs_spearman: absolute value of spearman correlation matrix
                distance: distance correlation matrix
                mutual_info: mutual information codependence matrix
                tail: tail index codependence matrix""",
            choices=self.codependence_choices,
        )
        parser.add_argument(
            "-cv",
            "--covariance",
            default="hist",
            dest="covariance",
            help="""Method used to estimate covariance matrix. Possible values are
                    hist: historical method
                    ewma1: exponential weighted moving average with adjust=True
                    ewma2: exponential weighted moving average with adjust=False
                    ledoit: Ledoit and Wolf shrinkage method
                    oas: oracle shrinkage method
                    shrunk: scikit-learn shrunk method
                    gl: graphical lasso method
                    jlogo: j-logo covariance
                    fixed: takes average of eigenvalues above max Marchenko Pastour limit
                    spectral:  makes zero eigenvalues above max Marchenko Pastour limit
                    shrink: Lopez de Prado's book shrinkage method
                    """,
            choices=self.covariance_choices,
        )
        parser.add_argument(
            "-rm",
            "--risk-measure",
            default="MV",
            dest="risk_measure",
            help="""Risk measure used to optimize the portfolio. Possible values are:
                    MV : Variance
                    MAD : Mean Absolute Deviation
                    MSV : Semi Variance (Variance of negative returns)
                    FLPM : First Lower Partial Moment
                    SLPM : Second Lower Partial Moment
                    CVaR : Conditional Value at Risk
                    EVaR : Entropic Value at Risk
                    WR : Worst Realization
                    ADD : Average Drawdown of uncompounded returns
                    UCI : Ulcer Index of uncompounded returns
                    CDaR : Conditional Drawdown at Risk of uncompounded returns
                    EDaR : Entropic Drawdown at Risk of uncompounded returns
                    MDD : Maximum Drawdown of uncompounded returns
                    """,
            choices=self.hcp_choices,
        )
        parser.add_argument(
            "-r",
            "--risk-free-rate",
            type=float,
            dest="risk_free",
            default=get_rf(),
            help="""Risk-free rate of borrowing/lending. The period of the
                risk-free rate must be annual""",
        )
        parser.add_argument(
            "-a",
            "--alpha",
            type=float,
            default=0.05,
            dest="significance_level",
            help="""Significance level of VaR, CVaR, EVaR, DaR, CDaR, EDaR and
                Tail Gini of losses""",
        )
        parser.add_argument(
            "-as",
            "--a-sim",
            type=int,
            default=100,
            dest="cvar_simulations_losses",
            help="""Number of CVaRs used to approximate Tail Gini of losses.
                The default is 100""",
        )
        parser.add_argument(
            "-b",
            "--beta",
            type=float,
            default=None,
            dest="cvar_significance",
            help="""Significance level of CVaR and Tail Gini of gains. If
                empty it duplicates alpha""",
        )
        parser.add_argument(
            "-bs",
            "--b-sim",
            type=int,
            default=None,
            dest="cvar_simulations_gains",
            help="""Number of CVaRs used to approximate Tail Gini of gains.
                If empty it duplicates a_sim value""",
        )
        parser.add_argument(
            "-lk",
            "--linkage",
            default="single",
            dest="linkage",
            help="Linkage method of hierarchical clustering",
            choices=self.linkage_choices,
        )
        parser.add_argument(
            "-k",
            type=int,
            default=None,
            dest="amount_clusters",
            help="Number of clusters specified in advance",
        )
        parser.add_argument(
            "-mk",
            "--max-k",
            type=int,
            default=10,
            dest="max_clusters",
            help="""Max number of clusters used by the two difference gap
            statistic to find the optimal number of clusters. If k is
            empty this value is used""",
        )
        parser.add_argument(
            "-bi",
            "--bins-info",
            default="KN",
            dest="amount_bins",
            help="Number of bins used to calculate the variation of information",
        )
        parser.add_argument(
            "-at",
            "--alpha-tail",
            type=float,
            default=0.05,
            dest="alpha_tail",
            help="""Significance level for lower tail dependence index, only
            used when when codependence value is 'tail' """,
        )
        parser.add_argument(
            "-lo",
            "--leaf-order",
            default=True,
            dest="leaf_order",
            help="""Indicates if the cluster are ordered so that the distance
                between successive leaves is minimal""",
        )
        parser.add_argument(
            "-de",
            "--d-ewma",
            type=float,
            default=0.94,
            dest="smoothing_factor_ewma",
            help="Smoothing factor for ewma estimators",
        )
        parser.add_argument(
            "-v",
            "--value",
            type=float,
            default=1.0,
            dest="long_allocation",
            help="Amount to allocate to portfolio",
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="HRP_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 loaded tickers to calculate weights.\n"
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_hrp(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                codependence=parameters["co_dependence"].lower(),
                covariance=parameters["covariance"].lower(),
                risk_measure=parameters["risk_measure"].lower(),
                risk_free_rate=parameters["risk_free"],
                alpha=parameters["significance_level"],
                a_sim=parameters["cvar_simulations_losses"],
                beta=parameters["cvar_significance"],
                b_sim=parameters["cvar_simulations_gains"],
                linkage=parameters["linkage"].lower(),
                k=parameters["amount_clusters"],
                max_k=parameters["max_clusters"],
                bins_info=parameters["amount_bins"].upper(),
                alpha_tail=parameters["alpha_tail"],
                leaf_order=parameters["leaf_order"],
                d_ewma=parameters["smoothing_factor_ewma"],
                value=parameters["long_allocation"],
            )
            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_herc(self, other_args: List[str]):
        """Process hierarchical equal risk contribution command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="herc",
            description="Builds a hierarchical equal risk contribution portfolio",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-cd",
            "--codependence",
            default="pearson",
            dest="co_dependence",
            help="""The codependence or similarity matrix used to build the
                distance metric and clusters. Possible values are:
                pearson: pearson correlation matrix
                spearman: spearman correlation matrix
                abs_pearson: absolute value of pearson correlation matrix
                abs_spearman: absolute value of spearman correlation matrix
                distance: distance correlation matrix
                mutual_info: mutual information codependence matrix
                tail: tail index codependence matrix""",
            choices=self.codependence_choices,
        )
        parser.add_argument(
            "-cv",
            "--covariance",
            default="hist",
            dest="covariance",
            help="""Method used to estimate covariance matrix. Possible values are
                    hist: historical method
                    ewma1: exponential weighted moving average with adjust=True
                    ewma2: exponential weighted moving average with adjust=False
                    ledoit: Ledoit and Wolf shrinkage method
                    oas: oracle shrinkage method
                    shrunk: scikit-learn shrunk method
                    gl: graphical lasso method
                    jlogo: j-logo covariance
                    fixed: takes average of eigenvalues above max Marchenko Pastour limit
                    spectral:  makes zero eigenvalues above max Marchenko Pastour limit
                    shrink: Lopez de Prado's book shrinkage method
                    """,
            choices=self.covariance_choices,
        )
        parser.add_argument(
            "-rm",
            "--risk-measure",
            default="MV",
            dest="risk_measure",
            help="""Risk measure used to optimize the portfolio. Possible values are:
                    MV : Variance
                    MAD : Mean Absolute Deviation
                    MSV : Semi Variance (Variance of negative returns)
                    FLPM : First Lower Partial Moment
                    SLPM : Second Lower Partial Moment
                    CVaR : Conditional Value at Risk
                    EVaR : Entropic Value at Risk
                    WR : Worst Realization
                    ADD : Average Drawdown of uncompounded returns
                    UCI : Ulcer Index of uncompounded returns
                    CDaR : Conditional Drawdown at Risk of uncompounded returns
                    EDaR : Entropic Drawdown at Risk of uncompounded returns
                    MDD : Maximum Drawdown of uncompounded returns
                    """,
            choices=self.hcp_choices,
        )
        parser.add_argument(
            "-r",
            "--risk-free-rate",
            type=float,
            dest="risk_free",
            default=get_rf(),
            help="""Risk-free rate of borrowing/lending. The period of the
                risk-free rate must be annual""",
        )
        parser.add_argument(
            "-a",
            "--alpha",
            type=float,
            default=0.05,
            dest="significance_level",
            help="""Significance level of VaR, CVaR, EVaR, DaR, CDaR, EDaR and
                Tail Gini of losses""",
        )
        parser.add_argument(
            "-as",
            "--a-sim",
            type=int,
            default=100,
            dest="cvar_simulations_losses",
            help="""Number of CVaRs used to approximate Tail Gini of losses.
                The default is 100""",
        )
        parser.add_argument(
            "-b",
            "--beta",
            type=float,
            default=None,
            dest="cvar_significance",
            help="""Significance level of CVaR and Tail Gini of gains. If
                empty it duplicates alpha""",
        )
        parser.add_argument(
            "-bs",
            "--b-sim",
            type=int,
            default=None,
            dest="cvar_simulations_gains",
            help="""Number of CVaRs used to approximate Tail Gini of gains.
                If empty it duplicates a_sim value""",
        )
        parser.add_argument(
            "-lk",
            "--linkage",
            default="single",
            dest="linkage",
            help="Linkage method of hierarchical clustering",
            choices=self.linkage_choices,
        )
        parser.add_argument(
            "-k",
            type=int,
            default=None,
            dest="amount_clusters",
            help="Number of clusters specified in advance",
        )
        parser.add_argument(
            "-mk",
            "--max-k",
            type=int,
            default=10,
            dest="max_clusters",
            help="""Max number of clusters used by the two difference gap
            statistic to find the optimal number of clusters. If k is
            empty this value is used""",
        )
        parser.add_argument(
            "-bi",
            "--bins-info",
            default="KN",
            dest="amount_bins",
            help="Number of bins used to calculate the variation of information",
        )
        parser.add_argument(
            "-at",
            "--alpha-tail",
            type=float,
            default=0.05,
            dest="alpha_tail",
            help="""Significance level for lower tail dependence index, only
            used when when codependence value is 'tail' """,
        )
        parser.add_argument(
            "-lo",
            "--leaf-order",
            default=True,
            dest="leaf_order",
            help="""Indicates if the cluster are ordered so that the distance
                between successive leaves is minimal""",
        )
        parser.add_argument(
            "-de",
            "--d-ewma",
            type=float,
            default=0.94,
            dest="smoothing_factor_ewma",
            help="Smoothing factor for ewma estimators",
        )
        parser.add_argument(
            "-v",
            "--value",
            type=float,
            default=1.0,
            dest="long_allocation",
            help="Amount to allocate to portfolio",
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="HERC_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 loaded tickers to calculate weights.\n"
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_herc(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                codependence=parameters["co_dependence"].lower(),
                covariance=parameters["covariance"].lower(),
                risk_measure=parameters["risk_measure"].lower(),
                risk_free_rate=parameters["risk_free"],
                alpha=parameters["significance_level"],
                a_sim=parameters["cvar_simulations_losses"],
                beta=parameters["cvar_significance"],
                b_sim=parameters["cvar_simulations_gains"],
                linkage=parameters["linkage"].lower(),
                k=parameters["amount_clusters"],
                max_k=parameters["max_clusters"],
                bins_info=parameters["amount_bins"].upper(),
                alpha_tail=parameters["alpha_tail"],
                leaf_order=parameters["leaf_order"],
                d_ewma=parameters["smoothing_factor_ewma"],
                value=parameters["long_allocation"],
            )
            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()

    @log_start_end(log=logger)
    def call_nco(self, other_args: List[str]):
        """Process nested clustered optimization command"""
        parser = argparse.ArgumentParser(
            add_help=False,
            formatter_class=argparse.ArgumentDefaultsHelpFormatter,
            prog="nco",
            description="Builds a nested clustered optimization portfolio",
        )
        parser.add_argument(
            "-p",
            "--period",
            default="3y",
            dest="historic_period",
            help="""Period to get yfinance data from.
                    Possible frequency strings are:
                    'd': means days, for example '252d' means 252 days
                    'w': means weeks, for example '52w' means 52 weeks
                    'mo': means months, for example '12mo' means 12 months
                    'y': means years, for example '1y' means 1 year
                    'ytd': downloads data from beginning of year to today
                    'max': downloads all data available for each asset""",
        )
        parser.add_argument(
            "-s",
            "--start",
            default="",
            dest="start_period",
            help="""Start date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-e",
            "--end",
            default="",
            dest="end_period",
            help="""End date to get yfinance data from. Must be in
                    'YYYY-MM-DD' format""",
        )
        parser.add_argument(
            "-lr",
            "--log-returns",
            action="store_true",
            default=False,
            dest="log_returns",
            help="If use logarithmic or arithmetic returns to calculate returns",
        )
        parser.add_argument(
            "-f",
            "--freq",
            default="d",
            dest="return_frequency",
            help="""Frequency used to calculate returns. Possible values are:
                    'd': for daily returns
                    'w': for weekly returns
                    'm': for monthly returns
                    """,
            choices=self.freq_choices,
        )
        parser.add_argument(
            "-mn",
            "--maxnan",
            type=float,
            default=0.05,
            dest="max_nan",
            help="""Max percentage of nan values accepted per asset to be
                considered in the optimization process""",
        )
        parser.add_argument(
            "-th",
            "--threshold",
            type=float,
            default=0.30,
            dest="threshold_value",
            help="""Value used to replace outliers that are higher to threshold
                in absolute value""",
        )
        parser.add_argument(
            "-mt",
            "--method",
            default="time",
            dest="nan_fill_method",
            help="""Method used to fill nan values in time series, by default time.
                    Possible values are:
                    linear: linear interpolation
                    time: linear interpolation based on time index
                    nearest: use nearest value to replace nan values
                    zero: spline of zeroth order
                    slinear: spline of first order
                    quadratic: spline of second order
                    cubic: spline of third order
                    barycentric: builds a polynomial that pass for all points""",
        )
        parser.add_argument(
            "-cd",
            "--codependence",
            default="pearson",
            dest="co_dependence",
            help="""The codependence or similarity matrix used to build the
                distance metric and clusters. Possible values are:
                pearson: pearson correlation matrix
                spearman: spearman correlation matrix
                abs_pearson: absolute value of pearson correlation matrix
                abs_spearman: absolute value of spearman correlation matrix
                distance: distance correlation matrix
                mutual_info: mutual information codependence matrix
                tail: tail index codependence matrix""",
            choices=self.codependence_choices,
        )
        parser.add_argument(
            "-cv",
            "--covariance",
            default="hist",
            dest="covariance",
            help="""Method used to estimate covariance matrix. Possible values are
                    hist: historical method
                    ewma1: exponential weighted moving average with adjust=True
                    ewma2: exponential weighted moving average with adjust=False
                    ledoit: Ledoit and Wolf shrinkage method
                    oas: oracle shrinkage method
                    shrunk: scikit-learn shrunk method
                    gl: graphical lasso method
                    jlogo: j-logo covariance
                    fixed: takes average of eigenvalues above max Marchenko Pastour limit
                    spectral:  makes zero eigenvalues above max Marchenko Pastour limit
                    shrink: Lopez de Prado's book shrinkage method
                    """,
            choices=self.covariance_choices,
        )
        parser.add_argument(
            "-o",
            "--objective",
            default="MinRisk",
            dest="objective",
            help="Objective function used to optimize the portfolio",
            choices=self.nco_objective_choices,
        )
        parser.add_argument(
            "-rm",
            "--risk-measure",
            default="MV",
            dest="risk_measure",
            help="""Risk measure used to optimize the portfolio. Possible values are:
                    MV : Variance
                    MAD : Mean Absolute Deviation
                    MSV : Semi Variance (Variance of negative returns)
                    FLPM : First Lower Partial Moment
                    SLPM : Second Lower Partial Moment
                    CVaR : Conditional Value at Risk
                    EVaR : Entropic Value at Risk
                    WR : Worst Realization
                    ADD : Average Drawdown of uncompounded returns
                    UCI : Ulcer Index of uncompounded returns
                    CDaR : Conditional Drawdown at Risk of uncompounded returns
                    EDaR : Entropic Drawdown at Risk of uncompounded returns
                    MDD : Maximum Drawdown of uncompounded returns
                    """,
            choices=self.hcp_choices,
        )
        parser.add_argument(
            "-r",
            "--risk-free-rate",
            type=float,
            dest="risk_free",
            default=get_rf(),
            help="""Risk-free rate of borrowing/lending. The period of the
                risk-free rate must be annual""",
        )
        parser.add_argument(
            "-ra",
            "--risk-aversion",
            type=float,
            dest="risk_aversion",
            default=1.0,
            help="Risk aversion parameter",
        )
        parser.add_argument(
            "-a",
            "--alpha",
            type=float,
            default=0.05,
            dest="significance_level",
            help="Significance level of CVaR, EVaR, CDaR and EDaR",
        )
        parser.add_argument(
            "-lk",
            "--linkage",
            default="single",
            dest="linkage",
            help="Linkage method of hierarchical clustering",
            choices=self.linkage_choices,
        )
        parser.add_argument(
            "-k",
            type=int,
            default=None,
            dest="amount_clusters",
            help="Number of clusters specified in advance",
        )
        parser.add_argument(
            "-mk",
            "--max-k",
            type=int,
            default=10,
            dest="max_clusters",
            help="""Max number of clusters used by the two difference gap
            statistic to find the optimal number of clusters. If k is
            empty this value is used""",
        )
        parser.add_argument(
            "-bi",
            "--bins-info",
            default="KN",
            dest="amount_bins",
            help="Number of bins used to calculate the variation of information",
        )
        parser.add_argument(
            "-at",
            "--alpha-tail",
            type=float,
            default=0.05,
            dest="alpha_tail",
            help="""Significance level for lower tail dependence index, only
            used when when codependence value is 'tail' """,
        )
        parser.add_argument(
            "-lo",
            "--leaf-order",
            action="store_true",
            default=True,
            dest="leaf_order",
            help="""indicates if the cluster are ordered so that the distance
                between successive leaves is minimal""",
        )
        parser.add_argument(
            "-de",
            "--d-ewma",
            type=float,
            default=0.94,
            dest="smoothing_factor_ewma",
            help="Smoothing factor for ewma estimators",
        )
        parser.add_argument(
            "-v",
            "--value",
            dest="long_allocation",
            help="Amount to allocate to portfolio",
            type=float,
            default=1.0,
        )
        parser.add_argument(
            "--name",
            type=str,
            dest="name",
            default="NCO_" + str(self.count),
            help="Save portfolio with personalized or default name",
        )
        ns_parser = parse_known_args_and_warn(parser, other_args)

        if ns_parser:
            if len(self.tickers) < 2:
                console.print(
                    "Please have at least 2 loaded tickers to calculate weights.\n"
                )
                return

            arguments_tuple = ns_parser._get_kwargs()
            parameters = optimizer_view.check_params(
                parser, arguments_tuple, self.params
            )

            weights = optimizer_view.display_nco(
                stocks=self.tickers,
                period=parameters["historic_period"],
                start=parameters["start_period"],
                end=parameters["end_period"],
                log_returns=parameters["log_returns"],
                freq=parameters["return_frequency"],
                maxnan=parameters["max_nan"],
                threshold=parameters["threshold_value"],
                method=parameters["nan_fill_method"],
                codependence=parameters["co_dependence"].lower(),
                covariance=parameters["covariance"].lower(),
                objective=parameters["objective"].lower(),
                risk_measure=parameters["risk_measure"].lower(),
                risk_free_rate=parameters["risk_free"],
                risk_aversion=parameters["risk_aversion"],
                alpha=parameters["significance_level"],
                linkage=parameters["linkage"].lower(),
                k=parameters["amount_clusters"],
                max_k=parameters["max_clusters"],
                bins_info=parameters["amount_bins"].upper(),
                alpha_tail=parameters["alpha_tail"],
                leaf_order=parameters["leaf_order"],
                d_ewma=parameters["smoothing_factor_ewma"],
                value=parameters["long_allocation"],
            )
            self.portfolios[ns_parser.name.upper()] = weights
            self.count += 1
            self.update_runtime_choices()
