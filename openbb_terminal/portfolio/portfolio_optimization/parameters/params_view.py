import configparser
from pathlib import Path
from typing import Tuple

import pandas as pd

from openbb_terminal.core.session.current_user import get_current_user
from openbb_terminal.helper_funcs import print_rich_table
from openbb_terminal.portfolio.portfolio_optimization import excel_model
from openbb_terminal.portfolio.portfolio_optimization.parameters import params_statics
from openbb_terminal.portfolio.portfolio_optimization.parameters.params_helpers import (
    booltostr,
    check_convert_parameters,
)
from openbb_terminal.rich_config import console


def load_file(path: str = "") -> Tuple[dict, str]:
    """
    Loads in the configuration file and return the parameters in a dictionary including the model
    if available.

    Parameters
    ----------
    path: str
        The location of the file to be loaded in either xlsx or ini.

    Returns
    -------
    Tuple[dict, str]
        Return the parameters and the model, if available.
    """
    if str(path).endswith(".ini"):
        params_obj = configparser.RawConfigParser()
        params_obj.read(path)
        params_obj.optionxform = str  # type: ignore
        params: dict = dict(params_obj["OPENBB"].items())

        current_model = params["technique"] if "technique" in params else ""

    elif str(path).endswith(".xlsx"):
        params, _ = excel_model.load_configuration(path)
        current_model = params["technique"]
    else:
        console.print("Cannot load in the file due to not being an .ini or .xlsx file.")
        return {}, ""

    converted_parameters = check_convert_parameters(received_parameters=params)

    max_len = max(len(k) for k in converted_parameters)
    help_text = "[info]Parameters:[/info]\n"

    if current_model:
        for k, v in converted_parameters.items():
            all_params = (
                params_statics.DEFAULT_PARAMETERS
                + params_statics.MODEL_PARAMS[current_model]
            )
            if k in all_params:
                clean_v = booltostr(v)
                help_text += (
                    f"    [param]{k}{' ' * (max_len - len(k))} :[/param] {clean_v}\n"
                )
    else:
        for k, v in converted_parameters.items():
            clean_v = booltostr(v)
            help_text += (
                f"    [param]{k}{' ' * (max_len - len(k))} :[/param] {clean_v}\n"
            )

    console.print(help_text)

    return converted_parameters, current_model


def save_file(path: str, params: dict) -> Path:
    if not path.endswith(".ini"):
        console.print("[red]File to be saved needs to be a .ini file.[/red]\n")
    # Create file if it does not exist
    base_path = (
        get_current_user().preferences.USER_PORTFOLIO_DATA_DIRECTORY / "optimization"
    )
    if not base_path.is_dir():
        base_path.mkdir()
    filepath = base_path / path

    config_parser = configparser.RawConfigParser()
    config_parser.add_section("OPENBB")
    for key, value in params.items():
        config_parser.set("OPENBB", key, value)

    with open(filepath, "w") as configfile:
        config_parser.write(configfile)

    return filepath


def show_arguments(arguments, description=None):
    """
    Show the available arguments and the choices you have for each. If available, also show
    the description of the argument.

    Parameters
    ----------
    arguments: Dictionary
        A dictionary containing the keys and the possible values.
    description: Dictionary
        A dictionary containing the keys equal to arguments and the descriptions.

    Returns
    -------
    A table containing the parameter names, possible values and (if applicable) the description.
    """
    adjusted_arguments = {}

    for variable in arguments:
        if len(arguments[variable]) > 15:
            minimum = min(arguments[variable])
            maximum = max(arguments[variable])
            adjusted_arguments[variable] = (
                f"Between {minimum} and {maximum} in steps of "
                f"{maximum / sum(x > 0 for x in arguments[variable])}"
            )
        else:
            adjusted_arguments[variable] = ", ".join(arguments[variable])

    if description:
        df = pd.DataFrame([adjusted_arguments, description]).T
        columns = ["Options", "Description"]
    else:
        df = pd.DataFrame([adjusted_arguments]).T
        columns = ["Options"]

    df = df[df.index != "technique"]

    print_rich_table(
        df, headers=list(columns), show_index=True, index_name="Parameters"
    )
