import pytest

from bots.economy.metals import metals_command


@pytest.mark.bots
@pytest.mark.vcr
def test_metals_command(mocker, recorder):
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = metals_command()

    recorder.capture(value)
