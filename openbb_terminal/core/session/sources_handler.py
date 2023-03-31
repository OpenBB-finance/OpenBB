import json
from pathlib import Path


def read_sources(path: str) -> dict:
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
        converted_path = Path(path)
        with open(converted_path) as file:
            sources = json.load(file)
            return sources
    except Exception as e:
        print(f"[Failed to load preferred source from file: " f"{path}")
        print(e)
        return {}
