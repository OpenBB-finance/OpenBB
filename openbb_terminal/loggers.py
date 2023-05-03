"""Logging Configuration"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
import atexit
import json
import logging
import re
import sys
import time
import uuid
from pathlib import Path
from platform import platform, python_version
from typing import Any, Dict, Optional

# IMPORTATION THIRDPARTY
try:
    import git
except ImportError:
    WITH_GIT = False
else:
    WITH_GIT = True

# IMPORTATION INTERNAL
from openbb_terminal.base_helpers import openbb_posthog
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
from openbb_terminal.core.log.generation.user_logger import (
    NO_USER_PLACEHOLDER,
    get_user_uuid,
)
from openbb_terminal.core.session.current_system import (
    get_current_system,
    set_current_system,
)

logger = logging.getLogger(__name__)
current_system = get_current_system()

logging.getLogger("requests").setLevel(current_system.LOGGING_VERBOSITY)
logging.getLogger("urllib3").setLevel(current_system.LOGGING_VERBOSITY)


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


def get_session_id() -> str:
    """UUID of the current session."""
    session_id = str(uuid.uuid4()) + "-" + str(int(time.time()))
    return session_id


def get_commit_hash(use_env=True) -> str:
    """Get Commit Short Hash"""

    if use_env and current_system.LOGGING_COMMIT_HASH != "REPLACE_ME":
        return current_system.LOGGING_COMMIT_HASH

    git_dir = Path(__file__).parent.parent.joinpath(".git")

    if WITH_GIT and git_dir.is_dir():
        repo = git.Repo(path=git_dir)
        sha = repo.head.object.hexsha
        short_sha = repo.git.rev_parse(sha, short=8)
        commit_hash = f"sha:{short_sha}"
    else:
        commit_hash = "unknown-commit"

    return commit_hash


class PosthogHandler(logging.Handler):
    """Posthog Handler"""

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.app_settings = settings.app_settings
        self.logged_in = False
        atexit.register(openbb_posthog.shutdown)

    def emit(self, record: logging.LogRecord):
        try:
            self.send(record=record)
        except Exception:
            self.handleError(record)

    def log_to_dict(self, log_info: str) -> dict:
        """Log to dict"""
        log_regex = r"(KEYS|PREFERENCES|SYSTEM|CMD|QUEUE): (.*)"
        log_dict: Dict[str, Any] = {}

        for log in re.findall(log_regex, log_info):
            log_dict[log[0]] = json.loads(log[1])

        sdk_regex = r"({\"INPUT\":.*})"
        if sdk_dict := re.findall(sdk_regex, log_info):
            log_dict["SDK"] = json.loads(sdk_dict[0])

        return log_dict

    def send(self, record: logging.LogRecord):
        """Send log record to Posthog"""

        app_settings = self.app_settings

        level_name = logging.getLevelName(record.levelno)
        log_line = FormatterWithExceptions.filter_log_line(text=record.getMessage())

        log_extra = self.extract_log_extra(record=record)
        log_extra.update(dict(level=level_name, message=log_line))
        event_name = f"log_{level_name.lower()}"

        if log_dict := self.log_to_dict(log_info=log_line):
            event_name = f"log_{list(log_dict.keys())[0].lower()}"

            log_extra = {**log_extra, **log_dict}
            log_extra.pop("message", None)

        if re.match(r"^(START|END|INPUT:)", log_line):
            return

        if not self.logged_in and get_user_uuid() != NO_USER_PLACEHOLDER:
            self.logged_in = True
            openbb_posthog.alias(get_user_uuid(), app_settings.identifier)

        openbb_posthog.capture(
            app_settings.identifier,
            event_name,
            properties=log_extra,
        )

    def extract_log_extra(self, record: logging.LogRecord) -> Dict[str, Any]:
        """Extract log extra from record"""

        log_extra: Dict[str, Any] = {
            "appName": self.app_settings.name,
            "appId": self.app_settings.identifier,
            "sessionId": self.app_settings.session_id,
            "commitHash": self.app_settings.commit_hash,
            "platform": platform(),
            "pythonVersion": python_version(),
            "terminalVersion": current_system.VERSION,
        }

        if get_user_uuid() != NO_USER_PLACEHOLDER:
            log_extra["userId"] = get_user_uuid()

        if hasattr(record, "extra"):
            log_extra = {**log_extra, **record.extra}

        if record.exc_info:
            log_extra["exception"] = {
                "type": str(record.exc_info[0]),
                "value": str(record.exc_info[1]),
                "traceback": self.format(record),
            }

        return log_extra


def add_posthog_handler(settings: Settings):
    app_settings = settings.app_settings
    handler = PosthogHandler(settings=settings)
    formatter = FormatterWithExceptions(app_settings=app_settings)
    handler.setFormatter(formatter)
    logging.getLogger().addHandler(handler)


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

    if (
        not any([current_system.TEST_MODE, current_system.LOGGING_SUPPRESS])
        and current_system.LOG_COLLECT
    ):
        add_posthog_handler(settings=settings)


def setup_logging(
    app_name: Optional[str] = None,
    frequency: Optional[str] = None,
    verbosity: Optional[int] = None,
) -> None:
    """Setup Logging"""

    # AppSettings
    commit_hash = get_commit_hash()
    name = app_name or current_system.LOGGING_APP_NAME
    identifier = get_app_id()
    session_id = get_session_id()
    user_id = get_user_uuid()

    current_system.LOGGING_APP_ID = identifier
    set_current_system(current_system)

    # AWSSettings
    aws_access_key_id = current_system.LOGGING_AWS_ACCESS_KEY_ID
    aws_secret_access_key = current_system.LOGGING_AWS_SECRET_ACCESS_KEY

    # LogSettings
    directory = get_log_dir()
    frequency = frequency or current_system.LOGGING_FREQUENCY
    handler_list = current_system.LOGGING_HANDLERS
    rolling_clock = current_system.LOGGING_ROLLING_CLOCK
    verbosity = verbosity or current_system.LOGGING_VERBOSITY

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
