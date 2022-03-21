import pytest

from bots.economy.grains import grains_command


@pytest.mark.vcr
def test_grains_command(mocker, recorder):
    mocker.patch(target="bots.economy.grains.imps.save_image", return_value=None)
    value = grains_command()

    recorder.capture(value)
