"""Logging Configuration"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging
import os
import sys
import time
from pathlib import Path
from typing import Optional

# IMPORTATION THIRDPARTY
import git

# IMPORTATION INTERNAL
import gamestonk_terminal.config_terminal as cfg
from gamestonk_terminal.log.collection.log_sender import LOG_SENDER
from gamestonk_terminal.log.collection.path_tracking_file_handler import (
    PathTrackingFileHandler,
)
from gamestonk_terminal.log.generation.formatter_with_exceptions import (
    Application,
    FormatterWithExceptions,
)
from gamestonk_terminal.log.generation.directories import get_log_dir

logging.getLogger("requests").setLevel(cfg.LOGGING_VERBOSITY)
logging.getLogger("urllib3").setLevel(cfg.LOGGING_VERBOSITY)

logger = logging.getLogger(__name__)

START_TIMESTAMP = int(time.time())


def get_app_id() -> str:
    """UUID of the current installation."""

    app_id = get_log_dir().stem

    return app_id


def get_commit_hash() -> str:
    """Get Commit Short Hash"""

    file_path = Path(__file__)
    git_dir = file_path.parent.parent.absolute().joinpath(".git")

    if os.path.isdir(git_dir.absolute()):
        repo = git.Repo(search_parent_directories=True)
        sha = repo.head.object.hexsha
        short_sha = repo.git.rev_parse(sha, short=8)
        commit_hash = f"sha:{short_sha}"
    else:
        commit_hash = "unknown-commit"

    return commit_hash


def setup_logging(
    frequency: Optional[str] = None,
    session_id: Optional[str] = None,
    verbosity: Optional[int] = None,
) -> None:
    """Setup Logging"""

    app_name = cfg.LOGGING_APP_NAME
    commit_hash = get_commit_hash()
    frequency = frequency or cfg.LOGGING_FREQUENCY
    identifier = get_app_id()
    session_id = session_id or START_TIMESTAMP
    verbosity = verbosity or cfg.LOGGING_VERBOSITY
    log_sender = LOG_SENDER
    log_dir = get_log_dir()

    app = Application(
        commit_hash=commit_hash,
        identifier=identifier,
        name=app_name,
        session_id=session_id,
    )

    logging.basicConfig(
        level=verbosity,
        format=FormatterWithExceptions.LOGFORMAT,
        datefmt=FormatterWithExceptions.DATEFORMAT,
        handlers=[],
    )

    for a_handler in cfg.LOGGING_HANDLERS.split(","):
        if a_handler == "stdout":
            handler = logging.StreamHandler(sys.stdout)   # type: ignore
            formatter = FormatterWithExceptions(app=app)
            handler.setFormatter(formatter)
            logging.getLogger().addHandler(handler)
        elif a_handler == "stderr":
            handler = logging.StreamHandler(sys.stderr)   # type: ignore
            formatter = FormatterWithExceptions(app=app)
            handler.setFormatter(formatter)
            logging.getLogger().addHandler(handler)
        elif a_handler == "noop":
            handler = logging.NullHandler()   # type: ignore
            formatter = FormatterWithExceptions(app=app)
            handler.setFormatter(formatter)
            logging.getLogger().addHandler(handler)
        elif a_handler == "file":
            filename = str(log_dir.absolute().joinpath(f"{app_name}_{session_id}"))
            handler = PathTrackingFileHandler(
                filename=filename,
                log_sender=log_sender,
                when=frequency,
            )   # type: ignore
            formatter = FormatterWithExceptions(app=app)
            handler.setFormatter(formatter)
            logging.getLogger().addHandler(handler)
        else:
            logger.debug("Unknown loghandler")

    logger.info("Logging configuration finished")
    logger.info("Logging set to %s", cfg.LOGGING_HANDLERS)
    logger.info("Verbosity set to %s", verbosity)
    logger.info(
        "LOGFORMAT: %s%s",
        FormatterWithExceptions.LOGPREFIXFORMAT.replace("|", "-"),
        FormatterWithExceptions.LOGFORMAT.replace("|", "-"),
    )
