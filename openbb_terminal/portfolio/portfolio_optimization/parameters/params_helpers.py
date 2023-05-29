import argparse
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List

from openbb_terminal.core.config import paths
from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.helper_funcs import log_and_raise
from openbb_terminal.portfolio.portfolio_optimization.statics import (
    OPTIMIZATION_PARAMETERS,
    TERMINAL_TEMPLATE_MAP,
)
from openbb_terminal.rich_config import console


def check_save_file(file: str) -> str:
    """Argparse type to check parameter file to be saved"""
    if file == "defaults.ini":
        log_and_raise(
            argparse.ArgumentTypeError(
                "Cannot overwrite defaults.ini file, please save with a different name"
            )
        )
    else:
        if not file.endswith(".ini"):
            log_and_raise(
                argparse.ArgumentTypeError("File to be saved needs to be .ini")
            )

    return file


def load_data_files() -> Dict[str, Path]:
    """Loads files from the misc directory and from the user's custom exports

    Returns
    -------
    Dict[str, Path]
        The dictionary of filenames and their paths
    """
    default_path = paths.MISCELLANEOUS_DIRECTORY / "portfolio"
    custom_exports = (
        get_current_user().preferences.USER_PORTFOLIO_DATA_DIRECTORY / "optimization"
    )
    data_files = {}
    for directory in [default_path, custom_exports]:
        for file_type in ["xlsx", "ini"]:
            for filepath in Path(directory).rglob(f"*.{file_type}"):
                if filepath.is_file() and "example" not in filepath.name:
                    data_files[filepath.name] = filepath

    return data_files


def check_convert_parameters(received_parameters: dict) -> dict:
    """Check if the argument is in the parameters list.
    If it is, try to cast it to the correct type, else use default value.

    Parameters
    ----------
    received_parameters: dict
        The parameters to be checked

    Returns
    -------
    dict
        The parameters with the correct types
    """

    converted_parameters = check_convert_dates(
        received_parameters, ["start_period", "start_date", "end_period", "end_date"]
    )

    for received_name, received_value in received_parameters.items():
        # TODO: Remove this line when mapping between template and terminal is not needed
        template_name = TERMINAL_TEMPLATE_MAP.get(received_name, received_name)

        if template_name in OPTIMIZATION_PARAMETERS:
            PARAMETER = OPTIMIZATION_PARAMETERS[template_name]
            if not PARAMETER.validate_type(received_value):
                converted_parameters[received_name] = check_convert_parameter(
                    name=received_name, value=received_value, parameter=PARAMETER
                )

    return converted_parameters


def check_convert_parameter(name, value, parameter):
    """Converts a parameter to the correct type

    Parameters
    ----------
    name: str
        The name of the received parameter
    value: str
        The value of the received parameter
    parameter: Parameter
        The parameter object

    Returns
    -------
    The converted parameter
    """

    try:
        # Try to cast the value to the correct type if int or float
        if parameter.type_ is int:
            new_value = parameter.type_(float(value))
        elif parameter.type_ is float:
            new_value = parameter.type_(value)
        elif parameter.type_ is bool:
            new_value = strtobool(value)
        else:
            new_value = value
    except ValueError:
        new_value = parameter.default
        console.print(
            f"[red]'{name}' format should be '{parameter.type_.__name__}' type[/red]",
            f"[red]and could not be converted. Setting default '{new_value}'.\n[/red]",
        )

    return new_value


def check_convert_dates(params: dict, param_name_list: List[str]) -> dict:
    """Check if the argument is in the list and convert it to a str object
    Parameters
    ----------
    params : dict
        The parameters to be converted
    param_name_list : List[str]
        The list of arguments to be converted

    Returns
    -------
    dict
        The converted parameters
    """

    for param_name in param_name_list:
        if param_name in params:
            param_value = params[param_name]
            if isinstance(param_value, date):
                params[param_name] = param_value.strftime("%Y-%m-%d")
            elif isinstance(param_value, str):
                try:
                    param_value = datetime.strptime(param_value, "%Y-%m-%d")
                except ValueError:
                    console.print(
                        f"[red]'{param_name}' format is not a valid date, must be YYYY-MM-DD.\n[/red]"
                    )
                    params.pop(param_name)
            else:
                console.print(
                    f"[red]'{param_name}' format is not a valid date, must be YYYY-MM-DD.\n[/red]"
                )
                params.pop(param_name)

    return params


def booltostr(value: bool) -> Any:
    """Converts a bool to a string or returns the value itself if not bool

    Parameters
    ----------
    value: bool
        The bool to be converted or the value itself if not bool

    Returns
    -------
    Any
        The converted value
    """

    if isinstance(value, bool):
        return "True" if value else "False"
    return value


def strtobool(value: str) -> Any:
    """Converts a string to a bool or returns the value itself if not string

    Parameters
    ----------
    value: str
        The string to be converted or the value itself if not string

    Returns
    -------
    Any
        The converted value
    """

    if isinstance(value, str):
        if value.lower() == "true":
            return True
        elif value.lower() == "false":
            return False
    return value
