import pytest

try:
    from bots.stocks.government.lobbying import lobbying_command
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
@pytest.mark.parametrize("ticker", ["TSLA", "RTX"])
def test_lobbying_command(recorder, ticker):
    value = lobbying_command(ticker)

    recorder.capture(value)
