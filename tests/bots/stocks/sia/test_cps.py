import pytest

try:
    from bots.stocks.sia.cps import cps_command
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
def test_cps_command(recorder):
    value = cps_command("Germany")
    value["imagefile"] = value["imagefile"][-4:]

    recorder.capture(value)
