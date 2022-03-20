import pytest

from bots.economy.usbonds import usbonds_command


@pytest.mark.vcr
def test_usbonds_command(mocker, recorder):
    mocker.patch(target="bots.economy.usbonds.save_image", return_value=None)
    value = usbonds_command()

    recorder.capture(value)
