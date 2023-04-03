import json
import os
from pathlib import Path
from typing import Dict

from openbb_terminal.core.sources.utils import generate_sources_dict


# instead of assigning to SourcesModel we should jus update the sources_dict
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
        if os.stat(path).st_size == 0:
            return {}
        with open(path) as file:
            return json.load(file)
    except Exception as e:
        print(f"\nFailed to read data sources file: {path}\n{e}\n")
        print("Using OpenBB defaults.")
        return {}


def update_sources(cmd, defaults, path: Path):
    try:
        if os.stat(path).st_size == 0:
            sources = {}
        with open(path) as f:
            sources = json.load(f)

        sources.update(generate_sources_dict({cmd: defaults}))
        with open(path, "w") as f:
            json.dump(sources, f, indent=4)
    except Exception as e:
        print(f"\nFailed to write data sources file: {path}\n{e}\n")
