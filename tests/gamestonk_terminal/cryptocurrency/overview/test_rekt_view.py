import pytest

from gamestonk_terminal.cryptocurrency.overview import rekt_view


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_crypto_hack():
    rekt_view.display_crypto_hacks(10, "Amount [$]", False, "bitmart-rekt", "")


@pytest.mark.vcr
@pytest.mark.record_stdout
def test_get_crypto_hacks():
    rekt_view.display_crypto_hacks(10, "Amount [$]", False, "", "")
