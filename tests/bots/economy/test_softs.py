import pytest

try:
    from bots.economy.softs import softs_command
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.bots
@pytest.mark.vcr
def test_softs_command(mocker, recorder):
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = softs_command()

    recorder.capture(value)
