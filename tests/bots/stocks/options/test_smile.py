import pytest

try:
    from bots.stocks.options.smile import smile_command
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
@pytest.mark.parametrize("min_sp, max_sp", [(None, None), (200.00, 1200.00)])
def test_smile_command(recorder, min_sp, max_sp):
    value = smile_command("TSLA", "2022-04-08", min_sp, max_sp)
    value["imagefile"] = str(type(value["imagefile"]))

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
@pytest.mark.parametrize("ticker", [None, "", "ZZZZ"])
def test_smile_command_invalid(ticker):
    with pytest.raises(Exception):
        smile_command(ticker, "2022-04-08")
