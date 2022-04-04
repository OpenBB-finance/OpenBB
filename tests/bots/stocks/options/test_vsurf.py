import pytest

try:
    from bots.stocks.options.vsurf import vsurf_command
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
@pytest.mark.parametrize("z", ["IV", "OI", "LP"])
def test_vsurf(recorder, z):
    value = vsurf_command("TSLA", z)
    value["imagefile"] = str(type(value["imagefile"]))

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
@pytest.mark.parametrize("ticker", [None, "", "ZZZZ"])
def test_vsurf_invalid(ticker):
    with pytest.raises(Exception):
        vsurf_command(ticker)
