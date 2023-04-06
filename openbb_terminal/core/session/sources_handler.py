import json
import os
from pathlib import Path
from typing import Dict

from openbb_terminal.core.sources.utils import extend, flatten


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
        if path.exists() and os.stat(path).st_size > 0:
            with open(path) as file:
                return flatten(json.load(file))
        return {}
    except Exception as e:
        print(f"\nFailed to read data sources file: {path}\n{e}\n")
        print("Using OpenBB defaults.")
        return {}


def write_sources(sources: Dict, path: Path):
    """Write sources to file.

    Parameters
    ----------
    sources : Dict
        Dictionary with sources
    path : Path
        Path to file
    """
    try:
        with open(path, "w") as f:
            json.dump(extend(sources), f, indent=4)
    except Exception as e:
        print(f"\nFailed to write data sources file: {path}\n{e}\n")
