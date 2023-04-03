import json
from pathlib import Path
from typing import Dict

from openbb_terminal.core.models.sources_model import flatten, read_default_sources


def read_sources(path: Path) -> Dict:
    """Read sources from file.

    Parameters
    ----------
    path : str
        Path to file

    Returns
    -------
    Dict
        Dictionary with sources
    """
    try:
        with open(path) as file:
            return flatten(json.load(file))
    except Exception as e:
        print(f"\nFailed to read data sources file: {path}\n{e}\n")
        print("Using OpenBB defaults.")
        return read_default_sources()
