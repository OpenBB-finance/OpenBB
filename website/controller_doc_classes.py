# pylint: disable=unused-argument
import argparse
import contextlib
import inspect
import sys
from datetime import datetime, timedelta
from importlib.util import module_from_spec, spec_from_file_location
from inspect import FullArgSpec, getmembers, isclass
from pathlib import Path
from types import FunctionType, ModuleType
from typing import Any, Dict, List, Optional
from unittest.mock import patch

import pandas as pd
from pandas.tseries.holiday import USFederalHolidayCalendar

import openbb_terminal
import openbb_terminal.config_terminal as cfg
from openbb_terminal.core.plots.backend import plots_backend
from openbb_terminal.core.session.current_system import set_system_variable
from openbb_terminal.core.session.current_user import get_current_user  # noqa: F401
from openbb_terminal.decorators import disable_check_api
from openbb_terminal.helper_funcs import (
    EXPORT_BOTH_RAW_DATA_AND_FIGURES,
    EXPORT_ONLY_FIGURES_ALLOWED,
    NO_EXPORT,
    set_command_location,
)
from openbb_terminal.parent_classes import BaseController
from openbb_terminal.rich_config import console
from openbb_terminal.sdk import openbb
from openbb_terminal.stocks.comparison_analysis import finviz_compare_model

set_system_variable("TEST_MODE", True)
set_system_variable("LOG_COLLECT", False)
disable_check_api()


CRYPTO_DATA = openbb.crypto.load("BTC", to_symbol="usd", source="YahooFinance")
ETF_DATA = openbb.etf.load("SPY")
ETF_DATA.index.name = "date"
FOREX_DATA = openbb.forex.load(to_symbol="USD", from_symbol="EUR")
FOREX_DATA.index.name = "date"
STOCK_DATA = openbb.stocks.load("AAPL", start_date="2022-01-01")
STOCK_DATA.index.name = "date"

data_dict = {
    "stocks": {
        "data": STOCK_DATA,
        "symbol": "AAPL",
    },
    "crypto": {
        "data": CRYPTO_DATA,
        "symbol": "BTC",
    },
    "forex": {
        "data": FOREX_DATA,
        "symbol": "EURUSD",
    },
    "futures": {
        "data": STOCK_DATA,
        "symbol": "ES",
    },
    "etf": {
        "data": ETF_DATA,
        "symbol": "SPY",
    },
}

sub_folders_abbr = {
    "discovery": "disc",
    "due_diligence": "dd",
    "overview": "ov",
    "alternative": "alt",
    "cryptocurrency": "crypto",
    "behavioural_analysis": "ba",
    "comparison_analysis": "ca",
    "dark_pool_shorts": "dps",
    "portfolio_optimization": "po",
    "quantitative_analysis": "qa",
    "technical_analysis": "ta",
    "tradinghours": "th",
    "fundamental_analysis": "fa",
    "mutual_funds": "funds",
    "government": "gov",
    "insider": "ins",
}

sub_names_full = {
    "alt": "Alternative",
    "ba": "Behavioural Analysis",
    "ca": "Comparison Analysis",
    "crypto": "Cryptocurrency",
    "dd": "Due Diligence",
    "defi": "DeFi",
    "disc": "Discovery",
    "dps": "Darkpool Shorts",
    "etf": "ETFs",
    "fa": "Fundamental Analysis",
    "forecast": "Forecasting",
    "funds": "Mutual Funds",
    "gov": "Government",
    "ins": "Insiders",
    "keys": "Keys",
    "nft": "NFTs",
    "onchain": "OnChain",
    "ov": "Overview",
    "po": "Portfolio Optimization",
    "qa": "Quantitative Analysis",
    "screener": "Screener",
    "ta": "Technical Analysis",
    "th": "Trading Hours",
}

required_flags = {
    "crypto": {
        "funot": ["-p", "ethereum"],
    },
    "econometrics": {
        "coint": ["-t"],  # TODO: add choice
        "norm": ["-v"],  # TODO: add choice
    },
}


