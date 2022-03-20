import pytest

from bots.economy.softs import softs_command


@pytest.mark.vcr
def test_softs_command(mocker, recorder):
    mocker.patch(target="bots.economy.softs.save_image", return_value=None)
    value = softs_command()

    recorder.capture(value)
