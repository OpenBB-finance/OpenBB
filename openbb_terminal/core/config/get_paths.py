from pathlib import Path
from typing import Dict
from . import paths


def get_folder_paths() -> Dict[str, Path]:
    """
    Returns paths of custom folders defined in paths.py
    """
    folder_paths = {}
    for folder in paths.FOLDERS:
        full_folder = paths.USER_DATA_DIRECTORY / folder
        folder_paths[folder] = full_folder
    return folder_paths
