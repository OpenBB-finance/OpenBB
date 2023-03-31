import json
from pathlib import Path

from openbb_terminal.core.config.paths import OPENBB_DATA_SOURCES_DEFAULT_FILE


def read_sources(path: Path) -> dict:
    """Read sources from file.

    Parameters
    ----------
    path : str
        Path to file

    Returns
    -------
    dict
        Dictionary with sources
    """
    try:
        with open(path) as file:
            return json.load(file)
    except Exception as e:
        print(f"\nFailed to read data sources file: " f"{path}\n{e}\n")
        print("Using OpenBB defaults for guest mode.")

        with open(OPENBB_DATA_SOURCES_DEFAULT_FILE) as file:
            return json.load(file)
