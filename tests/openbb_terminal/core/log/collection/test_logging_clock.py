from datetime import datetime
import pytest
from openbb_terminal.core.log.collection import logging_clock


clock = logging_clock.LoggingClock()
now = datetime.now()


class MockLoop:
    def __init__(self):
        self.count = 0

    def mock_next(self, **_):
        if self.count > 3:
            raise NotImplementedError
        else:
            self.count += 1


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
def test_do_action_every_sharp():
    with pytest.raises(NotImplementedError):
        clock.do_action_every_sharp(MockLoop().mock_next)


def test_run(mocker):
    mocker.patch(
        "openbb_terminal.core.log.collection.logging_clock.LoggingClock.do_action_every_sharp"
    )
    clock.run()


def test_default_action():
    clock.default_action()
