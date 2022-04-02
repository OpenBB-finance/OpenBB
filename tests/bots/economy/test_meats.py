import pytest

try:
    from bots.economy.meats import meats_command
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.bots
@pytest.mark.vcr
def test_meats_command(mocker, recorder):
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = meats_command()

    recorder.capture(value)
