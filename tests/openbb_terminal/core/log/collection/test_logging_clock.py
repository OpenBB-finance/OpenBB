from datetime import datetime
import pytest
from openbb_terminal.core.log.collection import logging_clock


clock = logging_clock.LoggingClock()
now = datetime.now()


def mock_next(**_):
    raise NotImplementedError


@pytest.mark.parametrize(
    "precision", [logging_clock.Precision.hour, logging_clock.Precision.minute]
)
def test_calculate_next_sharp(precision):
    value = clock.calculate_next_sharp(now, precision)
    assert value


def test_calculate_next_sharp_invalid():
    with pytest.raises(Exception):
        clock.calculate_next_sharp(now, "bad")


# TODO: find a better way to mock the while loop
def test_do_action_every_sharp(mocker):
    mock = mocker.Mock()
    mock.count = 0
    mock.mock_next = mock_next
    with pytest.raises(NotImplementedError):
        clock.do_action_every_sharp(mock.mock_next)


def test_run(mocker):
    mocker.patch(
        "openbb_terminal.core.log.collection.logging_clock.LoggingClock.do_action_every_sharp"
    )
    clock.run()


def test_default_action():
    clock.default_action()
