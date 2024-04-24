"""The controllers menu."""

import logging
import sys
from typing import Optional

from prompt_toolkit import PromptSession
from prompt_toolkit.history import FileHistory

from src.config.paths import HIST_FILE_PATH
from src.session.console import console

logger = logging.getLogger(__name__)


try:
    if sys.stdin.isatty():
        session: Optional[PromptSession] = PromptSession(
            history=FileHistory(str(HIST_FILE_PATH))
        )
    else:
        session = None
# pylint: disable=unused-variable
except Exception as e:  # noqa: F841
    logger.exception("%s", type(e).__name__)
    console.print(
        "WARNING: Prompt toolkit is turned on but did not initialize successfully."
        " Falling back to input()..."
    )
    session = None  # type: ignore
