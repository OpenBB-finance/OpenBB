import pytest
from openbb_terminal.forex.fxempire_model import get_forward_rates
from openbb_terminal.core.exceptions.exceptions import OpenBBUserError


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": [("User-Agent", None)]}


@pytest.mark.vcr
def test_forwards(recorder):
    df = get_forward_rates("USD", "EUR")
    assert df.empty is False
    recorder.capture(df)


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_forwards_not_known():
    with pytest.raises(OpenBBUserError):
        get_forward_rates("GWYG", "GUCHWUHW")
