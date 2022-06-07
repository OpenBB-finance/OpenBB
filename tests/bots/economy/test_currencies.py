import pytest

try:
    from bots.economy.currencies import currencies_command
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.bots
@pytest.mark.vcr
def test_currencies_command(mocker, recorder):
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = currencies_command()

    recorder.capture(value)
