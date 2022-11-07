import argparse
from typing import Dict
from pathlib import Path
from openbb_terminal.helper_funcs import log_and_raise
from openbb_terminal.core.config import paths


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
    ----------
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
