from openbb_core.app.logs.utils.expired_files import get_timestamp_from_x_days


def test_get_timestamp_from_x_days():
    result = get_timestamp_from_x_days(0)
    assert isinstance(result, float)
