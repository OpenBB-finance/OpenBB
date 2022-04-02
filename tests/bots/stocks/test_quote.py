import pytest

try:
    from bots.stocks.quote import quote_command
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


@pytest.mark.bots
@pytest.mark.vcr
def test_quote_command(recorder):
    value = quote_command("TSLA")
    value["imagefile"] = value["imagefile"][-4:]

    recorder.capture(value)


@pytest.mark.bots
@pytest.mark.vcr
def test_quote_command_none():
    with pytest.raises(Exception):
        quote_command(None)
