import argparse
from datetime import datetime
from typing import Dict, List
from pathlib import Path
from openbb_terminal.helper_funcs import log_and_raise
from openbb_terminal.core.config import paths
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
    default_path = paths.MISCELLANEOUS_DIRECTORY / "portfolio_examples" / "optimization"
    custom_exports = paths.USER_EXPORTS_DIRECTORY / "portfolio"
    data_files = {}
    for directory in [default_path, custom_exports]:
        for file_type in ["xlsx", "ini"]:
            for filepath in Path(directory).rglob(f"*.{file_type}"):
                if filepath.is_file():
                    data_files[filepath.name] = filepath

    return data_files


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
            if isinstance(param_value, datetime):
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
