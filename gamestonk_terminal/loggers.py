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
from gamestonk_terminal.log.generation.settings import (
    AppSettings,
    LogSettings,
    Settings,
)
from gamestonk_terminal.log.generation.path_tracking_file_handler import (
    PathTrackingFileHandler,
)
from gamestonk_terminal.log.generation.formatter_with_exceptions import (
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


def add_stdout_handler(settings: Settings):
    app_settings = settings.app_settings
    handler = logging.StreamHandler(sys.stdout)
    formatter = FormatterWithExceptions(app_settings=app_settings)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)


def add_stderr_handler(settings: Settings):
    app_settings = settings.app_settings
    handler = logging.StreamHandler(sys.stderr)
    formatter = FormatterWithExceptions(app_settings=app_settings)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)


def add_noop_handler(settings: Settings):
    app_settings = settings.app_settings
    handler = logging.NullHandler()
    formatter = FormatterWithExceptions(app_settings=app_settings)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)


def add_file_handler(settings: Settings):
    app_settings = settings.app_settings
    handler = PathTrackingFileHandler(settings=settings, rolling_clock=False)
    formatter = FormatterWithExceptions(app_settings=app_settings)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)


def setup_handlers(settings: Settings):
    log_settings = settings.log_settings
    handler_list = log_settings.handler_list
    verbosity = log_settings.verbosity

    logging.basicConfig(
        level=verbosity,
        format=FormatterWithExceptions.LOGFORMAT,
        datefmt=FormatterWithExceptions.DATEFORMAT,
        handlers=[],
    )

    for handler_type in handler_list.split(","):
        if handler_type == "stdout":
            add_stdout_handler(settings=settings)
        elif handler_type == "stderr":
            add_stderr_handler(settings=settings)
        elif handler_type == "noop":
            add_noop_handler(settings=settings)
        elif handler_type == "file":
            add_file_handler(settings=settings)
        else:
            logger.debug("Unknown log handler.")

    logger.info("Logging configuration finished")
    logger.info("Logging set to %s", handler_list)
    logger.info("Verbosity set to %s", verbosity)
    logger.info(
        "LOGFORMAT: %s%s",
        FormatterWithExceptions.LOGPREFIXFORMAT.replace("|", "-"),
        FormatterWithExceptions.LOGFORMAT.replace("|", "-"),
    )


def setup_logging(
    app_name: Optional[str] = None,
    frequency: Optional[str] = None,
    session_id: Optional[str] = None,
    verbosity: Optional[int] = None,
) -> None:
    """Setup Logging"""

    name = app_name or cfg.LOGGING_APP_NAME
    commit_hash = get_commit_hash()
    identifier = get_app_id()
    session_id = session_id or str(START_TIMESTAMP)

    frequency = frequency or cfg.LOGGING_FREQUENCY
    verbosity = verbosity or cfg.LOGGING_VERBOSITY
    directory = get_log_dir()
    handler_list = cfg.LOGGING_HANDLERS

    settings = Settings(
        app_settings=AppSettings(
            name=name,
            commit_hash=commit_hash,
            identifier=identifier,
            session_id=session_id,
        ),
        log_settings=LogSettings(
            directory=directory,
            frequency=frequency,
            handler_list=handler_list,
            verbosity=verbosity,
        ),
    )

    setup_handlers(settings=settings)
