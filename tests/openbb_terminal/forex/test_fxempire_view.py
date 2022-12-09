import pytest
from openbb_terminal.forex.fxempire_view import display_forward_rates
from openbb_terminal.core.exceptions.exceptions import OpenBBUserError


@pytest.fixture(scope="module")
def vcr_config():
    return {"filter_headers": [("User-Agent", None)]}


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_forwards():
    display_forward_rates("USD", "EUR")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_forwards_not_known():
    with pytest.raises(OpenBBUserError):
        display_forward_rates("HUGYDIBWU", "GWUBWYBCY")
