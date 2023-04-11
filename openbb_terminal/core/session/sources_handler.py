import json
import os
from pathlib import Path
from typing import Dict

from openbb_terminal.core.models.sources_model import SourcesModel, get_allowed_sources
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
        print("Falling back to OpenBB default sources.")
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


def merge_sources(incoming: Dict, allowed: Dict):
    """Update sources dict if command and sources allowed.

    Parameters
    ----------
    incoming : Dict
        Dictionary with incoming sources
    allowed : Dict
        Dictionary with allowed sources

    Returns
    -------
    Dict
        Updated sources
    """
    choices = allowed.copy()

    for cmd_path, incoming_sources in incoming.items():
        if cmd_path in allowed:
            allowed_sources = allowed[cmd_path]
            filtered_incoming = [s for s in incoming_sources if s in allowed_sources]
            remaining = [s for s in allowed_sources if s not in incoming_sources]
            choices[cmd_path] = filtered_incoming + remaining
    return choices


def load_file_to_model(path: Path) -> SourcesModel:
    """Load sources model from file.

    Parameters
    ----------
    path : Path
        Path to file

    Returns
    -------
    SourcesModel
        Sources model
    """
    choices = merge_sources(incoming=read_sources(path), allowed=get_allowed_sources())
    return SourcesModel(choices=choices)  # type: ignore


def get_updated_hub_sources(configs: Dict) -> Dict:
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
    if configs:
        incoming = configs.get("features_sources", {}) or {}
        if incoming:
            return merge_sources(incoming=incoming, allowed=get_allowed_sources())
        return {}
    return {}