def get_expiration_date():
    """Gets the next expiration date for controller init"""
    dt = datetime.now()
    bdays_indx = pd.bdate_range(
        dt.strftime("%Y-%m-%d"),
        (dt + timedelta(days=20)).strftime("%Y-%m-%d"),
        freq=pd.offsets.CustomBusinessDay(calendar=USFederalHolidayCalendar()),
    ).tolist()
    expiration = [x.strftime("%Y-%m-%d") for x in bdays_indx if x.weekday() == 4][0]
    return expiration


start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
end_date = datetime.now().strftime("%Y-%m-%d")

param_name_to_value = {
    "expiration": get_expiration_date(),
    "start_date": start_date,
    "start": start_date,
    "end_date": end_date,
    "end": end_date,
    "from_symbol": "USD",
    "to_symbol": "EUR",
    "vs": "USDT",
}
param_type_to_value = {
    (dict, Dict): {},
    list: [],
    str: "",
    int: 0,
    float: 0.0,
    bool: False,
}


def get_parameters(
    controller_cls: BaseController, name: str, df_loaded: pd.DataFrame, symbol: str
) -> Dict[str, Any]:
    """Gets the parameters of a controller's `__init__` signature. If required parameters are missing,
    we get the type and use a default value for it.

    Parameters
    ----------
    controller_class: Type[BaseController]
        The controller class
    name: str
        The name of the controller
    df_loaded: pd.DataFrame
        The dataframe loaded from the `load` function
    symbol: str
        The symbol to use on controller init

    Returns
    -------
    dict[str, Any]
        The parameters with their values for controller init
    """
    signature = inspect.signature(controller_cls)  # type: ignore
    kwargs: Dict[str, Any] = {}

    for param in signature.parameters.values():
        if param.name in ("ticker", "symbol", "coin"):
            kwargs[param.name] = symbol
        elif param.name == "data" and name in ("forecast", "qa"):
            kwargs["data"] = df_loaded
        elif (
            param.default is inspect.Parameter.empty
            and param.kind is not inspect.Parameter.VAR_KEYWORD
        ):
            for param_name, value in param_name_to_value.items():
                if param.name == param_name:
                    kwargs[param.name] = value
                    break
            if param.name not in kwargs:
                for param_type, value in param_type_to_value.items():
                    if isinstance(param_type, tuple):
                        if param.annotation in param_type:
                            kwargs[param.name] = {symbol: df_loaded}
                            break
                    elif param.annotation is pd.DataFrame:
                        kwargs[param.name] = df_loaded
                        break
                    elif param.annotation is param_type:
                        kwargs[param.name] = value
                        break

    return kwargs


