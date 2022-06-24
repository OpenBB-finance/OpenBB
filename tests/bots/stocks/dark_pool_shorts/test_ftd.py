import pytest

try:
    from bots.stocks.dark_pool_shorts.ftd import ftd_command
except ImportError:
    pytest.skip(allow_module_level=True)


@pytest.fixture(scope="module")
def vcr_config():
    return {
        "filter_headers": [("User-Agent", None)],
        "filter_query_parameters": [
            ("period1", "MOCK_PERIOD_1"),
            ("period2", "MOCK_PERIOD_2"),
            ("date", "MOCK_DATE"),
        ],
    }


@pytest.mark.vcr
@pytest.mark.bots
@pytest.mark.parametrize("start, end", [("", ""), ("2021-01-01", "2022-01-01")])
def test_ftd_command(recorder, start, end):
    value = ftd_command("AAPL", start, end)
    value["imagefile"] = value["imagefile"][-4:]

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
def test_ftd_command_invalid():
    with pytest.raises(Exception):
        ftd_command("")
