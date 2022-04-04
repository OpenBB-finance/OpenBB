import pytest

try:
    from bots.stocks.options.vol import vol_command
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
@pytest.mark.parametrize("min_sp, max_sp", [(None, None), (500.00, 1500.00)])
def test_vol_command(recorder, min_sp, max_sp):
    value = vol_command("TSLA", "2022-04-08", min_sp, max_sp)
    value["imagefile"] = str(type(value["imagefile"]))

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
@pytest.mark.parametrize("ticker", [None, "", "ZZZZ"])
def test_vol_command_invalid(ticker):
    with pytest.raises(Exception):
        vol_command(ticker, "2022-04-08")
