"""Logging Configuration"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
import logging
import sys
import time
from pathlib import Path
from typing import Optional

# IMPORTATION THIRDPARTY
try:
    import git
except ImportError:
    WITH_GIT = False
else:
    WITH_GIT = True

# IMPORTATION INTERNAL
from openbb_terminal.config_terminal import (
    LOGGING_APP_NAME,
    LOGGING_AWS_ACCESS_KEY_ID,
    LOGGING_AWS_SECRET_ACCESS_KEY,
    LOGGING_COMMIT_HASH,
    LOGGING_FREQUENCY,
    LOGGING_HANDLERS,
    LOGGING_ROLLING_CLOCK,
    LOGGING_VERBOSITY,
)
from openbb_terminal.core.log.generation.directories import get_log_dir
from openbb_terminal.core.log.generation.formatter_with_exceptions import (
    FormatterWithExceptions,
)
from openbb_terminal.core.log.generation.path_tracking_file_handler import (
    PathTrackingFileHandler,
)
from openbb_terminal.core.log.generation.settings import (
    AppSettings,
    AWSSettings,
    LogSettings,
    Settings,
)
from openbb_terminal.core.log.generation.user_logger import get_user_uuid

logging.getLogger("requests").setLevel(LOGGING_VERBOSITY)
logging.getLogger("urllib3").setLevel(LOGGING_VERBOSITY)

logger = logging.getLogger(__name__)

START_TIMESTAMP = int(time.time())


def get_app_id() -> str:
    """UUID of the current installation."""

    try:
        app_id = get_log_dir().stem
    except OSError as e:
        if e.errno == 30:
            print("Please move the application into a writable location.")
            print(
                "Note for macOS users: copy `OpenBB Terminal` folder outside the DMG."
            )
        else:
            raise e
    except Exception as e:
        raise e

    return app_id


def get_commit_hash(use_env=True) -> str:
    """Get Commit Short Hash"""

    if use_env and LOGGING_COMMIT_HASH != "REPLACE_ME":
        return LOGGING_COMMIT_HASH

    git_dir = Path(__file__).parent.parent.joinpath(".git")

    if WITH_GIT and git_dir.is_dir():
        repo = git.Repo(path=git_dir)
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
    handler = PathTrackingFileHandler(settings=settings)
    formatter = FormatterWithExceptions(app_settings=app_settings)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)


def setup_handlers(settings: Settings):
    logging_settings = settings.log_settings
    handler_list = logging_settings.handler_list
    verbosity = logging_settings.verbosity

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

    # AppSettings
    commit_hash = get_commit_hash()
    name = app_name or LOGGING_APP_NAME
    identifier = get_app_id()
    session_id = session_id or str(START_TIMESTAMP)
    user_id = get_user_uuid()

    # AWSSettings
    aws_access_key_id = LOGGING_AWS_ACCESS_KEY_ID
    aws_secret_access_key = LOGGING_AWS_SECRET_ACCESS_KEY

    # LogSettings
    directory = get_log_dir()
    frequency = frequency or LOGGING_FREQUENCY
    handler_list = LOGGING_HANDLERS
    rolling_clock = LOGGING_ROLLING_CLOCK
    verbosity = verbosity or LOGGING_VERBOSITY

    settings = Settings(
        app_settings=AppSettings(
            commit_hash=commit_hash,
            name=name,
            identifier=identifier,
            session_id=session_id,
            user_id=user_id,
        ),
        aws_settings=AWSSettings(
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
        ),
        log_settings=LogSettings(
            directory=directory,
            frequency=frequency,
            handler_list=handler_list,
            rolling_clock=rolling_clock,
            verbosity=verbosity,
        ),
    )

    setup_handlers(settings=settings)
