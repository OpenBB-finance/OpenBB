import pytest

try:
    from bots.economy.indices import indices_command
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.bots
@pytest.mark.vcr
def test_indices_command(mocker, recorder):
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = indices_command()

    recorder.capture(value)
