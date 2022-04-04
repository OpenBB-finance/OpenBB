import pytest

try:
    from bots.stocks.options.hist import hist_command
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
@pytest.mark.parametrize("opt_type", ["Puts", "Calls"])
def test_hist_command(recorder, opt_type):
    value = hist_command("TSLA", "2022-04-08", strike=1000.00, opt_type=opt_type)
    value["imagefile"] = str(type(value["imagefile"]))

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
@pytest.mark.parametrize("ticker", ["", "ZZZZ"])
def test_hist_command_invalid(ticker):
    with pytest.raises(Exception):
        hist_command(ticker, "2020-04-08")
