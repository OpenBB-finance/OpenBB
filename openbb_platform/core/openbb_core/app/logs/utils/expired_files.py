"""Expired files management utilities."""

import contextlib
from datetime import datetime
from pathlib import Path
from typing import List


def get_timestamp_from_x_days(x: int) -> float:
    """Get the timestamp from x days ago."""
    timestamp_from_x_days = datetime.now().timestamp() - x * 86400
    return timestamp_from_x_days


def get_expired_file_list(directory: Path, before_timestamp: float) -> List[Path]:
    """Get the list of expired files from a directory."""
    expired_files = []
    if directory.is_dir():  # Check if the directory exists and is a directory
        for file in directory.iterdir():
            if file.is_file() and file.lstat().st_mtime < before_timestamp:
                expired_files.append(file)

    return expired_files


def remove_file_list(file_list: List[Path]):
    """Remove a list of files."""
    for file in file_list:
        with contextlib.suppress(PermissionError):
            file.unlink(missing_ok=True)
