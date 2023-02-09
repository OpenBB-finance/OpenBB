# IMPORTATION STANDARD
import logging

# IMPORTATION THIRDPARTY
# IMPORTATION INTERNAL
from openbb_terminal.core.log.generation.path_tracking_file_handler import (
    PathTrackingFileHandler,
)


def do_rollover():
    """RollOver the log file."""

    for handler in logging.getLogger().handlers:
        if isinstance(handler, PathTrackingFileHandler):
            try:
                handler.doRollover()
            # IGNORE PermissionError : WINDOWS FILE OPEN
            except PermissionError:
                pass
