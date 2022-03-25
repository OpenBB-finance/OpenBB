import pytest

from bots.economy.grains import grains_command


@pytest.mark.vcr
def test_grains_command(mocker, recorder):
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = grains_command()

    recorder.capture(value)
