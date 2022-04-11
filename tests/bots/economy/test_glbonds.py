import pytest

try:
    from bots.economy.glbonds import glbonds_command
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.bots
@pytest.mark.vcr
def test_glbonds_command(mocker, recorder):
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = glbonds_command()

    recorder.capture(value)
