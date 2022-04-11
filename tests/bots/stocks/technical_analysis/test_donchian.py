import pytest

try:
    from bots.stocks.technical_analysis.donchian import donchian_command
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
@pytest.mark.parametrize(
    "start, end",
    [
        ("", ""),
        ("2021-01-01", "2022-01-01"),
    ],
)
def test_donchian_command(recorder, start, end):
    value = donchian_command("TSLA", start=start, end=end)
    value["imagefile"] = value["imagefile"][-4:]

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
@pytest.mark.parametrize("ticker", ["", "ZZZZ"])
def test_donchian_command_invalid(ticker):
    with pytest.raises(Exception):
        donchian_command(ticker)