class ControllerDoc:
    """Class that retrieves the ArgumentParser for each command of the Controller and stores it in a dictionary
        for use in auto-generating the documentation.

    Parameters
    ----------
    controller: BaseController
        The controller to get the commands from

    Attributes
    ----------
    controller: BaseController
        The controller to get the commands from
    cmd_parsers: Dict[str, argparse.ArgumentParser]
        A dictionary of the command name and the ArgumentParser for that command
    cmd_funcs: Dict[str, FunctionType]
        A dictionary of the command name and the function for that command
    cmd_fullspec: Dict[str, FullArgSpec]
        A dictionary of the command name and the full argument spec for that command
    ignore: List[str]
        A list of commands to ignore
    commands: List[str]
        A list of commands to document

    Methods
    -------
    get_commands()
        Get commands
    get_command_parser(command: str)
        Get the parser for a command
    get_all_command_parsers()
        Get all command parsers
    has_commands()
        Checks if controller has commands to document
    """

    def __init__(self, controller: BaseController, trailmap: str):
        self.trailmap = trailmap
        self.name = trailmap.split(".")[-1]

        params = data_dict.get(trailmap.split(".")[0], data_dict["stocks"])
        self.symbol = params.get("symbol", "AAPL")
        self.current_df = params.get("data", STOCK_DATA)

        self.controller: BaseController = controller(  # type: ignore
            **get_parameters(controller, self.name, self.current_df, self.symbol)
        )

        root_menu = self.controller.path[0]
        sub_menu = self.controller.path[1] if len(self.controller.path) > 1 else None
        if sub_menu and sub_menu:
            console.print(
                f"[bold green]Loading {root_menu}[/] [bold yellow]{sub_menu}[/]"
            )
        else:
            console.print(f"[bold green]Loading {root_menu}[/]")

        self.cmd_parsers: Dict[str, argparse.ArgumentParser] = {}
        self.cmd_funcs: Dict[str, FunctionType] = {}
        self.cmd_fullspec: Dict[str, FullArgSpec] = {}
        self.image_exportable: Dict[str, bool] = {}
        self.ignore = [
            "call_help",
            "call_exit",
            "call_clear",
            "call_cls",
            "call_quit",
            "call_about",
            "call_reset",
            "call_support",
            "call_wiki",
            "call_record",
            "call_stop",
            "call_screenshot",
        ]
        self.commands: List[str] = self.get_commands()

        if self.name == "options" and hasattr(self.controller, "selected_date"):
            self.controller.selected_date = get_expiration_date()
        elif self.name == "ca" and hasattr(self.controller, "similar"):
            self.controller.similar = finviz_compare_model.get_similar_companies(
                self.symbol, ["Sector", "Industry"]
            )
        if hasattr(self.controller, "current_currency"):
            self.controller.current_currency = "usdt"
        if hasattr(self.controller, "source") and trailmap.split(".")[0] == "crypto":
            self.controller.source = "YahooFinance"

        for attr in ["ticker", "symbol", "coin", "etf_name"]:
            if hasattr(self.controller, attr):
                setattr(self.controller, attr, self.symbol)
        for attr in ["current_df", "etf_data"]:
            if hasattr(self.controller, attr):
                setattr(self.controller, attr, self.current_df)

        self.get_all_command_parsers()

    def get_commands(self) -> List[str]:
        """Get commands"""
        commands = []
        for name, _ in getmembers(self.controller, predicate=inspect.ismethod):
            if name.startswith("call_") and name not in self.ignore:
                func = getattr(self.controller, name)

                if hasattr(func, "__wrapped__"):
                    while hasattr(func, "__wrapped__"):
                        func = func.__wrapped__

                self.cmd_funcs[name] = func
                self.cmd_fullspec[name] = inspect.getfullargspec(func)

                if "_" not in self.cmd_fullspec[
                    name
                ].args and "from openbb_terminal." not in inspect.getsource(func):
                    commands.append(name)

        return commands

    def get_command_parser(self, command: str) -> Optional[argparse.ArgumentParser]:
        """Get command parser"""
        if command not in self.cmd_parsers:
            self._get_parser(command)

        if command in self.cmd_parsers:
            return self.cmd_parsers[command]

        return None

    def _get_parser(self, command: str) -> None:
        """Get parser information from source"""
        self.image_exportable[command] = False

        def mock_func(fparser: argparse.ArgumentParser, *args, **kwargs):
            """Mock function to get the parser"""
            allowed = [EXPORT_BOTH_RAW_DATA_AND_FIGURES, EXPORT_ONLY_FIGURES_ALLOWED]
            export = kwargs.get("export_allowed", NO_EXPORT)

            if export in allowed:
                self.image_exportable[command] = True
            else:
                for arg in args:
                    if arg in allowed:
                        self.image_exportable[command] = True
                        break

            self.cmd_parsers[command] = fparser

        try:
            with patch.object(
                self.controller, "parse_known_args_and_warn", new=mock_func
            ) as _:
                args = {}

                fullspec = self.cmd_fullspec[command]
                if "_" in fullspec.args:
                    return

                if len(fullspec.args) > 2:
                    args.update({arg: ["1234"] for arg in fullspec.args[2:]})
                with patch(
                    "openbb_terminal.rich_config.console.print"
                ), contextlib.suppress(SystemExit, AttributeError):
                    _ = getattr(self.controller, command)(["--help"], **args)

        except Exception as e:
            print(e)

    def run_image_exports(self) -> None:
        """Run image exports"""
        if not self.image_exportable:
            return

        for command in self.commands:
            self.get_image_export(command)

    def get_image_export(self, command: str) -> None:
        """Get image export"""
        if not self.image_exportable[command]:
            return

        console.print(
            f"[yellow]Exporting {command} image for {self.name} controller[/]"
        )
        try:
            cmd_name = command.replace("call_", "")

            other_args = [
                "--export",
                f"{'_'.join(self.controller.path)}_{cmd_name}.png",
            ]

            for action in self.cmd_parsers[command]._actions:  # pylint: disable=W0212
                if action.dest == "strike":
                    other_args.extend(["--strike", "100"])
                if action.dest == "target_dataset":
                    other_args.extend(["--dataset", "AAPL"])
                if action.dest == "ticker":
                    other_args.extend(["--ticker", self.symbol])
                if self.name == "forecast" and action.dest == "values":
                    other_args.extend(["--values", "AAPL.close"])

            set_command_location(f"/{'/'.join(self.controller.path)}/{cmd_name}")

            _ = getattr(self.controller, command)(other_args)

        except (SystemExit, KeyError):
            pass

    def get_all_command_parsers(self) -> None:
        """Get all command parsers"""
        for command in self.commands:
            self.get_command_parser(command)

    def has_commands(self) -> bool:
        """Checks if controller has commands"""
        return len(self.commands) > 0


