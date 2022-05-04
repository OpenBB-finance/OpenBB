import pytest

try:
    from bots.stocks.due_diligence.supplier import supplier_command
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
def test_supplier_command(recorder):
    value = supplier_command("TSLA")
    value["view"] = str(type(value["view"]))
    value["embed"] = str(type(value["embed"]))
    value["choices"] = str(type(value["choices"]))

    recorder.capture(value)


@pytest.mark.vcr
@pytest.mark.bots
def test_supplier_command_invalid():
    with pytest.raises(Exception):
        supplier_command()
