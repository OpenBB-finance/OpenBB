import pytest

try:
    from bots.stocks.disc.ford import ford_command
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


@pytest.mark.bots
@pytest.mark.vcr
def test_ford_command(recorder):
    value = ford_command()
    value["view"] = str(type(value["view"]))
    value["embed"] = str(type(value["embed"]))
    value["choices"] = str(type(value["choices"]))
    value["embeds_img"] = str(type(value["embeds_img"]))
    value["images_list"] = str(type(value["images_list"]))

    recorder.capture(value)
