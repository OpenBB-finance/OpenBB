import pytest

try:
    from bots.etf.holdings import holdings_command
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.bots
@pytest.mark.vcr
def test_holdings_command(mocker, recorder):
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = holdings_command("VDE")

    recorder.capture(value)
