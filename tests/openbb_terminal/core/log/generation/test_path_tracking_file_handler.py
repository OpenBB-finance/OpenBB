import random
from datetime import datetime
from pathlib import Path

import pytest

from openbb_terminal.core.log.generation.path_tracking_file_handler import (
    PathTrackingFileHandler,
)

randint = random.randint(0, 999999999)  # noqa: S311


def return_list(**_):
    return [Path("."), Path(".")]


def test_build_log_file_path(settings):
    value = PathTrackingFileHandler.build_log_file_path(settings)
    assert value


@pytest.mark.parametrize("start", [True, False])
def test_build_log_sender(start, settings):
    value = PathTrackingFileHandler.build_log_sender(settings, start)
    assert value


def test_clean_expired_files():
    PathTrackingFileHandler.clean_expired_files(datetime.now().timestamp())


@pytest.mark.parametrize("start, freq", [(True, "H"), (False, "M")])
def test_build_rolling_clock(start, freq, mocker, settings):
    mocker.patch(
        "openbb_terminal.core.log.generation.path_tracking_file_handler.LoggingClock"
    )
    handler = PathTrackingFileHandler(settings)
    value = PathTrackingFileHandler.build_rolling_clock(handler.doRollover, freq, start)
    assert value


def test_build_rolling_clock_error(settings):
    handler = PathTrackingFileHandler(settings)
    with pytest.raises(AttributeError):
        PathTrackingFileHandler.build_rolling_clock(handler.doRollover, "T", True)


def test_send_expired_files(mocker, settings):
    handler = PathTrackingFileHandler(settings)
    mocker.patch(
        "openbb_terminal.core.log.generation.path_tracking_file_handler.get_expired_file_list",
        return_list,
    )
    handler.send_expired_files(datetime.now().timestamp())


def test_log_sender():
    value = PathTrackingFileHandler.log_sender
    assert value


def test_rolling_clock():
    value = PathTrackingFileHandler.rolling_clock
    assert value


def test_settings():
    value = PathTrackingFileHandler.settings
    assert value


def test_doRollover(settings):
    handler = PathTrackingFileHandler(settings)
    handler.doRollover()


def throw_error():
    raise Exception("Bad!")


def test_close(settings):
    handler = PathTrackingFileHandler(settings)
    handler.close()
