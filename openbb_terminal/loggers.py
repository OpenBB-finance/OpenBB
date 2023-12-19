"""Logging Configuration"""
__docformat__ = "numpy"

# IMPORTATION STANDARD
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
from openbb_terminal.core.log.generation.settings_logger import get_startup
from openbb_terminal.core.log.generation.user_logger import (
    NO_USER_PLACEHOLDER,
    get_current_user,
    get_user_uuid,
)
from openbb_terminal.core.session.current_system import (
    get_current_system,
    set_system_variable,
)
from openbb_terminal.helper_funcs import request
from openbb_terminal.rich_config import console

logger = logging.getLogger(__name__)
logging_verbosity = get_current_system().LOGGING_VERBOSITY

logging.getLogger("requests").setLevel(logging_verbosity)
logging.getLogger("urllib3").setLevel(logging_verbosity)


def get_app_id() -> str:
    """UUID of the current installation."""

    try:
        app_id = get_log_dir().stem
    except OSError as e:
        if e.errno == 30:
            console.print("Please move the application into a writable location.")
            console.print(
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

    logging_commit_hash = get_current_system().LOGGING_COMMIT_HASH
    if use_env and logging_commit_hash != "REPLACE_ME":
        return logging_commit_hash

    git_dir = Path(__file__).parent.parent.joinpath(".git")

    if WITH_GIT and git_dir.is_dir():
        repo = git.Repo(path=git_dir)
        sha = repo.head.object.hexsha
        short_sha = repo.git.rev_parse(sha, short=8)
        commit_hash = f"sha:{short_sha}"
    else:
        commit_hash = "unknown-commit"

    return commit_hash


def get_branch() -> str:
    def get_branch_commit_hash(branch: str) -> str:
        response = request(
            url=f"https://api.github.com/repos/openbb-finance/openbbterminal/branches/{branch}"
        )
        return "sha:" + response.json()["commit"]["sha"][:8]

    current_commit_hash = get_commit_hash()

    for branch in ["main", "develop"]:
        try:
            if get_branch_commit_hash(branch) == current_commit_hash:
                return branch
        except Exception:  # noqa: S110
            pass

    git_dir = Path(__file__).parent.parent.joinpath(".git")
    if WITH_GIT and git_dir.is_dir():
        try:
            repo = git.Repo(path=git_dir)
            branch = repo.active_branch.name
            return branch
        except Exception:  # noqa: S110
            pass

    return "unknown-branch"


class PosthogHandler(logging.Handler):
    """Posthog Handler"""

    def __init__(self, settings: Settings):
        super().__init__()
        self.settings = settings
        self.app_settings = settings.app_settings
        self.logged_in = False
        self.disabled = openbb_posthog.feature_enabled(
            "disable_analytics",
            self.app_settings.identifier,
            send_feature_flag_events=False,
        )

    def emit(self, record: logging.LogRecord):
        if self.disabled or "llama_index" in record.pathname:
            return
        try:
            self.send(record=record)
        except Exception:
            self.handleError(record)

    def log_to_dict(self, log_info: str) -> dict:
        """Log to dict"""
        log_regex = r"(STARTUP|CMD|ASKOBB): (.*)"
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
            log_dict = log_dict.get("STARTUP", log_dict)

            log_extra = {**log_extra, **log_dict}
            log_extra.pop("message", None)

        if re.match(r"^(QUEUE|START|END|INPUT:)", log_line) and not log_dict:
            return

        if (
            not self.logged_in
            and get_user_uuid() != NO_USER_PLACEHOLDER
            and get_current_user().profile.remember
        ):
            self.logged_in = True
            openbb_posthog.identify(
                get_user_uuid(),
                {
                    "email": get_current_user().profile.email,
                    "primaryUsage": get_current_user().profile.primary_usage,
                    **get_startup(),
                },
            )
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
            "terminalVersion": get_current_system().VERSION,
            "branch": get_current_system().LOGGING_BRANCH,
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

    # Remove any existing log handlers
    # Notebooks have a root logging handler by default, see https://github.com/ipython/ipython/issues/8282
    root_logger = logging.getLogger()
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    logging.basicConfig(
        level=verbosity,
        format=FormatterWithExceptions.LOGFORMAT,
        datefmt=FormatterWithExceptions.DATEFORMAT,
        handlers=[],
    )

    posthog_active: bool = False
    for handler_type in handler_list:
        if handler_type == "stdout":
            add_stdout_handler(settings=settings)
        elif handler_type == "stderr":
            add_stderr_handler(settings=settings)
        elif handler_type == "noop":
            add_noop_handler(settings=settings)
        elif handler_type == "file":
            add_file_handler(settings=settings)
        elif handler_type == "posthog":
            posthog_active = True
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
        posthog_active
        and not any(
            [get_current_system().TEST_MODE, get_current_system().LOGGING_SUPPRESS]
        )
        and get_current_system().LOG_COLLECT
    ):
        add_posthog_handler(settings=settings)


def setup_logging(
    app_name: Optional[str] = None,
    frequency: Optional[str] = None,
    verbosity: Optional[int] = None,
) -> None:
    """Setup Logging"""
    current_system = get_current_system()

    # AppSettings
    commit_hash = get_commit_hash()
    name = app_name or current_system.LOGGING_APP_NAME
    identifier = get_app_id()
    session_id = get_session_id()
    user_id = get_user_uuid()
    branch = get_branch()

    set_system_variable("LOGGING_APP_ID", identifier)
    set_system_variable("LOGGING_COMMIT_HASH", commit_hash)
    set_system_variable("LOGGING_BRANCH", branch)

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
