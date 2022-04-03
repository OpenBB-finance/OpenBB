import pytest

try:
    from bots.stocks.government.toplobbying import toplobbying_command
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
def test_toplobbying_command(recorder):
    value = toplobbying_command()
    value["imagefile"] = str(type(value["imagefile"]))

    recorder.capture(value)
