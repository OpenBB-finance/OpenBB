import pytest

from bots.economy.glbonds import glbonds_command


@pytest.mark.bots
@pytest.mark.vcr
def test_glbonds_command(mocker, recorder):
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = glbonds_command()

    recorder.capture(value)
