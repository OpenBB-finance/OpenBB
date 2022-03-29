import pytest

from bots.economy.energy import energy_command


@pytest.mark.bots
@pytest.mark.skip
@pytest.mark.vcr
def test_energy_command(mocker, recorder):
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = energy_command()

    recorder.capture(value)
