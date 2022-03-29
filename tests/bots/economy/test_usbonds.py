import pytest

from bots.economy.usbonds import usbonds_command


@pytest.mark.bots
@pytest.mark.vcr
def test_usbonds_command(mocker, recorder):
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = usbonds_command()

    recorder.capture(value)