class LoadControllersDoc:
    """Class that loads all controllers and creates a ControllerDoc class instance for each one


    Attributes
    ----------
    controller_docs: Dict[str, ControllerDoc]
        A dictionary of the controller name and the ControllerDoc class instance for that controller

    Methods
    -------
    get_controllers()
        Gets all controllers to create a ControllerDoc class instance for
    get_controller_doc(controller: str)
        Gets the ControllerDoc class instance for a controller
    available_controllers()
        Gets a list of available controllers names
    """

    def __init__(self) -> None:
        self.controller_docs: Dict[str, ControllerDoc] = {}
        self.get_controllers()

    def get_controllers(self) -> None:
        """Gets all controllers"""
        for trailmap, module in self._get_modules().items():
            for name, obj in getmembers(module):
                if (  # noqa: SIM102
                    name != "TerminalController" and "BaseController" not in name
                ):  # noqa: SIM102
                    if (
                        isclass(obj)
                        and issubclass(obj, BaseController)
                        and trailmap not in self.controller_docs
                    ):
                        ctrl = ControllerDoc(obj, trailmap)  # type: ignore
                        if ctrl.has_commands():
                            self.controller_docs[trailmap] = ctrl

    def _get_modules(self) -> Dict[str, ModuleType]:
        """Gets all controllers modules"""
        modules = {}
        terminal_path = Path(openbb_terminal.__file__).parent

        for file in terminal_path.glob("**/*controller.py"):
            spec = spec_from_file_location(file.stem, file)
            if spec is not None and spec.loader is not None:
                module = module_from_spec(spec)
                spec.loader.exec_module(module)

                ctrl_path = (
                    str(file)
                    .replace(str(terminal_path), "")
                    .replace("\\", "/")
                    .split("/")[1:]
                )
                for sub_name, abbr in sub_folders_abbr.items():
                    ctrl_path = [
                        path.lower().replace(sub_name, abbr) for path in ctrl_path
                    ]

                trailmap = ".".join(ctrl_path[:-1])
                if trailmap not in modules:
                    modules[trailmap] = module

        return modules

    def get_controller_doc(self, controller_name: str) -> ControllerDoc:
        """Get the ControllerDoc instance for a controller"""
        if controller_name not in self.controller_docs:
            raise KeyError(f"Controller {controller_name} not found")

        return self.controller_docs[controller_name]

    def available_controllers(self) -> List[str]:
        """Get available controllers"""
        return [ctrl for ctrl in self.controller_docs if ctrl != ""]


if __name__ == "__main__":
    try:
        run_image_exports = "--images" in sys.argv
        load_controllers = LoadControllersDoc()

        for loaded in load_controllers.available_controllers():
            controller_doc = load_controllers.get_controller_doc(loaded)
            controller_doc.get_all_command_parsers()
            if run_image_exports:
                cfg.setup_config_terminal()
                plots_backend().start()
                plots_backend().isatty = True
                get_current_user().preferences.USE_INTERACTIVE_DF = False
                controller_doc.run_image_exports()
    except KeyboardInterrupt:
        sys.exit(0)
