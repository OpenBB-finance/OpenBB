import pytest

try:
    from bots.stocks.technical_analysis.cg import cg_command
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
        ("2022-01-01", "2022-04-01"),
    ],
)
def test_cg_command(recorder, start, end):
    value = cg_command("TSLA", start=start, end=end)
    value["imagefile"] = value["imagefile"][-4:]

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
@pytest.mark.parametrize("ticker", ["", "ZZZZ"])
def test_cg_invalid(ticker):
    with pytest.raises(Exception):
        cg_command(ticker)
