import pytest

try:
    from bots.stocks.options.overview import (
        options_data,
        run,
        overview_command,
    )
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
def test_options_data(recorder):
    value = options_data("TSLA", expiry="2022-04-08")
    new_value = [str(type(x)) for x in value]

    recorder.capture(new_value)


@pytest.mark.vcr
@pytest.mark.bots
def test_run(recorder):
    value = run("TSLA", expiry="2022-04-08")
    new_value = [str(type(x)) for x in value]

    recorder.capture(new_value)


@pytest.mark.vcr
@pytest.mark.bots
def test_overview_command(recorder):
    value = overview_command("TSLA", expiry="2022-04-08")
    value["view"] = str(type(value["view"]))
    value["embed"] = str(type(value["embed"]))
    value["choices"] = str(type(value["choices"]))
    value["embeds_img"] = str(type(value["embeds_img"]))
    value["images_list"] = str(type(value["images_list"]))

    recorder.capture(value)
