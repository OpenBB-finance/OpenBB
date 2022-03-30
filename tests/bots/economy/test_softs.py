import pytest

from bots.economy.softs import softs_command


@pytest.mark.bots
@pytest.mark.vcr
def test_softs_command(mocker, recorder):
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = softs_command()

    recorder.capture(value)
