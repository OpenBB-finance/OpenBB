import pytest

try:
    from bots.stocks.government.histcont import histcont_command
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
def test_histcont_command(recorder):
    value = histcont_command("TSLA")
    value["imagefile"] = str(type(value["imagefile"]))

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
def test_histcont_command_invalid():
    with pytest.raises(Exception):
        histcont_command()
