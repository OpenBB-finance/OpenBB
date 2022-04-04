import pytest

try:
    from bots.stocks.options.oi import oi_command
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
@pytest.mark.parametrize("min_sp, max_sp", [(None, None), (10.00, 1000.00)])
def test_oi_command(recorder, min_sp, max_sp):
    value = oi_command("TSLA", "2022-04-08", min_sp, max_sp)
    value["imagefile"] = str(type(value["imagefile"]))

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
@pytest.mark.parametrize("ticker", ["", "ZZZZ"])
def test_oi_command_invalid(ticker):
    with pytest.raises(Exception):
        oi_command(ticker, "2022-04-08")
