import pytest

try:
    from bots.stocks.screener.technical import technical_command
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


@pytest.mark.skip
@pytest.mark.vcr
@pytest.mark.bots
def test_technical_command(recorder):
    value = technical_command("wedge_down")
    value["imagefile"] = str(type(value["imagefile"]))

    recorder.capture(value)
