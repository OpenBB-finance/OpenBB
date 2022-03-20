import pytest

from bots.economy.currencies import currencies_command


@pytest.mark.vcr
def test_currencies_command(mocker, recorder):
    mocker.patch(target="bots.economy.currencies.save_image", return_value=None)
    value = currencies_command()

    recorder.capture(value)
