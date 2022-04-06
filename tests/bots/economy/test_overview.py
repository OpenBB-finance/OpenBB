import pytest

try:
    from bots.economy.overview import overview_command
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.bots
@pytest.mark.vcr
def test_overview_command(mocker, recorder):
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = overview_command()

    recorder.capture(value)
