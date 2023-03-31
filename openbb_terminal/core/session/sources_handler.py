import json
from pathlib import Path


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
            sources = json.load(file)
            return sources
    except Exception as e:
        print(f"Failed to load data sources file: " f"{path}\n{e}\n")
        return {}
