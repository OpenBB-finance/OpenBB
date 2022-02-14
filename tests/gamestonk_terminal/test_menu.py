from contextlib import contextmanager
import pytest
from terminal import main


@contextmanager
def no_suppress():
    yield


@pytest.mark.vcr(record_mode="none")
@pytest.mark.record_stdout
@pytest.mark.parametrize(
    "debug, test, filtert, path",
    [
        (True, False, None, None),
        (False, False, None, ["scripts/test_alt_covid.gst"]),
        (False, True, "alt_covid", ["scripts/"]),
    ],
)
def test_menu(mocker, debug, test, filtert, path):

    mocker.patch(
        target="gamestonk_terminal.feature_flags.USE_DATETIME",
        new=False,
    )
    mocker.patch(target="terminal.suppress_stdout", side_effect=no_suppress)
    main(debug, test, filtert, path)
