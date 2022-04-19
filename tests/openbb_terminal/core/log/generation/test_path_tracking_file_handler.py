import random
from pathlib import Path
from datetime import datetime
import pytest
from openbb_terminal.core.log.generation import path_tracking_file_handler as ptfh

from openbb_terminal.core.log.generation.settings import (
    Settings,
    AppSettings,
    AWSSettings,
    LogSettings,
)


randint = random.randint(0, 999999999)

settings = Settings(
    app_settings=AppSettings(
        commit_hash="MOCK_COMMIT_HASH",
        name="MOCK_COMMIT_HASH",
        identifier="MOCK_COMMIT_HASH",
        session_id=f"MOCK_SESSION_{randint}",
    ),
    aws_settings=AWSSettings(
        aws_access_key_id="MOCK_AWS_ACCESS_KEY_ID",
        aws_secret_access_key="MOCK_AWS",  # pragma: allowlist secret
    ),
    log_settings=LogSettings(
        directory=Path("."),
        frequency="H",
        handler_list="file",
        rolling_clock=False,
        verbosity=20,
    ),
)

handler = ptfh.PathTrackingFileHandler(settings)


def return_list(**_):
    return [Path("."), Path(".")]


def test_build_log_file_path():
    value = handler.build_log_file_path(settings)
    assert value


@pytest.mark.parametrize("start", [True, False])
def test_build_log_sender(start):
    value = handler.build_log_sender(settings, start)
    assert value


def test_clean_expired_files():
    handler.clean_expired_files(datetime.now().timestamp())


@pytest.mark.parametrize("start, freq", [(True, "H"), (False, "M")])
def test_build_rolling_clock(start, freq, mocker):
    mocker.patch(
        "openbb_terminal.core.log.generation.path_tracking_file_handler.LoggingClock"
    )
    value = handler.build_rolling_clock(handler.doRollover, freq, start)
    assert value


def test_build_rolling_clock_error():
    with pytest.raises(AttributeError):
        handler.build_rolling_clock(handler.doRollover, "T", True)


def test_send_expired_files(mocker):
    mocker.patch(
        "openbb_terminal.core.log.generation.path_tracking_file_handler.get_expired_file_list",
        return_list,
    )
    handler.send_expired_files(datetime.now().timestamp())


def test_log_sender():
    value = handler.log_sender
    assert value


def test_rolling_clock():
    value = handler.rolling_clock
    assert value


def test_settings():
    value = handler.settings
    assert value


def test_doRollover():
    handler.doRollover()


def throw_error():
    raise Exception("Bad!")


def test_close():
    handler.close()
