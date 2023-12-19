from pathlib import Path

import pytest

from openbb_terminal import loggers
from openbb_terminal.core.log.generation.settings import (
    AppSettings,
    AWSSettings,
    LogSettings,
    Settings,
)

settings = Settings(
    app_settings=AppSettings(
        commit_hash="MOCK_COMMIT_HASH",
        name="MOCK_COMMIT_HASH",
        identifier="MOCK_COMMIT_HASH",
        session_id="MOCK_SESSION_ID",
        user_id="MOCK_USER_ID",
    ),
    aws_settings=AWSSettings(
        aws_access_key_id="MOCK_AWS_ACCESS_KEY_ID",
        aws_secret_access_key="MOCK_AWS",  # pragma: allowlist secret # noqa: S106
    ),
    log_settings=LogSettings(
        directory=Path("."),
        frequency="H",
        handler_list=["file"],
        rolling_clock=False,
        verbosity=20,
    ),
)


def throw_os_error():
    raise OSError("This is a test error")


def throw_os_error_30():
    e = OSError()
    e.errno = 30
    raise e


def throw_generic():
    raise Exception("This is a test error")


@pytest.mark.parametrize(
    "to_mock", [None, throw_os_error, throw_os_error_30, throw_generic]
)
def test_get_app_id(to_mock, mocker):
    if to_mock:
        mocker.patch("openbb_terminal.loggers.get_log_dir", to_mock)
        with pytest.raises(Exception):
            value = loggers.get_app_id()
    else:
        value = loggers.get_app_id()
        assert value


@pytest.mark.parametrize("git", [True, False])
def test_get_commit_hash(mocker, git):
    mocker.patch("openbb_terminal.loggers.WITH_GIT", git)
    value = loggers.get_commit_hash()
    assert value


def test_get_commit_hash_obff(mocker):
    class MockSystem:  # pylint: disable=too-few-public-methods
        def __init__(self):
            self.LOGGING_COMMIT_HASH = "MOCK_COMMIT_HASH"

    mocker.patch(
        "openbb_terminal.loggers.get_current_system",
        MockSystem,
    )
    value = loggers.get_commit_hash()
    assert value


@pytest.mark.skip(reason="Change the state of the logger.")
def test_add_stdout_handler():
    loggers.add_stdout_handler(settings)


@pytest.mark.skip(reason="Change the state of the logger.")
def test_add_stderr_handler():
    loggers.add_stderr_handler(settings)


@pytest.mark.skip(reason="Change the state of the logger.")
def test_add_nopp_handler():
    loggers.add_noop_handler(settings)


@pytest.mark.skip(reason="Change the state of the logger + lead to file generation.")
def test_add_file_handler():
    loggers.add_file_handler(settings)


@pytest.mark.skip(reason="Change the state of the logger.")
def test_setup_handlers():
    loggers.setup_handlers(settings)


@pytest.mark.skip(reason="Change the state of the logger.")
def test_setup_logging(mocker):
    mocker.patch("openbb_terminal.loggers.setup_handlers")
    loggers.setup_logging(settings)
