import pytest

from bots.economy.energy import energy_command


@pytest.mark.vcr
def test_energy_command(mocker, recorder):
    mocker.patch(target="bots.economy.energy.imps.save_image", return_value=None)
    value = energy_command()

    recorder.capture(value)
