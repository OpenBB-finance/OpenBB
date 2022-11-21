# pylint: disable=unused-argument
import argparse
import inspect
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
from openbb_terminal.parent_classes import BaseController, CryptoBaseController

DF_STOCK = pd.DataFrame.from_dict(
    data={
        pd.Timestamp("2020-11-30 00:00:00"): {
            "Open": 75.69999694824219,
            "High": 76.08999633789062,
            "Low": 75.41999816894531,
            "Close": 75.75,
            "Adj Close": 71.90919494628906,
            "Volume": 5539100,
            "date_id": 1,
            "OC_High": 75.75,
            "OC_Low": 75.69999694824219,
        },
        pd.Timestamp("2020-12-01 00:00:00"): {
            "Open": 76.0199966430664,
            "High": 77.12999725341797,
            "Low": 75.69000244140625,
            "Close": 77.02999877929688,
            "Adj Close": 73.1242904663086,
            "Volume": 6791700,
            "date_id": 2,
            "OC_High": 77.02999877929688,
            "OC_Low": 76.0199966430664,
        },
    },
    orient="index",
)

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
    "sector_industry_analysis": "sia",
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
    "sia": "Sector Industry Analysis",
    "ta": "Technical Analysis",
    "th": "Trading Hours",
}


def get_expiration_date():
    """Gets the next expiration date for dummy data"""
    dt = datetime.now()
    bdays_indx = pd.bdate_range(
        dt.strftime("%Y-%m-%d"),
        (dt + timedelta(days=20)).strftime("%Y-%m-%d"),
        freq=pd.offsets.CustomBusinessDay(calendar=USFederalHolidayCalendar()),
    ).tolist()
    expiration = [x.strftime("%Y-%m-%d") for x in bdays_indx if x.weekday() == 4][0]
    return expiration


def get_parameters(
    controller_cls: BaseController,
) -> Dict[str, Any]:
    """Gets the parameters of a controller's `__init__` signature. If required parameters are missing,
        we get the type and create a dummy value for it.

    Parameters:
    ----------
    controller_class: Type[BaseController]
        The controller class

    Returns:
    ----------
    dict[str, Any]
        The dummy parameters for the controller init
    """
    signature = inspect.signature(controller_cls)
    kwargs: Dict[str, Any] = {}
    for param in signature.parameters.values():
        if param.name in ("ticker", "symbol"):
            kwargs[param.name] = (
                "AAPL"
                if not issubclass(controller_cls, CryptoBaseController)
                else "BTC"
            )
        elif (
            param.default is inspect.Parameter.empty
            and param.kind is not inspect.Parameter.VAR_KEYWORD
        ):
            if param.name == "expiration":
                kwargs[param.name] = get_expiration_date()
            elif param.name in ("start_date", "start"):
                kwargs[param.name] = "2022-01-01"
            elif param.name in ("end_date", "end"):
                kwargs[param.name] = "2022-08-01"
            elif param.name == "vs":
                kwargs[param.name] = "USDT"
            elif param.annotation == pd.DataFrame:
                kwargs[param.name] = DF_STOCK
            elif param.annotation in (dict, Dict):
                kwargs[param.name] = {"AAPL": DF_STOCK}
            elif param.annotation == list:
                kwargs[param.name] = []
            elif param.annotation == str:
                kwargs[param.name] = ""
            elif param.annotation == int:
                kwargs[param.name] = 0
            elif param.annotation == float:
                kwargs[param.name] = 0.0
            elif param.annotation == bool:
                kwargs[param.name] = False

    return kwargs


class ControllerDoc:
    """Class that retrieves the ArgumentParser for each command of the Controller and stores it in a dictionary
        for use in auto-generating the documentation.

    Parameters:
    ----------
    controller: BaseController
        The controller to get the commands from

    Attributes:
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

    Methods:
    ----------
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

        self.controller = controller(**get_parameters(controller))
        self.trailmap = trailmap
        self.name = trailmap.split(".")[-1]
        self.cmd_parsers: Dict[str, argparse.ArgumentParser] = {}
        self.cmd_funcs: Dict[str, FunctionType] = {}
        self.cmd_fullspec: Dict[str, FullArgSpec] = {}
        self.ignore = [
            "call_help",
            "call_exit",
            "call_clear",
            "call_cls",
            "call_quit",
            "call_about",
            "call_reset",
            "call_support",
            "call_glossary",
            "call_wiki",
            "call_record",
            "call_stop",
            "call_screenshot",
        ]
        self.commands: List[str] = self.get_commands()
        self.get_all_command_parsers()

    def get_commands(self) -> List[str]:
        """Get commands"""
        commands = []
        for name, _ in getmembers(self.controller, predicate=inspect.ismethod):

            if name.startswith("call_") and name not in self.ignore:
                func = getattr(self.controller, name)

                if hasattr(func, "__wrapped__"):
                    func = func.__wrapped__
                    if hasattr(func, "__wrapped__"):
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

        def mock_func(fparser: argparse.ArgumentParser, *args, **kwargs):
            self.cmd_parsers[command] = fparser
            return

        with patch.object(
            self.controller, "parse_known_args_and_warn", new=mock_func
        ) as _:
            args = {}

            fullspec = self.cmd_fullspec[command]
            if "_" in fullspec.args:
                return

            if len(fullspec.args) > 2:
                args.update({arg: ["1234"] for arg in fullspec.args[2:]})

            _ = getattr(self.controller, command)(["--help"], **args)

    def get_all_command_parsers(self) -> None:
        """Get all command parsers"""
        for command in self.commands:
            self.get_command_parser(command)

    def has_commands(self) -> bool:
        """Checks if controller has commands"""
        return len(self.commands) > 0


class LoadControllersDoc:
    """Class that loads all controllers and creates a ControllerDoc class instance for each one


    Attributes:
    ----------
    controller_docs: Dict[str, ControllerDoc]
        A dictionary of the controller name and the ControllerDoc class instance for that controller

    Methods:
    ----------
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
                if name != "TerminalController" and "BaseController" not in name:
                    if isclass(obj) and issubclass(obj, BaseController):
                        if trailmap not in self.controller_docs:
                            ctrl = ControllerDoc(obj, trailmap)
                            if ctrl.has_commands():
                                self.controller_docs[trailmap] = ctrl

    def _get_modules(self) -> Dict[str, ModuleType]:
        """Gets all controllers modules"""
        modules = {}
        for file in Path(openbb_terminal.__file__).parent.glob("**/*controller.py"):
            spec = spec_from_file_location(file.stem, file)
            if spec is not None and spec.loader is not None:
                module = module_from_spec(spec)
                spec.loader.exec_module(module)

                ctrl_path = (
                    str(file)
                    .replace(str(Path(openbb_terminal.__file__).parent), "")
                    .split("\\")[1:]
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
