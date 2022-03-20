import pytest

from bots.etf.holdings import holdings_command


@pytest.mark.vcr
def test_holdings_command(mocker, recorder):
    mocker.patch(target="bots.etf.holdings.helpers.save_image", return_value="1")
    value = holdings_command("VDE")

    recorder.capture(value)
