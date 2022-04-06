import pytest

try:
    from bots.etf.tops import etfs_disc_command
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.mark.bots
@pytest.mark.parametrize("sort", ["active"])
@pytest.mark.vcr
def test_etfs_disc_command(mocker, recorder, sort):
    mocker.patch("bots.helpers.uuid_get", return_value="1")
    value = etfs_disc_command(sort)
    for key, value in value.items():
        key = str(value)
        print(f"{key}: {type(value)}-{str(value)}")
    recorder.capture(value)
