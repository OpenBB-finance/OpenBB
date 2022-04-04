import pytest

try:
    from bots.stocks.due_diligence.arktrades import arktrades_command
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


@pytest.mark.skip
@pytest.mark.vcr
@pytest.mark.bots
def test_arktrades_command(recorder):
    value = arktrades_command("AAPL")
    value["view"] = str(type(value["view"]))
    value["embed"] = str(type(value["embed"]))
    value["choices"] = str(type(value["choices"]))
    value["embeds_img"] = str(type(value["embeds_img"]))
    value["images_list"] = str(type(value["images_list"]))

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
def test_arktrades_command_invalid():
    with pytest.raises(Exception):
        arktrades_command("")
