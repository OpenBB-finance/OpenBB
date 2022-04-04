import pytest

try:
    from bots.stocks.government.contracts import contracts_command
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
@pytest.mark.parametrize("ticker", ["TSLA", "RTX"])
def test_contracts_command(recorder, ticker):
    value = contracts_command(ticker)
    if "imagefile" in value:
        value["imagefile"] = value["imagefile"][-4:]

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
def test_contracts_command_invalid():
    with pytest.raises(Exception):
        contracts_command()
