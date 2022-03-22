import pytest

from bots.etf.whatetf import by_ticker_command


@pytest.mark.skip
@pytest.mark.vcr
def test_by_ticker_command(mocker, recorder):
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = by_ticker_command("TSLA")

    recorder.capture(value)
