import pytest
from openbb_terminal.forex.fxempire_model import get_forward_rates


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": [("User-Agent", None)]}


@pytest.mark.vcr
def test_forwards(recorder):
    df = get_forward_rates("USD", "EUR")
    assert df.empty is False
    recorder.capture(df)


@pytest.mark.vcr
def test_forwards_not_known(recorder):
    df = get_forward_rates("GWYG", "GUCHWUHW")
    assert df.empty is True
    recorder.capture(df)
