import pytest

try:
    from bots.stocks.technical_analysis.stoch import stoch_command
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
    "start, end, extended, heikin, news",
    [
        ("", "", False, False, False),
        ("2022-01-01", "2022-04-01", True, True, True),
    ],
)
def test_stoch_command(recorder, start, end, extended, heikin, news):
    value = stoch_command(
        "TSLA",
        start=start,
        end=end,
        extended_hours=extended,
        heikin_candles=heikin,
        news=news,
    )
    value["imagefile"] = value["imagefile"][-4:]

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
@pytest.mark.parametrize("ticker", ["", "ZZZZ"])
def test_stoch_invalid(ticker):
    with pytest.raises(Exception):
        stoch_command(ticker)
