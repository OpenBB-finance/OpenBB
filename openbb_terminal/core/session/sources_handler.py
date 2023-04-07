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


def update_hub_sources(default: Dict, hub: Dict) -> Dict:
    """Update hub sources if new source or command path available.

    Parameters
    ----------
    default : Dict
        Dictionary with default sources
    hub : Dict
        Dictionary with hub sources

    Returns
    -------
    Dict
        Updated hub sources
    """
    updated_hub = hub.copy()

    # Add new sources
    for cmd_path, source_list in hub.items():
        if cmd_path in default:
            new_source_list = [v for v in default[cmd_path] if v not in source_list]
            updated_hub[cmd_path].extend(new_source_list)

    # Add new command paths
    for cmd_path, source_list in default.items():
        if cmd_path not in hub:
            updated_hub[cmd_path] = source_list

    return updated_hub
