import pytest

try:
    from bots.stocks.options.opt_chain import chain_command
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
    "opt_type, min_sp, max_sp", [("Calls", None, None), ("Puts", 100.0, 1000.0)]
)
def test_chain_command(recorder, opt_type, min_sp, max_sp):
    value = chain_command("TSLA", "2022-04-08", opt_type, min_sp, max_sp)
    value["view"] = str(type(value["view"]))
    value["embed"] = str(type(value["embed"]))
    value["choices"] = str(type(value["choices"]))
    value["embeds_img"] = str(type(value["embeds_img"]))
    value["images_list"] = str(type(value["images_list"]))

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
@pytest.mark.parametrize("ticker", ["", "zzzz"])
def test_chain_command_invalid(ticker):
    with pytest.raises(Exception):
        chain_command(ticker)
