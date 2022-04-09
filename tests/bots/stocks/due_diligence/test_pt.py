import pytest

try:
    from bots.stocks.due_diligence.pt import pt_command
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
def test_pt(recorder):
    value = pt_command("TSLA")
    value["imagefile"] = value["imagefile"][-4:]

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
def test_pt_invalid():
    with pytest.raises(Exception):
        pt_command()
