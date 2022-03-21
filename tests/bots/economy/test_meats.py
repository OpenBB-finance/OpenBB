import pytest

from bots.economy.meats import meats_command


@pytest.mark.vcr
def test_meats_command(mocker, recorder):
    mocker.patch(target="bots.economy.meats.imps.save_image", return_value=None)
    value = meats_command()

    recorder.capture(value)
